#!/usr/bin/env python3
"""
Quick test for speaker diarization
Tests the module with the first available audio file
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from speaker_diarization import SpeakerDiarizer
    print("✓ Speaker diarization module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import module: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install pyannote.audio torch torchaudio huggingface_hub")
    sys.exit(1)


def find_audio_file():
    """Find the first available audio file"""
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    
    for ext in audio_extensions:
        files = list(Path('.').glob(f'*{ext}'))
        if files:
            return str(files[0])
    
    return None


def main():
    """Main test function"""
    print("Speaker Diarization Quick Test")
    print("=" * 40)
    
    # Find audio file
    audio_file = find_audio_file()
    if not audio_file:
        print("✗ No audio files found in current directory")
        print("Supported formats: .mp3, .wav, .m4a, .flac, .ogg")
        return
    
    print(f"✓ Found audio file: {audio_file}")
    
    try:
        # Test model loading
        print("\nTesting model loading...")
        diarizer = SpeakerDiarizer(device="auto", max_speakers=4, min_segment_duration=0.4, max_gap_duration=0.2)
        print("✓ Model loaded successfully")
        
        # Test processing
        print(f"\nProcessing {audio_file}...")
        results = diarizer.diarize_audio(audio_file)
        
        # Display results
        print("\n" + "=" * 40)
        print("RESULTS")
        print("=" * 40)
        print(f"File: {results['file_path']}")
        print(f"Duration: {results['duration']} seconds")
        print(f"Speakers: {results['speakers_detected']}")
        print(f"Sentences: {len(results['sentences'])}")
        
        # Show first few sentences
        print("\nFirst few sentences:")
        for i, sentence in enumerate(results['sentences'][:3]):
            print(f"  {i+1}. {sentence['start_time']:6.2f}s - {sentence['end_time']:6.2f}s "
                  f"| {sentence['speaker']} | {sentence['duration']:.2f}s")
        
        if len(results['sentences']) > 3:
            print(f"  ... and {len(results['sentences']) - 3} more sentences")
        
        # Save results
        output_file = f"quick_test_diarization.json"
        diarizer.save_results(results, output_file)
        print(f"\n✓ Results saved to: {output_file}")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\nIf this is an authentication error:")
        print("1. Run: huggingface-cli login")
        print("2. Visit: https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("3. Click 'Agree and access repository'")


if __name__ == "__main__":
    main()
