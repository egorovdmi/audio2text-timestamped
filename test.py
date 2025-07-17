#!/usr/bin/env python3
"""
Test script for audio2text_timestamped.py
Creates test audio file and demonstrates script functionality
"""

import os
import json
import tempfile
from pathlib import Path

# Function to create test audio file using speech synthesis
def create_test_audio():
    """
    Create test audio file for demonstration
    Uses system say command on macOS or espeak on Linux
    """
    test_text = "Hello! This is a test audio file for speech recognition demonstration. This script converts audio to text with timestamps. It uses the Faster-Whisper library for high-accuracy speech recognition."
    
    # Create file in current directory in AIFF format (better supported by say command)
    audio_path = os.path.join(os.getcwd(), "test_audio.aiff")
    
    try:
        # Use AIFF format, which is better supported by say command
        cmd = f'say "{test_text}" -o "{audio_path}"'
        
        print(f"Executing command: {cmd}")
        result = os.system(cmd)
        
        if result == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            print(f"✅ Test audio file created: {audio_path}")
            print(f"   File size: {os.path.getsize(audio_path)} bytes")
            return audio_path
        else:
            print(f"❌ Command failed or file is empty")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return None
        
    except Exception as e:
        print(f"❌ Error creating test audio file: {e}")
        return None


def test_transcription():
    """Test transcription"""
    print("=== Speech Recognition System Test ===")
    
    # Create test audio file
    audio_path = create_test_audio()
    if not audio_path:
        print("Could not create test audio file.")
        print("For testing, use your own audio file:")
        print("python audio2text_timestamped.py your_audio.mp3")
        return
    
    try:
        # Import our module
        from audio2text_timestamped import AudioToTextConverter
        
        # Create converter
        print("Initializing Whisper model...")
        converter = AudioToTextConverter(model_size="tiny", device="auto")  # Use tiny for fast testing
        
        # Transcribe audio
        print("Transcribing audio...")
        result = converter.transcribe_audio(audio_path)
        
        # Output results
        print("\n=== Transcription Results ===")
        print(f"Detected language: {result['detected_language']}")
        print(f"Language probability: {result['language_probability']:.2f}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Number of sentences: {result['sentence_count']}")
        print(f"Number of words: {result['word_count']}")
        
        print(f"\nFull text:\n{result['full_text']}")
        
        print("\n=== Sentences with Timestamps ===")
        for i, sentence in enumerate(result['sentences'], 1):
            print(f"{i:2d}. [{sentence['start_time']:5.2f}s - {sentence['end_time']:5.2f}s] {sentence['sentence']}")
        
        # Save result
        output_path = "test_result.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\nResult saved to: {output_path}")
        
        # Delete temporary file
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Temporary file deleted: {audio_path}")
        
        print("\n✅ Test completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install faster-whisper")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        
        # Delete temporary file on error
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


def demo_command_line():
    """Demonstrate command line usage"""
    print("\n=== Command Line Usage Examples ===")
    
    examples = [
        "# Basic usage",
        "python audio2text_timestamped.py audio.mp3",
        "",
        "# With file output",
        "python audio2text_timestamped.py audio.mp3 --output result.json",
        "",
        "# With model and language selection",
        "python audio2text_timestamped.py audio.mp3 --model medium --language en",
        "",
        "# With pretty JSON formatting",
        "python audio2text_timestamped.py audio.mp3 --output result.json --pretty",
        "",
        "# Using utilities for result processing",
        "python utils.py result.json --stats",
        "python utils.py result.json --csv output.csv",
        "python utils.py result.json --srt subtitles.srt",
        "python utils.py result.json --search 'search text'"
    ]
    
    for example in examples:
        print(example)


if __name__ == "__main__":
    test_transcription()
    demo_command_line()
