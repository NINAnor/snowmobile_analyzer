<h1 align="center">Snowmobile analyzer :snowflake: </h1>
<h2 align="center">A model to detect whether snowmobiles are present in an acoustic dataset.</h2>

![CC BY-NC-SA 4.0][license-badge]
![Supported OS][os-badge]
[![DOI](https://zenodo.org/badge/644880301.svg)](https://zenodo.org/badge/latestdoi/644880301)

[license-badge]: https://badgen.net/badge/License/MIT/red
[os-badge]: https://badgen.net/badge/OS/Linux/blue

# Introduction

This repository contains the necessary for running the snowmobile detector on audio dataset.


## Use of the repository

Below are the intructions on installing and using the snowmobile detector with both Docker and without. The output of the script is a subfolder `SNOWMOBILE_RESULTS` containing the `.csv` file of the analyzed file. Note that the folder `SNOWMOBILE_RESULTS` will be located in the same folder as the input file.

### Use with Docker (recommanded)

Create the Docker image image:

```
git clone https://github.com/NINAnor/snowmobile_analyzer.git
cd snowmobile_analyzer
docker build -t snowmobile -f Dockerfile .
```

Run the program:

```bash
./analyze.sh ./example/example_audio.mp3 
```

Note that you can change `./example/example_audio.mp3` to the path of your own file.

### Use without Docker

Install `poetry` (the package manager we use) if it is not already installed.

```bash
pip install poetry
```

Copy the github repository and get the model from [Zenodo](https://zenodo.org/record/7969521).

```bash
cd ~ 
git clone https://github.com/NINAnor/snowmobile_analyzer.git
cd snowmobile-analyzer/audioclip
wget https://zenodo.org/record/7969521/files/assets.zip?download=1
unzip ./assets.zip?download=1
cd ../
```

Install the dependancies and update the `PYTHONPATH`:

```bash
poetry install --no-root
export PYTHONPATH="${PYTHONPATH}:~/snowmobile_analyzer/:~/snowmobile_analyzer/audioclip"
```

Run the script:

```bash
poetry run python src/predict.py --input example/example_audio.mp3
```

### Output

The program creates a folder SNOWMOBILE_RESULTS containing a `.csv` file with the following columns:

| start_detection | end_detection | label | confidence | hr |
|-----------------|---------------|-------|------------|----|
| 0 | 3 | 1 | 0.97691464 | 0.19687336119166438 |
| 3 | 6 | 1 | 0.9611957 | 0.16774687365839228 |

- `start_detection` and `end_detection` are in **seconds**
- `label` is always equal to 1 (i.e. snowmobile detected)
- `confidence` is the model confidence
- `hr` is the harmonic ratio value

By default the program select detections for which `confidence` > 0.95 and `hr` > 0.1.
 
## Acknowlegment and contact

For bug reports please use the [issues section](https://github.com/NINAnor/snowmobile_analyzer/issues).

For other inquiries please contact [Benjamin Cretois](mailto:benjamin.cretois@nina.no) or [Femke Gelderblom](mailto:femke.gelderblom@sintef.no) 


## Cite this work

Cretois, B., Bick, I. A., Balantic, C., Gelderblom, F., Pavon-Jordan, D., Wiel, J., ... & Reinen, T. A. (2023). Snowmobile noise alters bird vocalization patterns during winter and pre-breeding season. bioRxiv, 2023-07.
