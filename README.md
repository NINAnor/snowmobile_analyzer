# Snowmobile analyser

This repository contains the necessary for running the snowmobile detector.

## Use of the repository

Below are the intructions on installing and using the snowmobile detector with both Docker and without. The output of the script is a subfolder `SNOWMOBILE_RESULTS` containing the `.csv` file of the analyzed file. Note that the folder `SNOWMOBILE_RESULTS` will be located in the same folder as the input file.

### Use with Docker (recommanded)

Pull the Docker image:

```
docker pull ghcr.io/ninanor/snowmobile_analyzer:main
```

Run the program:

```bash
./analyze.sh ~/Code/snowmobile-analyzer/example/example_audio.mp3
```

### Use without Docker - assume Linux installation!

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

## Acknowlegment and contact

For bug reports please use the [issues section](https://github.com/NINAnor/snowmobile_analyzer/issues).

For other inquiries please contact [Benjamin Cretois](mailto:benjamin.cretois@nina.no) or [Femke Gelderblom](mailto:femke.gelderblom@sintef.no) 


## Cite this work

Manuscript for this work soon to be available.