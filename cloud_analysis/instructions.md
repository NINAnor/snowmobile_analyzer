# Documentation on running a Docker container on google cloud

## General stuff with GCloud UI

- If lost, there is a button `console` on the upper right corner that brings us back to the projects


## Login stuff

1- Generate the Google Cloud credentials:

```
gcloud auth application-default login
```

The credentials are stored in `~/.config/gcloud/`

2- Login to your Google Cloud account:

```
gcloud auth login
```

3- Log in to the project

```
gcloud config set project snokuter-akustikk
```

## Docker stuff

1- Enable services

Enable the Cloud Functions, Cloud Run, and Cloud Build APIs:

```
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2- Set up credentials on Google Cloud:

The credentials are stored in `~/.docker/config.json`

```
gcloud auth configure-docker
```

3- Change the name of the image to push it on GCloud

The Docker image will be saved in Google's container registry, which is directly supported by Cloud Run

```
docker tag ghcr.io/ninanor/snowmobile_analyzer:main gcr.io/snoskuter-akustikk/snowmobile_analyzer:main
docker push gcr.io/snoskuter-akustikk/snowmobile_analyzer:main

```

4- Deploy the Docker image to Google Cloud run

```
gcloud run deploy model --image gcr.io/snoskuter-akustikk/snowmobile_analyzer:main
```
