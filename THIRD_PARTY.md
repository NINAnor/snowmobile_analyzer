# Third-party software

This repository vendors code from the following third-party projects. Their
license texts are reproduced in the corresponding upstream repositories.

## AudioCLIP

- Source: https://github.com/AndreyGuzhov/AudioCLIP
- Reference: v0.1 (commit 611d974591b32f03a7dd1ef4c3c14355739d9aca)
- License: MIT
- Description: "AudioCLIP: Extending CLIP to Image, Text and Audio"
  (arXiv:2106.13043). The model implementation used by this project
  (directory `audioclip/`).

The vendored copy differs from upstream v0.1 in the following ways:

- the top-level `ignite_trainer/` package is renamed to `training/ignite_trainer/`
  and its imports updated accordingly;
- `model/audioclip.py` uses `dtype=torch.int64` in `torch.arange`;
- `utils/simple_tokenizer.py` reads the tokenizer path from `CONFIG.yaml`
  instead of a hardcoded path;
- `model/custom_model.py` is added (the fine-tuned snowmobile model wrapper).

## OpenAI CLIP

- Source: https://github.com/openai/CLIP
- License: MIT
- Used in: `audioclip/model/clip/`, `audioclip/utils/simple_tokenizer.py`

## PyTorch vision

- Source: https://github.com/pytorch/vision
- License: BSD-3-Clause
- Used in: the ResNet blocks in `audioclip/model/esresnet/base.py`
