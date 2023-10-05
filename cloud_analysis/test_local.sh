#!/bin/bash

curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"hr": 0.00, "conf": 0.0001, "audio_id": "test-id", "audio_rec": {"location": {"latitude": 0, "longitude": 0}}, "bucket_name": "snoskuter-detector-test", "blob_name": "from_BUGG.mp3"}' \
     http://localhost:8080/process-audio


# proj_snowmobile/bugg_RPiID-10000000f8e69c84/conf_6f40914/2023-10-04T11_28_44.579Z.mp3
# other.mp3