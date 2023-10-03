ID_TOKEN=$(gcloud auth print-identity-token)

curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${ID_TOKEN}" \
     -d '{"audio_file_path": "/app/example/example_audio.mp3", "audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}}' \
     https://model-4uhtnq5xla-lz.a.run.app/process-audio


