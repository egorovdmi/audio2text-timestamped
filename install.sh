#!/bin/bash

# Installation script for audio2text-timestamped
# Handles the sentencepiece compilation issue on Python 3.13

echo "Installing audio2text-timestamped dependencies..."

echo "Step 1: Installing core dependencies..."
pip install faster-whisper torch torchaudio

echo "Step 2: Installing pyannote.audio without problematic dependencies..."
pip install --no-deps pyannote.audio

echo "Step 3: Installing remaining dependencies..."
pip install \
    "asteroid-filterbanks>=0.4" \
    "einops>=0.6.0" \
    "omegaconf>=2.1,<3.0" \
    "pyannote.core>=5.0.0" \
    "pyannote.database>=5.0.1" \
    "pyannote.metrics>=3.2" \
    "pyannote.pipeline>=3.0.1" \
    "pytorch-metric-learning>=2.1.0" \
    "rich>=12.0.0" \
    "semver>=3.0.0" \
    "soundfile>=0.12.1" \
    "tensorboardX>=2.6" \
    "torch-audiomentations>=0.11.0" \
    "torchmetrics>=0.11.0"

echo "Installation complete!"
echo "Note: speechbrain is skipped due to sentencepiece compilation issues on Python 3.13"
echo "This should not affect speaker diarization functionality."
