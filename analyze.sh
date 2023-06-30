#!/bin/bash

set -euo pipefail
# Get the path variables
INPUT="$1"
FOLDER_TO_EXPOSE="$(dirname "$INPUT")"
FILENAME="$(basename "$INPUT")"

# Run the script
exec docker run \
    --rm \
    --gpus all \
    -v ./logs:/app/logs \
    -v "$FOLDER_TO_EXPOSE":/data \
    ghcr.io/ninanor/snowmobile_analyzer:main \
    --input /data/"$FILENAME"



