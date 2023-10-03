#!/bin/bash

curl -X POST -H "Content-Type: application/json" \
    -d '{"audio_file_path": "/app/example/example_audio.mp3", "audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}}' \
    http://localhost:8080/process-audio