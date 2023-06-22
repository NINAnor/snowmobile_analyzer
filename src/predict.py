import argparse
import datetime
import os
import numpy as np
import csv

import torch
from torch.utils.data import DataLoader

from utils.utils import AudioList
from utils.audio_signal import AudioSignal

def initModel(model_path, device):
    model = torch.load(model_path)
    model.eval()

    return model.to(device)

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

def predict(testLoader, model, device, threshold=0.95):

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

    with open(outname, "w") as file:

        writer = csv.writer(file)
        header = ["start_detection", "end_detection", "label", "confidence", "hr"]

        writer.writerow(header)
        writer.writerows(rows_for_csv)


def analyzeFile(
    file_path, out_path, model, device, num_workers, min_hr, min_conf, batch_size=1
):
    # Start time
    start_time = datetime.datetime.now()

    # Check if the output already exists
    outname = out_path

    if os.path.exists(outname):
        print("File {} already exists".format(outname))
    else:
        # Run the predictions
        list_preds = AudioList().get_processed_list(file_path)
        predLoader = DataLoader(
            list_preds, batch_size=batch_size, num_workers=num_workers, pin_memory=False
        )

        pred_audioclip_array, pred_hr_array = predict(predLoader, model, device)
        write_results(pred_audioclip_array, pred_hr_array, outname, min_hr, min_conf)

        # Give the tim it took to analyze file
        delta_time = (datetime.datetime.now() - start_time).total_seconds()
        print("Finished {} in {:.2f} seconds".format(file_path, delta_time), flush=True)


if __name__ == "__main__":

    # Get the config for doing the predictions
    # FOR TESTING THE PIPELINE WITH ONE FILE
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        help="Path to the file to analyze",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--output",
        help="Result file path",
        default="config_inference.yaml",
        required=False,
        type=str,
    )

    parser.add_argument(
        "--num_workers",
        help="Number of workers for reading in audiofiles",
        default=1,
        required=False,
        type=int,
    )

    parser.add_argument(
        "--min_hr",
        help="Minimum value for harmonic ratio to take detection in",
        default=0.1,
        required=False,
        type=int,
    )

    parser.add_argument(
        "--min_conf",
        help="Minimum value for model confidence to take detection in",
        default=0.95,
        required=False,
        type=int,
    )
    
    cli_args = parser.parse_args()

    # Initiate model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "/app/audioclip/assets/snowmobile_model.pth"

    model = initModel(model_path=model_path, device=device)

    # Analyze file
    print("Analysing {}".format(cli_args.input))
    try:
        analyzeFile(
            cli_args.input,
            cli_args.output,
            model,
            device=device,
            batch_size=1,
            num_workers=cli_args.num_workers,
            min_hr=cli_args.min_hr,
            min_conf=cli_args.min_conf
        )
    except:
        print("File {} failed to be analyzed".format(cli_args.input))
