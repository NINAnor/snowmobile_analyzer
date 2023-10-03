# Documentation on running a Docker container on google cloud

## General stuff with GCloud UI

- If lost, there is a button `console` on the upper right corner that brings us back to the projects

## Create service account with access to the Google Cloud bucket

First create a new service account:

```
IAM and Admin -> Service Account -> Create Service Account
```

Then you need to change the permission for **Storage Object Viewer** so that the service account can access the cloud bucket.

Then create a **Key** that will act as the `GOOGLE_APPLICATION_CREDENTIALS`, an environment variable that authentificate a user for accessing the Google Cloud Bucket (see `main.py/fetch_audio_data`).

Copy/Paste the `.json` file created from the key and copy it in a file called `g_application_credentials.json`. This will be access in the `main.py/fetch_audio_data`:

```
    credentials = service_account.Credentials.from_service_account_file(
        '/app/cloud_analysis/g_application_credentials.json'
)

    storage_client = storage.Client(credentials=credentials)
```

## Create the Docker image for Cloud analysis

The Docker image used for the cloud analysis is slightly different:

- The entrypoint uses `cloud_analysis/main.py`
- Some libraries are added to the base `pyproject.toml` (i.e. `Flask`, `distlib`)
- `snowmobile_cloud` also has a `.env` file containing the information for `Gmail` loggin

Make sure you have the following `gmail_logs.env` in the folder `cloud_analysis`:

```
GMAIL_USER=XXX@gmail.com
GMAIL_PASS=XXX
RECEIVER_EMAIL=XXX@gmail.com
```

You may need to **Use an App Password** that you can set from your [Google Account](https://myaccount.google.com/) -> Security -> 2-step validation -> App Password (bottom of the page).

Then run:

```bash
docker build -t snowmobile_cloud -f cloud_Dockerfile .
```

It is possible to test the image by sending a file to the endpoint:

```
docker run --rm -p 8080:8080 -v $PWD:/app snowmobile_cloud
```

And in another terminal:

```bash
cd cloud_analysis
./test.sh
```

The sender should receive an email.

## Login stuff

1- Generate the Google Cloud credentials:

```bash
gcloud auth application-default login
```

The credentials are stored in `~/.config/gcloud/`

2- Login to your Google Cloud account:

```bash
gcloud auth login
```

3- Log in to the project

```bash
gcloud config set project snokuter-akustikk
```

## Docker stuff

1- Enable services

Enable the Cloud Functions, Cloud Run, and Cloud Build APIs:

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2- Set up credentials on Google Cloud:

The credentials are stored in `~/.docker/config.json`

```bash
gcloud auth configure-docker
```

3- Change the name of the image to push it on GCloud

The Docker image will be saved in Google's container registry, which is directly supported by Cloud Run

```bash
docker tag snowmobile_cloud gcr.io/snoskuter-akustikk/snowmobile_cloud:main
docker push gcr.io/snoskuter-akustikk/snowmobile_cloud:main

```

4- Deploy the Docker image to Google Cloud run

```bash
gcloud run deploy \
    model \
    --image gcr.io/snoskuter-akustikk/snowmobile_cloud:main \
    --memory 1Gi \
    --region europe-north1 \
    --platform managed
```

Be sure to allocate enough memory for the service to be able to process the files and run the model.
