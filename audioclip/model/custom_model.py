import torch
from torch import nn
from torch.nn import functional as F

import pytorch_lightning as pl

from model import AudioCLIP

# Open the config file
import yaml
from yaml import FullLoader
with open("./CONFIG.yaml") as f:
    cfg = yaml.load(f, Loader=FullLoader)

class CustomAudioCLIP(pl.LightningModule):
    def __init__(self, num_target_classes, model_arguments=None):
        super().__init__()
        model_arguments = {} if model_arguments is None else model_arguments
        self.aclp = AudioCLIP(pretrained=cfg["path_audioclip"], **model_arguments)
        self.num_target_classes = num_target_classes
        self._build_model()

    def _build_model(self):
        backbone = self.aclp.audio
        num_filters = backbone.fc.out_features
        layers = list(backbone.children())[:-1]
        self.feature_extractor = nn.Sequential(*layers)

        # Classifier
        self.classifier = nn.Linear(num_filters, self.num_target_classes)

    def forward(self, x):
        audio_features = self.aclp.encode_audio(x) 
        x = self.classifier(audio_features)
        x = F.log_softmax(x)
        return x