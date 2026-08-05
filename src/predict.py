import csv
import datetime
import logging
import os
import sys
import traceback

import numpy as np
import torch

# Open the config file
import yaml
from torch.utils.data import DataLoader
from yaml import FullLoader

from utils.audio_signal import AudioSignal
from utils.utils import AudioList

with open("./CONFIG.yaml") as f:
    cfg = yaml.load(f, Loader=FullLoader)

logging.basicConfig(
    filename="./logs/logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def initModel(model_path, device):
    model = torch.load(
        model_path, map_location=torch.device(device), weights_only=False
    )
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


def predict(testLoader, model, device):
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

        # Compute HR if label=snowmobile
        label = np.argmax(output[0], axis=0)

        if label == 1:
            hr = compute_hr(np.array(array))
            hr_list.append(hr)
        else:
            hr_list.append(0)

    return proba_list, hr_list


def write_results(prob_audioclip_array, hr_array, outname):
    # Store the array result in a CSV friendly format
    rows_for_csv = []
    idx_begin = 0

    for item_audioclip, item_hr in zip(prob_audioclip_array, hr_array, strict=False):
        # Get the properties of the detection (start, end, label and confidence)
        idx_end = idx_begin + 3
        conf = np.array(item_audioclip)
        label = np.argmax(conf, axis=0)
        max_value = conf.max()
        hr = np.array(item_hr)

        # Write everything in the row
        item_properties = [idx_begin, idx_end, label, max_value, hr]
        rows_for_csv.append(item_properties)

        # Update the start time of the detection
        idx_begin = idx_end

        # Write only if there are some detections respecting our conditions
        if len(rows_for_csv) > 0:
            with open(outname, "w") as file:
                writer = csv.writer(file)
                header = [
                    "start_detection",
                    "end_detection",
                    "label",
                    "confidence",
                    "hr",
                ]

                writer.writerow(header)
                writer.writerows(rows_for_csv)
        else:
            file_analyzed = os.path.basename(outname)
            message = f"No detection has been made for {file_analyzed}"
            print(message)
            logging.info(message)


def analyzeFile(file_path, model, device, num_workers, batch_size=1):
    # Start time
    start_time = datetime.datetime.now()

    # Create a result folder
    input_dir = os.path.dirname(file_path)
    result_folder = os.path.join(input_dir, "SNOWMOBILE_RESULTS")

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    # Check if the output already exists
    outname = file_path.split("/")[-1] + "_ANALYZED.csv"
    outpath = os.path.join(result_folder, outname)

    # Run the predictions
    list_preds = AudioList().get_processed_list(file_path)
    predLoader = DataLoader(
        list_preds, batch_size=batch_size, num_workers=num_workers, pin_memory=False
    )

    pred_audioclip_array, pred_hr_array = predict(predLoader, model, device)

    write_results(pred_audioclip_array, pred_hr_array, outpath)

    # Give the time it took to analyze file
    delta_time = (datetime.datetime.now() - start_time).total_seconds()
    message = f"Finished {file_path} in {delta_time:.2f} seconds"
    print(message, flush=True)
    logging.info(message)


def main(filename, cfg):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = initModel(model_path=cfg["path_snowmobile_model"], device=device)

    analyzeFile(
        filename,
        model,
        device,
        num_workers=cfg.get("NUM_WORKERS", 0),
        batch_size=cfg.get("BATCH_SIZE", 1),
    )


if __name__ == "__main__":
    filename = sys.argv[1]

    # Analyze file
    print(f"Analysing {filename}")
    try:
        main(filename, cfg)
    except Exception as e:
        print(f"File {filename} failed to be analyzed")
        logging.error(f"File {filename} failed to be analyzed: {str(e)}")
        logging.error(traceback.format_exc())
