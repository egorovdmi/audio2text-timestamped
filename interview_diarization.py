#!/usr/bin/env python3
"""
Optimized speaker diarization settings for interviews and overlapping speech
Focuses on voice-based segmentation rather than silence-based
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speaker_diarization import SpeakerDiarizer


def interview_diarization(audio_file: str, expected_speakers: int = None):
    """
    Optimized diarization for interview scenarios with overlapping speech
    
    Args:
        audio_file: Path to audio file
        expected_speakers: Expected number of speakers (interviewer + interviewees)
    """
    
    print(f"Interview-optimized diarization: {audio_file}")
    print("=" * 60)
    
    # Interview-specific settings
    settings = {
        "min_segment_duration": 0.1,    # Very short segments to catch quick responses  
        "max_gap_duration": 0.05,       # Minimal merging to preserve rapid exchanges
        "device": "auto"
    }
    
    # Add speaker constraints if known
    if expected_speakers:
        if expected_speakers == 2:
            settings["num_speakers"] = 2
        else:
            settings["min_speakers"] = 2
            settings["max_speakers"] = expected_speakers + 1  # Allow some flexibility
    
    print("Interview-optimized settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        # Initialize with interview settings
        diarizer = SpeakerDiarizer(**settings)
        
        # Process audio
        print("Processing... (this may take a while for high sensitivity)")
        result = diarizer.diarize_audio(audio_file)
        
        # Analyze results for interview patterns
        sentences = result["sentences"]
        speakers = set(sen["speaker"] for sen in sentences)
        
        print(f"Raw results:")
        print(f"  Speakers detected: {len(speakers)}")
        print(f"  Total sentences: {len(sentences)}")
        
        # Analyze overlapping sentences (common in interviews)
        overlaps = []
        for i in range(len(sentences) - 1):
            current = sentences[i]
            next_sen = sentences[i + 1]
            
            if current["end_time"] > next_sen["start_time"]:
                overlap_duration = current["end_time"] - next_sen["start_time"]
                overlaps.append({
                    "sentence1": i,
                    "sentence2": i + 1,
                    "overlap_duration": round(overlap_duration, 2),
                    "speaker1": current["speaker"],
                    "speaker2": next_sen["speaker"]
                })
        
        print(f"  Overlapping sentences: {len(overlaps)}")
        
        # Show first few overlaps (typical for interviews)
        if overlaps:
            print("\nFirst few overlapping sentences (typical in interviews):")
            for i, overlap in enumerate(overlaps[:5]):
                s1_start = sentences[overlap["sentence1"]]["start_time"]
                s1_end = sentences[overlap["sentence1"]]["end_time"]
                s2_start = sentences[overlap["sentence2"]]["start_time"]
                s2_end = sentences[overlap["sentence2"]]["end_time"]
                
                print(f"  {i+1}. {s1_start:.2f}-{s1_end:.2f}s ({overlap['speaker1']}) overlaps with")
                print(f"     {s2_start:.2f}-{s2_end:.2f}s ({overlap['speaker2']}) by {overlap['overlap_duration']:.2f}s")
        
        # Calculate speaker statistics
        speaker_stats = {}
        for sentence in sentences:
            speaker = sentence["speaker"]
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "total_time": 0,
                    "sentence_count": 0,
                    "avg_sentence_duration": 0
                }
            speaker_stats[speaker]["total_time"] += sentence["duration"]
            speaker_stats[speaker]["sentence_count"] += 1
        
        # Calculate averages
        for speaker in speaker_stats:
            stats = speaker_stats[speaker]
            stats["avg_sentence_duration"] = round(stats["total_time"] / stats["sentence_count"], 2)
            stats["speech_percentage"] = round((stats["total_time"] / result["duration"]) * 100, 1)
        
        print(f"\nSpeaker statistics:")
        print(f"{'Speaker':<12} {'Time (s)':<8} {'%':<6} {'Sentences':<9} {'Avg Duration':<12}")
        print("-" * 60)
        
        # Sort by speaking time (interviewer usually speaks less)
        sorted_speakers = sorted(speaker_stats.items(), key=lambda x: x[1]["total_time"], reverse=True)
        
        for speaker, stats in sorted_speakers:
            print(f"{speaker:<12} {stats['total_time']:<8.1f} {stats['speech_percentage']:<6.1f} "
                  f"{stats['sentence_count']:<9} {stats['avg_sentence_duration']:<12.2f}")
        
        # Interview analysis
        print(f"\nInterview Analysis:")
        if len(sorted_speakers) >= 2:
            main_speaker = sorted_speakers[0]
            secondary_speaker = sorted_speakers[1]
            
            ratio = main_speaker[1]["total_time"] / secondary_speaker[1]["total_time"]
            if ratio > 2:
                print(f"  🎤 Likely interviewer: {secondary_speaker[0]} (speaks less)")
                print(f"  🗣️  Likely interviewee: {main_speaker[0]} (speaks more)")
            else:
                print(f"  💬 Balanced conversation between {main_speaker[0]} and {secondary_speaker[0]}")
        
        if overlaps:
            overlap_rate = len(overlaps) / len(sentences) * 100
            print(f"  🔄 Overlap rate: {overlap_rate:.1f}% (higher = more interruptions/quick exchanges)")
        
        # Save results
        output_file = f"interview_diarization_{Path(audio_file).stem}.json"
        
        # Add analysis to results
        result["interview_analysis"] = {
            "overlapping_sentences": len(overlaps),
            "overlap_rate_percent": round(len(overlaps) / len(sentences) * 100, 1) if sentences else 0,
            "speaker_stats": speaker_stats
        }
        
        diarizer.save_results(result, output_file)
        print(f"\n💾 Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python interview_diarization.py <audio_file> [expected_speakers]")
        print("Example: python interview_diarization.py interview.mp3 2")
        return
    
    audio_file = sys.argv[1]
    expected_speakers = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    
    interview_diarization(audio_file, expected_speakers)


if __name__ == "__main__":
    main()
