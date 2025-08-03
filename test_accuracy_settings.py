#!/usr/bin/env python3
"""
Test speaker diarization with different accuracy settings
Compares results with various parameters to find optimal settings
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speaker_diarization import SpeakerDiarizer


def test_accuracy_settings(audio_file: str):
    """Test different accuracy settings"""
    
    print(f"Testing accuracy settings with: {audio_file}")
    print("=" * 60)
    
    # Different test configurations
    test_configs = [
        {
            "name": "Default Settings",
            "params": {
                "min_segment_duration": 0.5,
                "max_gap_duration": 0.3
            }
        },
        {
            "name": "High Sensitivity (Short Segments)",
            "params": {
                "min_segment_duration": 0.2,  # Shorter minimum segments
                "max_gap_duration": 0.1       # Less merging
            }
        },
        {
            "name": "Conservative (Long Segments)",
            "params": {
                "min_segment_duration": 1.0,  # Longer minimum segments
                "max_gap_duration": 0.5       # More merging
            }
        },
        {
            "name": "Constrained to 2 Speakers",
            "params": {
                "min_segment_duration": 0.5,
                "max_gap_duration": 0.3,
                "min_speakers": 2,
                "max_speakers": 2
            }
        },
        {
            "name": "Very High Sensitivity",
            "params": {
                "min_segment_duration": 0.1,  # Very short segments
                "max_gap_duration": 0.05      # Minimal merging
            }
        }
    ]
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}. Testing: {config['name']}")
        print("-" * 40)
        
        try:
            # Create diarizer with specific settings
            diarizer = SpeakerDiarizer(
                device="auto",
                **config["params"]
            )
            
            # Run diarization
            result = diarizer.diarize_audio(audio_file)
            
            # Calculate statistics
            speakers_count = result["speakers_detected"]
            sentences_count = len(result["sentences"])
            
            # Calculate average sentence duration
            if sentences_count > 0:
                avg_duration = sum(sen["duration"] for sen in result["sentences"]) / sentences_count
                min_duration = min(sen["duration"] for sen in result["sentences"])
                max_duration = max(sen["duration"] for sen in result["sentences"])
            else:
                avg_duration = min_duration = max_duration = 0
            
            # Check for overlapping sentences (potential issue)
            overlaps = 0
            for j in range(len(result["sentences"]) - 1):
                current = result["sentences"][j]
                next_sen = result["sentences"][j + 1]
                if current["end_time"] > next_sen["start_time"]:
                    overlaps += 1
            
            stats = {
                "config": config["name"],
                "speakers": speakers_count,
                "sentences": sentences_count,
                "avg_duration": round(avg_duration, 2),
                "min_duration": round(min_duration, 2),
                "max_duration": round(max_duration, 2),
                "overlaps": overlaps,
                "params": config["params"]
            }
            
            results.append(stats)
            
            # Print summary
            print(f"  Speakers detected: {speakers_count}")
            print(f"  Total sentences: {sentences_count}")
            print(f"  Avg sentence duration: {avg_duration:.2f}s")
            print(f"  Duration range: {min_duration:.2f}s - {max_duration:.2f}s")
            print(f"  Overlapping sentences: {overlaps}")
            
            # Save detailed results
            output_file = f"accuracy_test_{i}_{config['name'].lower().replace(' ', '_')}.json"
            diarizer.save_results(result, output_file)
            print(f"  Saved to: {output_file}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append({
                "config": config["name"],
                "error": str(e),
                "params": config["params"]
            })
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    print(f"{'Configuration':<30} {'Speakers':<9} {'Sentences':<9} {'Avg Dur':<8} {'Overlaps':<8}")
    print("-" * 70)
    
    for result in results:
        if "error" not in result:
            print(f"{result['config']:<30} {result['speakers']:<9} {result['sentences']:<9} "
                  f"{result['avg_duration']:<8} {result['overlaps']:<8}")
        else:
            print(f"{result['config']:<30} {'ERROR':<9}")
    
    # Recommendations
    print(f"\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if results:
        # Find configuration with most sentences (potentially most detailed)
        valid_results = [r for r in results if "error" not in r]
        if valid_results:
            most_detailed = max(valid_results, key=lambda x: x["sentences"])
            least_overlaps = min(valid_results, key=lambda x: x["overlaps"])
            
            print(f"🔍 Most detailed segmentation: {most_detailed['config']}")
            print(f"   - {most_detailed['sentences']} sentences, {most_detailed['speakers']} speakers")
            
            print(f"🎯 Least overlapping sentences: {least_overlaps['config']}")
            print(f"   - {least_overlaps['overlaps']} overlaps, {least_overlaps['sentences']} sentences")
            
            print(f"\n💡 For your use case:")
            print(f"   - If you want to catch all speech: use High Sensitivity settings")
            print(f"   - If you want clean, non-overlapping sentences: use Conservative settings")
            print(f"   - If you know approximate speaker count: use constraints")


def main():
    """Main function"""
    # Find audio file
    audio_files = list(Path('.').glob('*.mp3')) + list(Path('.').glob('*.wav'))
    
    if not audio_files:
        print("No audio files found. Add some .mp3 or .wav files to test.")
        return
    
    # Use command line argument or first found file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = str(audio_files[0])
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    
    test_accuracy_settings(audio_file)


if __name__ == "__main__":
    main()
