FROM busybox:1.36 AS assets
ADD --checksum=sha256:0a4c8f86f45cb1ba647f9a15a42a18a2ff178da31431fabb1d16271296138279 \
    "https://zenodo.org/record/7969521/files/assets.zip?download=1" \
    /assets/assets.zip
RUN unzip -q -o /assets/assets.zip -d /assets \
    && rm /assets/assets.zip

# Use latest CUDA runtime image
FROM nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu22.04

# Copy uv binary from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy

WORKDIR /app

# System dependencies for audio decoding
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy application code and the model assets
COPY . .
COPY --from=assets /assets ./audioclip

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENV PYTHONPATH=/app:/app/src:/app/audioclip

ENTRYPOINT ["uv", "run", "python", "src/predict.py"]
