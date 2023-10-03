#!/usr/env/bin python3

from flask import Flask, request, jsonify
app = Flask(__name__)

import os
from dotenv import load_dotenv

import argparse
import numpy as np

import smtplib
from email.message import EmailMessage

import torch
from torch.utils.data import DataLoader

from predict import predict
from predict import initModel
from utils.utils import AudioList

from google.cloud import storage
import io

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Get the environment variables
load_dotenv(dotenv_path="/app/cloud_analysis/gmail_logs.env")

GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PASS = os.environ.get('GMAIL_PASS')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

if not GMAIL_USER or not GMAIL_PASS:
    logging.error("GMAIL_USER or GMAIL_PASS environment variables are not set.")

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = RECEIVER_EMAIL

    # Establish a connection to Gmail
    try:
        logging.info("Attempting to connect to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        logging.info("Connected to Gmail SMTP server. Attempting login...")
        server.login(GMAIL_USER, GMAIL_PASS)
        logging.info("Logged in to Gmail. Sending email...")
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


from pydub import AudioSegment
import io

def convert_mp3_to_wav(mp3_file_object):
    # Load MP3 file from file object
    audio = AudioSegment.from_file(mp3_file_object, format="mp3")
    
    # Convert to WAV
    wav_file_object = io.BytesIO()
    audio.export(wav_file_object, format="wav")
    wav_file_object.seek(0)  # Move file pointer to the start
    
    return wav_file_object


def fetch_audio_data(bucket_name, blob_name):
    """
    Fetches audio data from Google Cloud Storage.

    Parameters:
        bucket_name (str): The name of the GCS bucket.
        blob_name (str): The name of the blob (file) in the GCS bucket.

    Returns:
        BytesIO: An in-memory file object of the audio data.
    """
    # Create a GCS client
    from google.oauth2 import service_account
    import google.auth

    credentials = service_account.Credentials.from_service_account_file(
        '/app/cloud_analysis/g_application_credentials.json'
)

    storage_client = storage.Client(credentials=credentials)

    # Get the GCS bucket and blob
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Download the file into an in-memory file object
    audio_file_object = io.BytesIO()
    blob.download_to_file(audio_file_object)
    audio_file_object.seek(0)  # Move file pointer to the start

    # Convert MP3 to WAV
    wav_file_object = convert_mp3_to_wav(audio_file_object)
    
    return wav_file_object


def analyseAudioFile(
        audio_file_object, batch_size=1, num_workers=4, min_hr = 0.1, min_conf = 0.99
):

    # Initiate model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "/app/audioclip/assets/snowmobile_model.pth"
    model = initModel(model_path=model_path, device=device)

    # Run the predictions
    list_preds = AudioList().get_processed_list(audio_file_object)
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

def on_process_audio(audio_id: str, audio_rec: dict, bucket_name: str, blob_name: str):
    
    print(f"PROCESSING audioId={audio_id}")
    location = audio_rec["location"]

    # A call out to your code here. Optionally we can pass on the recorder coordinates 
    audio_file_object = fetch_audio_data(bucket_name, blob_name)
    results = analyseAudioFile(audio_file_object)
    # The object results is a list containing detections in the form:
    # [start, end, confidence, harmonic ratio]

    # After processing we record each detection in the database. 
    # Each detection should have a start and end time which is used to create an audio clip later. 
    count = 0
    detections = []
    for r in results: 
        start, end, confidence, harmonic_ratio = r
        if harmonic_ratio > 0.1 and confidence > 0.99:
            count += 1

        # create the detections dataset
        detections.append({
            u"start": start,
            u"end": end,
            u"tags": ["snowmobile"],
            u"confidence": confidence,
            u"harmonic_ratio": harmonic_ratio,
            #u"analysisId": analysis_id,
            # Add any other information you want to record here
        })

    return count


@app.route('/process-audio', methods=['POST'])
def process_audio_endpoint():
    data = request.json
    bucket_name = data['bucket_name']
    blob_name = data['blob_name']
    audio_id = data['audio_id']
    audio_rec = data['audio_rec']
    
    results = on_process_audio(audio_id, audio_rec, bucket_name, blob_name)

    if results > 0:
        send_email("Snowmobile Detection Alert", f"{results} snowmobile detections were made in the audio file!")

    return jsonify({"message": "Audio processing completed!"})


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

