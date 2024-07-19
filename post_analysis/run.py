import os
import glob
import numpy as np
import csv

import torch
from torch.utils.data import DataLoader

from src.utils.utils import AudioList
from src.utils.audio_signal import AudioSignal

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

if __name__ == "__main__":

    mpath = "audioclip/assets/snowmobile_model.pth"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = torch.load(mpath, map_location=device)
    m.eval()

    file_paths = "/home/benjamin.cretois/data/proj_snowmobile/bugg_RPiID-10000000/**/**/*.mp3" 
    files_to_analyze = glob.glob(file_paths)
    # take only a subset
    files_to_analyze = files_to_analyze[ : 10]

    for file_path in files_to_analyze:
        list_preds = AudioList().get_processed_list(file_path)
        predLoader = DataLoader(
        list_preds, batch_size=1, num_workers=10, pin_memory=False
        )

        pred_audioclip_array, pred_hr_array = predict(predLoader, m, device)
        print(pred_audioclip_array)