FROM python:3.8

ARG PACKAGES="ffmpeg build-essential unzip"

ARG DEBIAN_FRONTEND=noninteractive
RUN \
    apt-get update && \
    apt-get install -qq $PACKAGES && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry 

WORKDIR /app

# Package install
COPY . ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# Clone the repository and download assets
RUN cd audioclip 
RUN wget https://zenodo.org/record/7969521/files/assets.zip?download=1 
RUN unzip ./assets.zip?download=1 
RUN cd ../

ENV PYTHONPATH "${PYTHONPATH}:/app:/app/audioclip"
ENTRYPOINT [ "./entrypoint.sh" ]

