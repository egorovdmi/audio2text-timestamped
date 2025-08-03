# Speaker Diarization Module

## Overview

This module provides speaker diarization functionality using the `pyannote/speaker-diarization-3.1` model. It analyzes audio files to identify different speakers and their speaking intervals.

## Features

- **Automatic speaker detection** - Identifies multiple speakers in audio
- **Time-stamped segments** - Provides precise start/end times for each speaker
- **Post-processing** - Filters short segments and merges close segments from same speaker
- **Multiple device support** - Works with CPU, CUDA GPU, and Apple Silicon (MPS)
- **JSON output** - Compatible with existing project structure

## Installation

```bash
pip install -r requirements.txt
```

### HuggingFace Authentication

The pyannote model requires HuggingFace authentication **only for the first download**:

```bash
huggingface-cli login
```

**Important**: After the first successful download, the model is cached locally and can be used without internet connection or re-authentication.

### Model Caching

Models are automatically cached in your local HuggingFace cache directory:

- **Linux/Mac**: `~/.cache/huggingface/hub/`
- **Windows**: `C:\Users\{username}\.cache\huggingface\hub\`

Check cache status:

```bash
python speaker_diarization.py cache info
```

Clear cache (if needed):

```bash
python speaker_diarization.py cache clear
```

## Usage

### Command Line Interface

```bash
# Basic usage
python speaker_diarization.py audio_file.mp3

# Or explicitly use diarize command
python speaker_diarization.py diarize audio_file.mp3

# With custom output file
python speaker_diarization.py diarize audio_file.mp3 -o results.json

# Force CPU usage
python speaker_diarization.py diarize audio_file.mp3 --device cpu

# Adjust sensitivity
python speaker_diarization.py diarize audio_file.mp3 --min-duration 1.0 --max-gap 0.5

# Check cache information
python speaker_diarization.py cache info

# Clear model cache
python speaker_diarization.py cache clear
```

### Programmatic Usage

```python
from speaker_diarization import SpeakerDiarizer

# Initialize diarizer
diarizer = SpeakerDiarizer(
    device="auto",
    min_segment_duration=0.5,
    max_gap_duration=0.3
)

# Process audio file
results = diarizer.diarize_audio("audio_file.mp3")

# Save results
diarizer.save_results(results, "output.json")
```

## Output Format

```json
{
  "file_path": "audio_file.mp3",
  "duration": 60.35,
  "speakers_detected": 2,
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 10.98,
      "duration": 10.98,
      "speaker": "SPEAKER_00"
    },
    {
      "start_time": 11.16,
      "end_time": 19.18,
      "duration": 8.02,
      "speaker": "SPEAKER_01"
    }
  ]
}
```

## Parameters

### SpeakerDiarizer Parameters

- `model_name` (str): Pyannote model name (default: "pyannote/speaker-diarization-3.1")
- `device` (str): Device to use - "auto", "cpu", "cuda", "mps" (default: "auto")
- `min_segment_duration` (float): Minimum duration for speech segments in seconds (default: 0.5)
- `max_gap_duration` (float): Maximum gap to merge adjacent segments in seconds (default: 0.3)

### Command Line Options

**Diarization command:**

- `-o, --output`: Output JSON file path
- `--model`: Pyannote model name
- `--device`: Device to use (auto, cpu, cuda, mps)
- `--min-duration`: Minimum segment duration in seconds
- `--max-gap`: Maximum gap to merge segments in seconds
- `-v, --verbose`: Enable verbose logging

**Cache management:**

- `cache info`: Show cache location and size
- `cache clear`: Clear all cached models

## Testing

Run the test script to verify functionality:

```bash
python test_speaker_diarization.py
```

Run the demo script to see example usage:

```bash
python demo_speaker_diarization.py
```

## Offline Usage

After the first successful download, the model can be used completely offline:

1. **First time setup** (requires internet and authentication):

   ```bash
   huggingface-cli login
   python speaker_diarization.py diarize test_audio.mp3
   ```

2. **Subsequent usage** (no internet required):

   ```bash
   # Works offline automatically
   python speaker_diarization.py diarize audio_file.mp3
   ```

3. **Check what's cached**:

   ```bash
   python speaker_diarization.py cache info
   ```

4. **Manual cache location**:
   - Linux/Mac: `~/.cache/huggingface/hub/`
   - Windows: `C:\Users\{username}\.cache\huggingface\hub\`

You can even copy the cache directory to another machine for offline deployment.

## Supported Audio Formats

- MP3
- WAV
- M4A
- FLAC
- OGG
- And other formats supported by torchaudio

## Performance Notes

- **GPU recommended** - Diarization can be slow on CPU
- **Memory usage** - Large files may require significant RAM
- **First run** - Model download may take time on first execution

## Troubleshooting

### Common Issues

1. **Authentication Error (First Time Only)**

   ```bash
   huggingface-cli login
   ```

   Then accept the license at: https://huggingface.co/pyannote/speaker-diarization-3.1

2. **Model Already Cached**

   ```bash
   python speaker_diarization.py cache info
   ```

   Check if model is already downloaded

3. **CUDA Out of Memory**

   ```bash
   python speaker_diarization.py diarize --device cpu audio_file.mp3
   ```

4. **ImportError**

   ```bash
   pip install -r requirements.txt
   ```

5. **Offline Usage**
   After first successful download, the model works offline automatically

### Performance Optimization

- Use GPU for faster processing
- Adjust `min_segment_duration` to filter noise
- Increase `max_gap_duration` to merge more segments
- Process shorter audio chunks for large files

## Integration

This module is designed to work as a preprocessing step before the main `audio2text_timestamped.py` script. The output can be used to:

1. Pre-segment audio by speaker
2. Enhance transcription with speaker labels
3. Improve timestamp accuracy using speaker boundaries
4. Generate speaker-specific transcriptions

## Examples

See the following files for usage examples:

- `test_speaker_diarization.py` - Basic functionality test
- `demo_speaker_diarization.py` - Interactive demonstration
