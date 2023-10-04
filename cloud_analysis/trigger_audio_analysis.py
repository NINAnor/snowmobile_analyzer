import requests
import os
from google.cloud import storage

def trigger_audio_analysis(data, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This function is triggered when a file is uploaded to the GCS bucket.
    """
    file_name = data['name']
    bucket_name = data['bucket']
    
    # URL of your Cloud Run service
    cloud_run_url = "https://model-4uhtnq5xla-lz.a.run.app/process-audio"
    
    # ID Token for authentication
    id_token = os.environ.get("ID_TOKEN")
    
    # Payload to send to Cloud Run
    payload = {
        "bucket_name": bucket_name,
        "blob_name": file_name,
        "audio_id": "example-audio-id",
        "audio_rec": {"location": {"latitude": 0, "longitude": 0}}
    }
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    
    # Send a POST request to the Cloud Run service
    response = requests.post(cloud_run_url, json=payload, headers=headers)
    
    # Log the response
    print(f"Response from Cloud Run: {response.text}")
