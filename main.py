
#!/usr/env/bin python3

import argparse
import numpy as np

import torch
from torch.utils.data import DataLoader

from predict import predict
from predict import initModel
from utils.utils import AudioList


def analyseAudioFile(
        audio_file_path, batch_size=1, num_workers=4, min_hr = 0.1, min_conf = 0.95
):
    # Initiate model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "./assets/snowmobile_model.pth"
    model = initModel(model_path=model_path, device=device)

    # Run the predictions
    list_preds = AudioList().get_processed_list(audio_file_path)
    predLoader = DataLoader(list_preds, batch_size=batch_size, num_workers=num_workers, pin_memory=False)
    prob_audioclip_array, hr_array = predict(predLoader, model, device)

    # Set index of the array to 0 (beginning)
    idx_begin = 0

    # List of results
    results = []

    for item_audioclip, item_hr in zip(prob_audioclip_array, hr_array):

        # Get the properties of the detection (start, end, label, confidence and harmonic ratio)
        idx_end = idx_begin + 3
        conf = np.array(item_audioclip)
        label = np.argmax(conf, axis=0)
        confidence = conf.max()
        hr = np.array(item_hr)

        # If the label is not "soundscape" then write the row:
        if label != 0 and hr > min_hr and confidence > min_conf:
            item_properties = [idx_begin, idx_end, confidence, hr]
            results.append(item_properties)

        # Update the start time of the detection
        idx_begin = idx_end

    return results

def on_process_audio(
        audio_id: str, audio_rec: dict, audio_file_path: str
):
    
    print(f"PROCESSING audioId={audio_id}")
    location = audio_rec["location"]

    # A call out to your code here. Optionally we can pass on the recorder coordinates 
    results = analyseAudioFile(audio_file_path)
    # The object results is a list containing detections in the form:
    # [start, end, confidence, harmonic ratio]

    # After processing we record each detection in the database. 
    # Each detection should have a start and end time which is used to create an audio clip later. 
    detections = []
    for r in results: 
        start, end, confidence, harmonic_ratio = r
        # create the detections
        detections.append({
            u"start": start,
            u"end": end,
            u"tags": ["snowmobile"],
            #u"analysisId": analysis_id,
            # Add any other information you want to record here
            u"confidence": confidence,
            u"harmonic_ratio": harmonic_ratio
        })

    print(detections)
    print(f"{audio_id} completed with {len(detections)} detections")



if __name__ == "__main__":


    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        help="Path to the file to analyze",
        required=True,
        type=str,
    )

    cli_args = parser.parse_args()

    on_process_audio("my-audio-id", {
        "location": {
            "latitude": 0,
            "longitude": 0
        }
    }, cli_args.input)

