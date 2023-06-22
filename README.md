# Snowmobile analyser

This repository contains the necessary for running the snowmobile detector.

## Use of the repository

Copy the github repository and get the model from [Zenodo](https://zenodo.org/record/7969521).

```bash
git clone https://github.com/NINAnor/snowmobile_analyzer.git
cd snowmobile-analyzer/audioclip
wget https://zenodo.org/record/7969521/files/assets.zip?download=1
tar -xvf ./assets.zip?download=1
cd ../
```

### Use with Docker (recommanded)

Pull the Docker image:



Run the detector:

```bash
docker run \
    --rm \
    --gpus all \
    -v $PWD:/app snowmobile \
        --input example/example_audio.mp3 \
        --output example/analysed_example_audio.csv
```

### Use without Docker

Install the dependancies and update the PYTHONPATH:

```bash
poetry install --no-root
export PYTHONPATH="${PYTHONPATH}:/app:/app/audioclip"
```

Run the script:

```bash
poetry run python src/predict.py \
        --input example/example_audio.mp3 \
        --output example/analysed_example_audio.csv
```