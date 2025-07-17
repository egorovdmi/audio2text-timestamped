# Audio to Text with Timestamps

This project provides a Python script for converting audio files to text with timestamps using the Faster-Whisper library.

## Features

- Speech recognition with precise timestamps
- Automatic text division into sentences
- Audio language detection
- Support for various audio file formats
- Export results in JSON format
- Choice of Whisper models of different sizes

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd audio2text-timestamped
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

Basic usage:

```bash
python audio2text_timestamped.py audio_file.mp3
```

With additional parameters:

```bash
python audio2text_timestamped.py audio_file.mp3 --model medium --output result.json --language en --pretty
```

### Parameters

- `audio_file` - Path to the audio file
- `--model` - Whisper model size (tiny, base, small, medium, large-v2, large-v3)
- `--output` - Output file name (default: generates automatically)
- `--language` - Audio language (auto-detection if not specified)
- `--device` - Device for processing (cpu, cuda, auto)
- `--pretty` - Pretty JSON formatting

### Makefile

For convenience, use the Makefile:

```bash
# Install dependencies
make install

# Run test
make test

# Quick test
make quick-test

# Unit tests
make unit-test

# Transcribe audio file
make transcribe FILE=audio.mp3 MODEL=medium

# Convert result to CSV and SRT
make convert

# Show help
make help
```

## Model Selection

### Available Models

- **tiny** (~40 MB) - Fastest, lowest accuracy
- **base** (~140 MB) - Good balance of speed and accuracy
- **small** (~460 MB) - Better accuracy
- **medium** (~1.5 GB) - Recommended for production
- **large-v2** (~3.0 GB) - High accuracy
- **large-v3** (~3.1 GB) - Best accuracy

### Model Recommendations

- For quick testing: `tiny` or `base`
- For production use: `medium` or `small`
- For maximum accuracy: `large-v3`

**Note**: First download of large models may take 10-30 minutes depending on internet speed.

## Output Format

The script generates JSON with the following structure:

```json
{
  "file_path": "audio.mp3",
  "detected_language": "en",
  "language_probability": 0.95,
  "duration": 120.5,
  "full_text": "Complete transcription text...",
  "sentences": [
    {
      "sentence": "First sentence.",
      "start_time": 0.0,
      "end_time": 2.5,
      "duration": 2.5,
      "language": "en"
    }
  ],
  "word_count": 45,
  "sentence_count": 8
}
```

## Utilities

### Converting Results

Use `utils.py` to convert JSON results to other formats:

```bash
# Convert to CSV
python utils.py result.json --csv output.csv

# Convert to SRT subtitles
python utils.py result.json --srt output.srt

# Show statistics
python utils.py result.json --stats

# Search in transcript
python utils.py result.json --search "search text"
```

### Programmatic Usage

```python
from audio2text_timestamped import AudioToTextConverter

# Create converter
converter = AudioToTextConverter(model_size="medium", device="auto")

# Transcribe audio
result = converter.transcribe_audio("audio.mp3")

# Access results
print(f"Language: {result['detected_language']}")
print(f"Duration: {result['duration']:.2f} seconds")
print(f"Text: {result['full_text']}")

# Access sentences with timestamps
for sentence in result['sentences']:
    print(f"[{sentence['start_time']:.2f}s - {sentence['end_time']:.2f}s] {sentence['sentence']}")
```

## Examples

### Basic Example

```bash
python audio2text_timestamped.py interview.mp3
```

### With Specific Model

```bash
python audio2text_timestamped.py lecture.mp3 --model large-v3 --output lecture_transcript.json
```

### With Language Specification

```bash
python audio2text_timestamped.py spanish_audio.mp3 --language es --model medium
```

## Testing

Run tests to verify everything works:

```bash
# Integration test
make test

# Quick test with demo
make quick-test

# Unit tests
make unit-test

# Legacy test with audio file creation
make test-legacy
```

## Supported Audio Formats

- MP3
- WAV
- M4A
- FLAC
- OGG
- WebM
- MP4
- AIFF

## System Requirements

- Python 3.8+
- 4GB+ RAM (more for larger models)
- Internet connection for first model download

## Troubleshooting

### Model Loading Issues

If models take too long to load:

1. Use smaller models: `tiny`, `base`, or `small`
2. Check internet connection
3. Wait patiently for first download (10-30 minutes)

### Memory Issues

If you encounter memory errors:

1. Use smaller models
2. Close other applications
3. Use CPU instead of GPU: `--device cpu`

### Audio File Issues

If audio files are not recognized:

1. Check file format (use supported formats)
2. Verify file is not corrupted
3. Try converting to MP3 or WAV

## License

This project is licensed under the MIT License.

## Dependencies

- faster-whisper
- argparse (built-in)
- json (built-in)
- pathlib (built-in)
- re (built-in)

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- OpenAI for the Whisper model
- Faster-Whisper team for the optimized implementation
