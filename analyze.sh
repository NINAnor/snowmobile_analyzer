#!/bin/bash

# Get the path variables
INPUT=$1
FOLDER_TO_EXPOSE=$(dirname $INPUT)
FILENAME=$(basename $INPUT)

# Run the script
docker run \
    --rm \
    --gpus all \
    -v ./logs:/app/logs \
    -v $FOLDER_TO_EXPOSE:/data \
    snowmobile \
    --input /data/$FILENAME



# ghcr.io/ninanor/snowmobile_analyzer:main