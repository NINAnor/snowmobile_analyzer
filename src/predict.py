import argparse
import datetime
import os
import numpy as np
import csv
import sys

import torch
from torch.utils.data import DataLoader

from utils.utils import AudioList
from utils.audio_signal import AudioSignal

import traceback
import logging

# Open the config file
import yaml
from yaml import FullLoader
with open("../CONFIG.yaml") as f:
    cfg = yaml.load(f, Loader=FullLoader)

logging.basicConfig(filename='../logs/logfile.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def initModel(model_path, device):
    model = torch.load(model_path, map_location=torch.device(device))
    model.eval()
    return model

def compute_hr(array):

    signal = AudioSignal(samples=array, fs=44100)

    signal.apply_butterworth_filter(order=18, Wn=np.asarray([1, 600]) / (signal.fs / 2))
    signal_hr = signal.harmonic_ratio(
        win_length=int(1 * signal.fs),
        hop_length=int(0.1 * signal.fs),
        window="hamming",
    )
    hr = np.mean(signal_hr)

    return hr

def predict(testLoader, model, device, threshold=0.99):

    proba_list = []
    hr_list = []

    for array in testLoader:

        # Compute confidence for the DL model
        if device == "cpu":
            tensor = torch.tensor(array)
        else:
            tensor = array

        tensor = tensor.to(device)
        output = model(tensor)
        output = np.exp(output.cpu().detach().numpy())
        proba_list.append(output[0])

        # Compute HR if confidence is more than a threshold
        max_value = output[0].max()
        if max_value >= threshold:
            hr = compute_hr(np.array(array))
            hr_list.append(hr)
        else:
            hr_list.append(0)

    return proba_list, hr_list


def get_outname(input, out_path):

    # Get a name for the output // if there are multiple "." in the list
    # only remove the extension
    filename = input.split("/")[-1].split(".")
    if len(filename) > 2:
        filename = ".".join(filename[0:-1])
    else:
        filename = input.split("/")[-1].split(".")[0]

    # Make folder if it doesn't exist
    outpath = os.sep.join([out_path, os.path.dirname(input)])
    if not os.path.exists(outpath):
        os.makedirs(outpath, exist_ok=True)

    file_path = os.path.join(outpath, filename + ".csv")

    return file_path

def write_results(prob_audioclip_array, hr_array, outname, min_hr, min_conf):

    # Store the array result in a CSV friendly format
    rows_for_csv = []
    idx_begin = 0

    for item_audioclip, item_hr in zip(prob_audioclip_array, hr_array):

        # Get the properties of the detection (start, end, label and confidence)
        idx_end = idx_begin + 3
        conf = np.array(item_audioclip)
        label = np.argmax(conf, axis=0)
        max_value = conf.max()
        hr = np.array(item_hr)

        # If the label is not "soundscape" then write the row:
        if label != 0 and hr > min_hr and max_value > min_conf:
            item_properties = [idx_begin, idx_end, label, max_value, hr]
            rows_for_csv.append(item_properties)

        # Update the start time of the detection
        idx_begin = idx_end

        # Write only if there are some detections respecting our conditions
        if len(rows_for_csv) > 0:
            with open(outname, "w") as file:

                writer = csv.writer(file)
                header = ["start_detection", "end_detection", "label", "confidence", "hr"]

                writer.writerow(header)
                writer.writerows(rows_for_csv)
        else:
            file_analyzed = os.path.basename(outname)
            message = f"No detection has been made for {file_analyzed}"
            print(message)
            logging.info(message)


def analyzeFile(
    file_path, model, device, num_workers, min_hr, min_conf, batch_size=1
):
    # Start time
    start_time = datetime.datetime.now()

    # Create a result folder
    input_dir = os.path.dirname(file_path)
    result_folder = os.path.join(input_dir, "SNOWMOBILE_RESULTS")

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    # Check if the output already exists
    outname = file_path.split("/")[-1].split(".")[0] + "_ANALYZED.csv"
    outpath = os.path.join(result_folder, outname)

    if os.path.exists(outname):
        print("File {} already exists".format(outname))
    else:
        # Run the predictions
        list_preds = AudioList().get_processed_list(file_path)
        predLoader = DataLoader(
            list_preds, batch_size=batch_size, num_workers=num_workers, pin_memory=False
        )

        pred_audioclip_array, pred_hr_array = predict(predLoader, model, device)

        write_results(pred_audioclip_array, pred_hr_array, outpath, min_hr, min_conf)

        # Give the time it took to analyze file
        delta_time = (datetime.datetime.now() - start_time).total_seconds()
        message = "Finished {} in {:.2f} seconds".format(file_path, delta_time)
        print(message, flush=True)
        logging.info(message)

def main(filename, cfg):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = initModel(model_path=cfg["path_snowmobile_model"], device=device)

    analyzeFile(filename,
                model, 
                device, 
                num_workers=cfg["NUM_WORKERS"],
                min_hr=cfg["MIN_HR"],
                min_conf=cfg["MIN_CONF"],
                batch_size=cfg["BATCH_SIZE"])


if __name__ == "__main__":

    filename = sys.argv[1]

    # Analyze file
    print("Analysing {}".format(filename))
    try:
        main(filename, cfg)
    except Exception as e:
        print(f"File {filename} failed to be analyzed")
        logging.error(f"File {filename} failed to be analyzed: {str(e)}")
        logging.error(traceback.format_exc())
