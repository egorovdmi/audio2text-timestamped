#!/usr/bin/env python3
"""
Example usage of audio2text_timestamped.py
"""

from audio2text_timestamped import AudioToTextConverter
import json

def example_usage():
    """Example of programmatic usage"""
    
    # Create converter with base model
    converter = AudioToTextConverter(model_size="base", device="auto")
    
    # Path to audio file (replace with actual path)
    audio_path = "example_audio.mp3"
    
    try:
        # Transcribe audio
        result = converter.transcribe_audio(audio_path)
        
        # Output results
        print("=== Transcription Results ===")
        print(f"File: {result['file_path']}")
        print(f"Language: {result['detected_language']} (probability: {result['language_probability']})")
        print(f"Duration: {result['duration']} seconds")
        print(f"Sentences: {result['sentence_count']}")
        print(f"Words: {result['word_count']}")
        print()
        
        print("=== Full Text ===")
        print(result['full_text'])
        print()
        
        print("=== Sentences with Timestamps ===")
        for i, sentence in enumerate(result['sentences'], 1):
            print(f"{i:2d}. [{sentence['start_time']:6.2f}s - {sentence['end_time']:6.2f}s] {sentence['sentence']}")
        
        # Save to JSON
        output_path = "transcription_result.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResult saved to: {output_path}")
        
    except FileNotFoundError:
        print(f"Error: File {audio_path} not found.")
        print("Please replace 'example_audio.mp3' with path to actual audio file.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    example_usage()
