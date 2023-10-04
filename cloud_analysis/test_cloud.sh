ID_TOKEN=$(gcloud auth print-identity-token)

curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${ID_TOKEN}" \
     -d '{"audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}, "bucket_name": "snoskuter-detector-test", "blob_name": "example_audio.mp3"}' \
     https://model-4uhtnq5xla-lz.a.run.app/process-audio


