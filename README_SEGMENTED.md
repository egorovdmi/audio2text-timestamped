# Audio to Text with Timestamps - Enhanced with Speaker Diarization

This project provides a comprehensive Python solution for converting audio files to text with timestamps, featuring both traditional full-file transcription and advanced speaker-aware segmented transcription.

## 🚀 Features

### Core Features

- **Speech recognition** with precise timestamps using Faster-Whisper
- **Speaker diarization** using pyannote.audio models
- **Segmented transcription** for higher accuracy per speaker
- **Automatic language detection** for multilingual content
- **Multiple output formats**: JSON, SRT subtitles
- **Overlap resolution** for speaker conflicts
- **Complete pipeline** from audio to final transcription

### Transcription Methods

1. **Traditional Method**: Full-file transcription with timestamp detection
2. **Segmented Method**: Speaker diarization → segment extraction → individual transcription

## 📁 Project Structure

```
audio2text-timestamped/
├── audio2text_timestamped.py       # Original full-file transcription
├── speaker_diarization.py          # Speaker diarization with overlap resolution
├── extract_audio_segments.py       # Audio segment extraction
├── audio2text_segments.py          # Segmented transcription system
├── segmented_transcription_pipeline.py  # Complete pipeline
├── utils.py                        # Utility functions
├── test_pipeline.py                # Pipeline testing script
└── requirements.txt                # Dependencies
```

## 🛠️ Installation

1. **Clone the repository:**

```bash
git clone <repository-url>
cd audio2text-timestamped
```

2. **Create a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Accept pyannote.audio terms:**

- Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
- Accept the terms and get your access token
- Login: `huggingface-cli login`

## 🎯 Quick Start

### Method 1: Complete Pipeline (Recommended)

Run the full segmented transcription pipeline:

```bash
# Test on available files
python test_pipeline.py

# Run on specific file
python segmented_transcription_pipeline.py your_audio.mp3

# With custom settings
python segmented_transcription_pipeline.py your_audio.mp3 \
    --whisper-model base \
    --diarization-model pyannote/speaker-diarization-3.1 \
    --output-dir ./results/
```

### Method 2: Step-by-Step Process

1. **Speaker Diarization:**

```bash
python speaker_diarization.py audio_file.mp3 --output diarization.json
```

2. **Extract Audio Segments:**

```bash
python extract_audio_segments.py audio_file.mp3 diarization.json --output-dir segments/
```

3. **Transcribe Segments:**

```bash
python audio2text_segments.py diarization_with_segments.json --output final_transcription.json
```

### Method 3: Traditional Transcription

For single-file transcription without speaker separation:

```bash
python audio2text_timestamped.py audio_file.mp3
```

## 📊 Usage Examples

### Complete Pipeline Example

```bash
# Process audio with medium Whisper model
python segmented_transcription_pipeline.py interview.mp3 \
    --whisper-model medium \
    --output-dir ./interview_results/ \
    --verbose

# Results will include:
# - Speaker diarization JSON
# - Individual audio segments
# - Final transcription with speaker labels
```

### Individual Component Examples

**Speaker Diarization:**

```bash
python speaker_diarization.py meeting.mp3 \
    --model pyannote/speaker-diarization-3.1 \
    --output meeting_speakers.json \
    --min-speakers 2 \
    --max-speakers 5
```

**Segment Transcription:**

```bash
python audio2text_segments.py meeting_with_segments.json \
    --model large-v3 \
    --language auto \
    --output final_transcript.json
```

## 🔧 Configuration Options

### Whisper Models

- `tiny`: Fastest, least accurate
- `base`: Good balance (recommended for testing)
- `small`: Better accuracy
- `medium`: High accuracy
- `large`: Best accuracy
- `large-v3`: Latest large model

### Diarization Models

- `pyannote/speaker-diarization-3.1`: Latest model (recommended)
- Custom models supported

### Output Formats

- **JSON**: Complete data with timestamps and metadata
- **SRT**: Subtitle format (traditional method only)

## 📈 Output Structure

### Segmented Transcription Output

```json
{
  "audio_file": "interview.mp3",
  "sentences": [
    {
      "start_time": 0.5,
      "end_time": 3.2,
      "speaker": "SPEAKER_00",
      "text": "Hello, welcome to our interview.",
      "segment_file_path": "interview_01_01.mp3",
      "language": "en",
      "confidence": 0.95
    }
  ],
  "processing_info": {
    "total_segments": 45,
    "successful_transcriptions": 44,
    "transcription_success_rate": 97.8,
    "whisper_model": "base",
    "detected_language": "en",
    "confidence": 0.98
  }
}
```

## 🧪 Testing

Run the test suite to verify your setup:

```bash
# Test pipeline on available audio files
python test_pipeline.py

# Test individual components
python test_segments_transcription.py
```

## 🔍 Troubleshooting

### Common Issues

1. **pyannote.audio authentication:**

   ```bash
   huggingface-cli login
   ```

2. **Missing audio files:**

   - Ensure audio files are in supported formats: MP3, WAV, M4A, MP4
   - Check file paths are correct

3. **Memory issues:**

   - Use smaller Whisper models (`tiny`, `base`)
   - Process shorter audio files
   - Reduce segment padding

4. **Low transcription accuracy:**
   - Use larger Whisper models (`medium`, `large`)
   - Ensure good audio quality
   - Check detected language matches content

### Performance Optimization

- **Fast processing**: Use `whisper_model="tiny"` and minimal padding
- **High accuracy**: Use `whisper_model="large-v3"` with quality audio
- **Balanced**: Use `whisper_model="base"` or `"medium"`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) for optimized inference
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) for speaker diarization
- [Hugging Face](https://huggingface.co/) for model hosting

## 📚 Additional Resources

- [MODEL_RECOMMENDATIONS.md](MODEL_RECOMMENDATIONS.md) - Model selection guide
- [TESTING_SOLUTION.md](TESTING_SOLUTION.md) - Testing methodology
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide

---

**💡 Pro Tip**: For best results with interviews or meetings, use the segmented pipeline with `medium` or `large` Whisper models. The speaker separation significantly improves transcription accuracy for multi-speaker content.
