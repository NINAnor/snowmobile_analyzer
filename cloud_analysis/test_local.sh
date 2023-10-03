#!/bin/bash

curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}, "bucket_name": "snoskuter-detector-test", "blob_name": "example_audio.mp3"}' \
     http://localhost:8080/process-audio
