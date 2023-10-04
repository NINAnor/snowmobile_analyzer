import requests
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.cloud import storage
import io
import json

from google.oauth2 import id_token
from google.auth.transport.requests import AuthorizedSession

def get_id_token(service_account_info):
    """
    Obtain an ID token for authentication from the service account info.

    Parameters:
        service_account_info (dict): The service account info in dictionary format.

    Returns:
        str: An ID token for authentication.
    """
    # Create credentials object from service account info
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    
    # Create a Request object
    request_obj = Request()
    
    # Obtain an ID token to use for authentication
    id_token_info = id_token.fetch_id_token(request_obj, "https://model-4uhtnq5xla-lz.a.run.app")
    
    return id_token_info

def fetch_service_account_key(bucket_name, blob_name):
    """
    Fetch the service account key file from Google Cloud Storage.

    Parameters:
        bucket_name (str): The name of the GCS bucket.
        blob_name (str): The name of the blob (file) in the GCS bucket.

    Returns:
        dict: The service account key file as a dictionary.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Download the JSON key file content
    key_file_content = blob.download_as_text()
    
    # Convert the JSON content to a dictionary
    key_file_dict = json.loads(key_file_content)
    
    return key_file_dict

def trigger_audio_analysis(data, context):
    file_name = data['name']
    bucket_name = data['bucket']
    
    # URL of your Cloud Run service
    cloud_run_url = "https://model-4uhtnq5xla-lz.a.run.app/process-audio"
    
    # Payload to send to Cloud Run
    payload = {
        "bucket_name": bucket_name,
        "blob_name": file_name,
        "audio_id": "example-audio-id",
        "audio_rec": {"location": {"latitude": 0, "longitude": 0}}
    }
    
    # Specify the GCS bucket and blob name of the service account key file
    key_file_bucket = "snoskuter-detector-test"
    key_file_blob = "key-file.json"
    
    # Fetch the service account key file from GCS
    service_account_info = fetch_service_account_key(key_file_bucket, key_file_blob)
    
    # Obtain the identity token
    id_token = get_id_token(service_account_info)
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    
    # Send a POST request to the Cloud Run service
    response = requests.post(cloud_run_url, json=payload, headers=headers)
    
    # Log the response
    print(f"Response from Cloud Run: {response.text}")