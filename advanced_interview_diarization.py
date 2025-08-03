#!/usr/bin/env pytdef resolve_overlapping_sentences(sentences: List[Dict[str, Any]], 
                                max_overlap: float = 0.1) -> List[Dict[str, Any]]:
    """
    Post-process overlapping sentences to create cleaner timeline
    
    Args:
        sentences: List of speaker sentences"
Advanced techniques for handling overlapping speech in interviews
Combines multiple approaches for maximum accuracy
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speaker_diarization import SpeakerDiarizer


def resolve_overlapping_sentences(sentences: List[Dict[str, Any]], 
                                min_overlap_duration: float = 0.1) -> List[Dict[str, Any]]:
    """
    Post-process overlapping sentences to create cleaner timeline
    
    Args:
        sentences: List of speaker sentences
        min_overlap_duration: Minimum overlap to consider significant
        
    Returns:
        Processed sentences with resolved overlaps
    """
    
    if not sentences:
        return sentences
    
    # Sort by start time
    sentences = sorted(sentences, key=lambda x: x["start_time"])
    
    resolved_sentences = []
    
    for i, current in enumerate(sentences):
        # Check for overlaps with previous sentences
        overlaps_resolved = False
        
        for j, previous in enumerate(resolved_sentences):
            # Check if current sentence overlaps with previous
            if (current["start_time"] < previous["end_time"] and 
                current["end_time"] > previous["start_time"]):
                
                overlap_duration = min(current["end_time"], previous["end_time"]) - max(current["start_time"], previous["start_time"])
                
                if overlap_duration >= min_overlap_duration:
                    # Significant overlap found
                    if current["speaker"] == previous["speaker"]:
                        # Same speaker - merge segments
                        resolved_segments[j] = {
                            "start_time": min(current["start_time"], previous["start_time"]),
                            "end_time": max(current["end_time"], previous["end_time"]),
                            "speaker": current["speaker"]
                        }
                        resolved_segments[j]["duration"] = round(
                            resolved_segments[j]["end_time"] - resolved_segments[j]["start_time"], 2
                        )
                        overlaps_resolved = True
                        break
                    else:
                        # Different speakers - split at midpoint or keep both
                        overlap_midpoint = (max(current["start_time"], previous["start_time"]) + 
                                          min(current["end_time"], previous["end_time"])) / 2
                        
                        # Adjust boundaries
                        if current["start_time"] < overlap_midpoint < current["end_time"]:
                            current_adjusted = {
                                "start_time": overlap_midpoint,
                                "end_time": current["end_time"],
                                "speaker": current["speaker"]
                            }
                            current_adjusted["duration"] = round(
                                current_adjusted["end_time"] - current_adjusted["start_time"], 2
                            )
                            
                            # Only add if duration is significant
                            if current_adjusted["duration"] >= 0.1:
                                resolved_segments.append(current_adjusted)
                            overlaps_resolved = True
                            break
        
        if not overlaps_resolved:
            resolved_segments.append(current)
    
    return sorted(resolved_segments, key=lambda x: x["start_time"])


def create_interview_timeline(sentences: List[Dict[str, Any]], 
                            total_duration: float) -> List[Dict[str, Any]]:
    """
    Create a clean timeline for interview with speaker changes
    
    Args:
        sentences: Speaker sentences
        total_duration: Total audio duration
        
    Returns:
        Clean timeline with speaker changes
    """
    
    if not sentences:
        return []
    
    timeline = []
    current_time = 0.0
    
    # Resolve overlaps first
    clean_sentences = resolve_overlapping_sentences(sentences)
    
    for sentence in clean_sentences:
        # Add silence/gap if needed
        if sentence["start_time"] > current_time + 0.1:  # Gap larger than 100ms
            timeline.append({
                "start_time": current_time,
                "end_time": sentence["start_time"],
                "duration": round(sentence["start_time"] - current_time, 2),
                "speaker": "SILENCE",
                "type": "gap"
            })
        
        # Add speaker sentence
        timeline.append({
            "start_time": sentence["start_time"],
            "end_time": sentence["end_time"],
            "duration": sentence["duration"],
            "speaker": sentence["speaker"],
            "type": "speech"
        })
        
        current_time = sentence["end_time"]
    
    # Add final silence if needed
    if current_time < total_duration - 0.1:
        timeline.append({
            "start_time": current_time,
            "end_time": total_duration,
            "duration": round(total_duration - current_time, 2),
            "speaker": "SILENCE",
            "type": "gap"
        })
    
    return timeline


def advanced_interview_diarization(audio_file: str, expected_speakers: int = 2):
    """
    Advanced interview diarization with overlap resolution
    """
    
    print(f"Advanced Interview Diarization: {audio_file}")
    print("=" * 60)
    
    try:
        # Step 1: High sensitivity diarization
        print("Step 1: Running high-sensitivity diarization...")
        diarizer = SpeakerDiarizer(
            min_segment_duration=0.05,  # Very short segments
            max_gap_duration=0.02,      # Minimal merging
            num_speakers=expected_speakers if expected_speakers else None,
            device="auto"
        )
        
        result = diarizer.diarize_audio(audio_file)
        raw_sentences = result["sentences"]
        
        print(f"  Raw sentences: {len(raw_sentences)}")
        
        # Step 2: Resolve overlaps
        print("Step 2: Resolving overlapping sentences...")
        clean_sentences = resolve_overlapping_sentences(raw_sentences)
        
        print(f"  Clean sentences: {len(clean_sentences)}")
        print(f"  Removed/merged: {len(raw_sentences) - len(clean_sentences)} sentences")
        
        # Step 3: Create interview timeline
        print("Step 3: Creating interview timeline...")
        timeline = create_interview_timeline(clean_sentences, result["duration"])
        
        speech_sentences = [t for t in timeline if t["type"] == "speech"]
        gap_sentences = [t for t in timeline if t["type"] == "gap"]
        
        print(f"  Speech sentences: {len(speech_sentences)}")
        print(f"  Gap sentences: {len(gap_sentences)}")
        
        # Analysis
        speakers = set(sen["speaker"] for sen in speech_sentences)
        print(f"  Unique speakers: {len(speakers)}")
        
        # Create final result
        final_result = {
            "file_path": result["file_path"],
            "duration": result["duration"],
            "speakers_detected": len(speakers),
            "processing_steps": {
                "raw_segments": len(raw_segments),
                "clean_segments": len(clean_segments),
                "final_timeline": len(timeline)
            },
            "segments": clean_segments,
            "full_timeline": timeline,
            "interview_analysis": {
                "speech_segments": len(speech_segments),
                "gap_segments": len(gap_segments),
                "total_speech_time": sum(s["duration"] for s in speech_segments),
                "total_gap_time": sum(s["duration"] for s in gap_segments)
            }
        }
        
        # Save results
        output_file = f"advanced_interview_{Path(audio_file).stem}.json"
        diarizer.save_results(final_result, output_file)
        
        print(f"\n💾 Advanced results saved to: {output_file}")
        
        # Summary
        print(f"\n📊 Summary:")
        for speaker in speakers:
            speaker_time = sum(s["duration"] for s in speech_segments if s["speaker"] == speaker)
            percentage = (speaker_time / result["duration"]) * 100
            print(f"  {speaker}: {speaker_time:.1f}s ({percentage:.1f}%)")
        
        return final_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python advanced_interview.py <audio_file> [expected_speakers]")
        return
    
    audio_file = sys.argv[1]
    expected_speakers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    
    advanced_interview_diarization(audio_file, expected_speakers)


if __name__ == "__main__":
    main()
