#!/usr/bin/env python3
"""
Test script for audio2text_segments.py
Tests the segment-based transcription functionality
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio2text_segments import SegmentTranscriber


def test_segment_transcription():
    """Test the segment transcription functionality"""
    
    print("🎯 Testing Audio Segments Transcription")
    print("=" * 50)
    
    # Look for diarization JSON files
    test_files = [
        "quick_test_diarization.json",
        "test_about_cloud_4.diarization.json",
        "7513748408921_10min.diarization.json"
    ]
    
    diarization_file = None
    for test_file in test_files:
        if os.path.exists(test_file):
            diarization_file = test_file
            break
    
    if not diarization_file:
        print("❌ No diarization JSON file found!")
        print("Available files:")
        for f in os.listdir('.'):
            if f.endswith('.json'):
                print(f"  - {f}")
        return
    
    print(f"📁 Using diarization file: {diarization_file}")
    
    try:
        # Initialize transcriber with a small model for testing
        print("\n1. Initializing transcriber...")
        transcriber = SegmentTranscriber(
            model_name="tiny",  # Use tiny model for fast testing
            device="auto"
        )
        
        print("2. Processing segments...")
        results = transcriber.process_segments(diarization_file)
        
        print("3. Results summary:")
        print(f"   📝 File: {results['file_path']}")
        print(f"   ⏱️  Duration: {results['duration']} seconds")
        print(f"   🗣️  Speakers: {results['speakers_detected']}")
        print(f"   📊 Segments: {results['sentence_count']}")
        print(f"   📈 Success rate: {results['processing_info']['success_rate']}%")
        
        if results['word_count'] > 0:
            print(f"   📝 Words: {results['word_count']}")
            print(f"   🌍 Language: {results['detected_language']} (confidence: {results['language_probability']})")
        
        # Show first few transcribed segments
        print("\n4. First few transcribed segments:")
        transcribed_segments = [seg for seg in results['sentences'] if seg.get('sentence', '').strip()]
        
        for i, segment in enumerate(transcribed_segments[:5], 1):
            print(f"   {i}. [{segment['speaker']}] {segment['start_time']:.1f}s-{segment['end_time']:.1f}s")
            text = segment['sentence'][:100] + "..." if len(segment['sentence']) > 100 else segment['sentence']
            print(f"      \"{text}\"")
        
        if len(transcribed_segments) > 5:
            print(f"      ... and {len(transcribed_segments) - 5} more segments")
        
        # Save results
        output_file = f"test_segments_transcription.json"
        transcriber.save_results(results, output_file)
        print(f"\n5. Results saved to: {output_file}")
        
        # Show any failures
        failed_segments = [seg for seg in results['sentences'] if 'transcription_error' in seg]
        if failed_segments:
            print(f"\n⚠️  {len(failed_segments)} segments failed to transcribe:")
            for seg in failed_segments[:3]:  # Show first 3 failures
                print(f"   - {seg.get('segment_file_path', 'unknown')}: {seg.get('transcription_error', 'unknown error')}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have Whisper installed: pip install openai-whisper")
        print("2. Check that the diarization JSON file has 'segment_file_path' fields")
        print("3. Verify that the audio segment files exist")


if __name__ == "__main__":
    test_segment_transcription()
