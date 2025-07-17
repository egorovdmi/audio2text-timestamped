# Quick Start

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Simple run

```bash
python demo.py audio.mp3
```

### 2. Command line with options

```bash
python audio2text_timestamped.py audio.mp3 --output result.json --model base --pretty
```

### 3. Programmatic usage

```python
from audio2text_timestamped import AudioToTextConverter

converter = AudioToTextConverter(model_size="base")
result = converter.transcribe_audio("audio.mp3")
print(result)
```

## Supported formats

- MP3, WAV, M4A, FLAC, OGG, WebM, MP4

## Whisper models

- `tiny` - fast, less accurate
- `base` - balance of speed and accuracy (recommended)
- `small` - better accuracy
- `medium` - high accuracy
- `large-v2`, `large-v3` - maximum accuracy

## Result

JSON with sentences and timestamps:

```json
{
  "detected_language": "en",
  "sentences": [
    {
      "sentence": "First sentence.",
      "start_time": 0.0,
      "end_time": 3.25,
      "duration": 3.25,
      "language": "en"
    }
  ]
}
```
