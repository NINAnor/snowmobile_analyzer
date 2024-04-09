ID_TOKEN=$(gcloud auth print-identity-token)

curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${ID_TOKEN}" \
     -d '{"audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}, "bucket_name": "snoskuter-detector-test", "blob_name": "proj_miljodir/bugg_RPiID-10000000f8e69c84/conf_6f40914/2024-04-08T11_54_33.575Z.mp3", "hr": 0.1, "conf": 0.99}' \
     https://model-4uhtnq5xla-lz.a.run.app/process-audio


