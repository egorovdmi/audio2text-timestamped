#!/usr/bin/env python3
"""
Test Segmented Transcription Pipeline
Tests the complete pipeline on available audio files
"""

import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_test_audio_files():
    """Find audio files in current directory for testing"""
    current_dir = Path(".")
    audio_extensions = ['.mp3', '.wav', '.aiff', '.m4a', '.mp4']
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(list(current_dir.glob(f"*{ext}")))
    
    return sorted(audio_files)


def test_pipeline_on_file(audio_file: str):
    """Test the complete pipeline on a single audio file"""
    print(f"\n{'='*60}")
    print(f"TESTING PIPELINE ON: {audio_file}")
    print(f"{'='*60}")
    
    try:
        from segmented_transcription_pipeline import SegmentedTranscriptionPipeline
        
        # Initialize pipeline with small model for fast testing
        pipeline = SegmentedTranscriptionPipeline(
            whisper_model="tiny",  # Use tiny model for speed
            segment_padding=0.05   # Minimal padding for testing
        )
        
        # Run pipeline
        results = pipeline.run_complete_pipeline(audio_file)
        
        # Print results
        pipeline.print_results_summary(results)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed for {audio_file}: {e}")
        return False


def main():
    """Main test function"""
    print("🔍 Searching for audio files to test...")
    
    audio_files = find_test_audio_files()
    
    if not audio_files:
        print("❌ No audio files found in current directory")
        print("Supported formats: .mp3, .wav, .aiff, .m4a, .mp4")
        return
    
    print(f"📁 Found {len(audio_files)} audio file(s):")
    for i, file in enumerate(audio_files, 1):
        file_size = file.stat().st_size / (1024 * 1024)  # MB
        print(f"   {i}. {file.name} ({file_size:.1f} MB)")
    
    # Test on first file (or smallest file)
    test_file = min(audio_files, key=lambda f: f.stat().st_size)
    
    print(f"\n🎯 Testing pipeline on smallest file: {test_file.name}")
    
    success = test_pipeline_on_file(str(test_file))
    
    if success:
        print(f"\n✅ Pipeline test completed successfully!")
        print(f"💡 To test other files, run:")
        print(f"   python segmented_transcription_pipeline.py <audio_file>")
    else:
        print(f"\n❌ Pipeline test failed!")
        print(f"🔧 Check the error messages above for debugging")


if __name__ == "__main__":
    main()
