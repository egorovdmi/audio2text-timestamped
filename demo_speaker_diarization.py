#!/usr/bin/env python3
"""
Demo script for speaker diarization
Shows how to use the SpeakerDiarizer class programmatically
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speaker_diarization import SpeakerDiarizer


def demo_diarization():
    """Demonstrate speaker diarization functionality"""
    
    print("Speaker Diarization Demo")
    print("=" * 40)
    
    # Check for audio files
    audio_files = list(Path('.').glob('*.mp3')) + list(Path('.').glob('*.wav'))
    
    if not audio_files:
        print("No audio files found. Please add some .mp3 or .wav files to test.")
        return
    
    # Use the first available audio file
    audio_file = str(audio_files[0])
    print(f"Using audio file: {audio_file}")
    
    try:
        # Create diarizer instance
        print("\n1. Initializing speaker diarizer...")
        diarizer = SpeakerDiarizer(
            device="auto",  # Will use GPU if available
            min_segment_duration=1.0,  # Minimum 1 second segments
            max_gap_duration=0.5       # Merge segments with <0.5s gap
        )
        
        # Run diarization
        print("2. Running speaker diarization (this may take a while)...")
        results = diarizer.diarize_audio(audio_file)
        
        # Display results
        print("\n3. Results:")
        print(f"   - File: {results['file_path']}")
        print(f"   - Duration: {results['duration']} seconds")
        print(f"   - Speakers detected: {results['speakers_detected']}")
        print(f"   - Speech sentences: {len(results['sentences'])}")
        
        # Show first few sentences
        print("\n4. First few sentences:")
        for i, sentence in enumerate(results['sentences'][:5]):
            print(f"   {i+1}. {sentence['start_time']:6.2f}s - {sentence['end_time']:6.2f}s "
                  f"| {sentence['speaker']} | {sentence['duration']:.2f}s")
        
        if len(results['sentences']) > 5:
            print(f"   ... and {len(results['sentences']) - 5} more sentences")
        
        # Save results
        output_file = f"{Path(audio_file).stem}_demo_diarization.json"
        diarizer.save_results(results, output_file)
        print(f"\n5. Results saved to: {output_file}")
        
        # Show example of how to use results
        print("\n6. Example usage of results:")
        print("   for sentence in results['sentences']:")
        print("       print(f\"Speaker {sentence['speaker']} spoke from \"")
        print("             f\"{sentence['start_time']}s to {sentence['end_time']}s\")")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        print("\nPossible solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Authenticate with HuggingFace: huggingface-cli login")
        print("- Try with CPU only: add device='cpu' parameter")


if __name__ == "__main__":
    demo_diarization()
