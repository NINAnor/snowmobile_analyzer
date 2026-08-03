<h1 align="center">Snowmobile analyzer :snowflake: </h1>
<h2 align="center">A model to detect whether snowmobiles are present in an acoustic dataset.</h2>

![CC BY-NC-SA 4.0][license-badge]
![Supported OS][os-badge]
[![DOI](https://zenodo.org/badge/644880301.svg)](https://zenodo.org/badge/latestdoi/644880301)

[license-badge]: https://badgen.net/badge/License/MIT/red
[os-badge]: https://badgen.net/badge/OS/Linux/blue

# Introduction

This repository is made to run the snowmobile detector on your audio files.

Moreover, in this repository we provide guidance on setting up a pipeline for real-time analysis of audio files on [Google Cloud](https://cloud.google.com/). For more information see the [README in the subfolder cloud_analysis](https://github.com/NINAnor/snowmobile_analyzer/blob/main/cloud_analysis/README.md).

## Setup

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
uv sync --dev
```

Copy the GitHub repository and get the model from [Zenodo](https://zenodo.org/record/7969521).

```bash
cd audioclip
wget "https://zenodo.org/record/7969521/files/assets.zip?download=1"
unzip "./assets.zip?download=1"
cd ..
```

Place the model files inside `audioclip/assets/` (adjust the paths in `CONFIG.yaml` if needed).

## Use of the repository

Below are the instructions on installing and using the snowmobile detector with both Docker and without. The output of the script is a subfolder `SNOWMOBILE_RESULTS` containing the `.csv` file of the analyzed file. Note that the folder `SNOWMOBILE_RESULTS` will be located in the same folder as the input file.

### Use with Docker

Create the Docker image:

```
docker build -t snowmobile -f Dockerfile .
```

Run the program using the `analyze.sh` script which is a wrapper around the Docker command:

```bash
./analyze.sh ./example/example_audio.mp3
```

Note that if you want to have more control over the arguments you can use Docker:

```bash
docker run \
    --rm \
    --gpus all \
    -v ./logs:/app/logs \ # Important to write the log files
    -v "$FOLDER_TO_EXPOSE":/data \
    snowmobile \
    /data/"$FILENAME"
```

Note that you can change `./example/example_audio.mp3` to the path of your own file.

### Use without Docker

Run the script:

```bash
uv run python src/predict.py example/example_audio.mp3
```

### Output

The program creates a folder `SNOWMOBILE_RESULTS` containing a `.csv` file with the following columns:

| start_detection | end_detection | label | confidence | hr |
|-----------------|---------------|-------|------------|----|
| 0 | 3 | 1 | 0.97691464 | 0.19687336119166438 |
| 3 | 6 | 1 | 0.9611957 | 0.16774687365839228 |

- `start_detection` and `end_detection` are in **seconds**
- `label` is always equal to 1 (i.e. snowmobile detected)
- `confidence` is the model confidence
- `hr` is the harmonic ratio value

By default the program selects detections for which `confidence` > 0.95 and `hr` > 0.1.

## Update from template

To update this project with the latest changes from the template, run:

```bash
uvx --with copier-template-extensions copier update --trust
```

You can keep your previous answers by using:

```bash
uvx --with copier-template-extensions copier update --trust --defaults
```

## Development

Run the [prek](https://prek.j178.dev/) git hooks to keep code quality:

```bash
prek install
prek run --all-files
```

## Acknowledgment and contact

For bug reports please use the [issues section](https://github.com/NINAnor/snowmobile_analyzer/issues).

For other inquiries please contact [Benjamin Cretois](mailto:benjamin.cretois@nina.no) or [Femke Gelderblom](mailto:femke.gelderblom@sintef.no).

## Cite this work

Cretois, B., Bick, I. A., Balantic, C., Gelderblom, F., Pavon-Jordan, D., Wiel, J., ... & Reinen, T. A. (2023). Snowmobile noise alters bird vocalization patterns during winter and pre-breeding season. bioRxiv, 2023-07.
