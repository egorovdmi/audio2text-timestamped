#!/usr/bin/env python3
"""
Test script for speaker diarization module
Quick test to verify the speaker diarization functionality
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from speaker_diarization import SpeakerDiarizer
except ImportError as e:
    print(f"Failed to import speaker_diarization module: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_speaker_diarization():
    """Test speaker diarization with available audio files"""
    
    # Look for audio files in current directory
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    audio_files = []
    
    current_dir = Path('.')
    for ext in audio_extensions:
        audio_files.extend(current_dir.glob(f'*{ext}'))
    
    if not audio_files:
        print("No audio files found in current directory")
        print(f"Supported formats: {', '.join(audio_extensions)}")
        return
    
    # Use the first audio file found
    test_file = str(audio_files[0])
    print(f"Testing with audio file: {test_file}")
    
    try:
        # Initialize diarizer with default settings
        print("Initializing speaker diarizer...")
        diarizer = SpeakerDiarizer(
            min_segment_duration=0.5,
            max_gap_duration=0.3
        )
        
        # Process the audio file
        print("Running speaker diarization...")
        results = diarizer.diarize_audio(test_file)
        
        # Display results
        print("\n" + "="*50)
        print("DIARIZATION RESULTS")
        print("="*50)
        print(f"File: {results['file_path']}")
        print(f"Duration: {results['duration']} seconds")
        print(f"Speakers detected: {results['speakers_detected']}")
        print(f"Total sentences: {len(results['sentences'])}")
        
        print("\nSentences:")
        print("-" * 60)
        for i, sentence in enumerate(results['sentences'], 1):
            print(f"{i:2d}. {sentence['start_time']:6.2f}s - {sentence['end_time']:6.2f}s "
                  f"({sentence['duration']:5.2f}s) | {sentence['speaker']}")
        
        # Save results
        output_file = f"{Path(test_file).stem}_diarization_test.json"
        diarizer.save_results(results, output_file)
        print(f"\nResults saved to: {output_file}")
        
        # Calculate speaker statistics
        speaker_stats = {}
        for sentence in results['sentences']:
            speaker = sentence['speaker']
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    'total_time': 0,
                    'sentence_count': 0
                }
            speaker_stats[speaker]['total_time'] += sentence['duration']
            speaker_stats[speaker]['sentence_count'] += 1
        
        print("\nSpeaker Statistics:")
        print("-" * 40)
        for speaker, stats in speaker_stats.items():
            percentage = (stats['total_time'] / results['duration']) * 100
            print(f"{speaker}: {stats['total_time']:.2f}s ({percentage:.1f}%) "
                  f"in {stats['sentence_count']} sentences")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have HuggingFace authentication setup:")
        print("   huggingface-cli login")
        print("2. Check if all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("3. Make sure you have sufficient GPU memory or use CPU:")
        print("   python speaker_diarization.py --device cpu your_audio.mp3")


if __name__ == "__main__":
    test_speaker_diarization()
