#!/usr/bin/env python3
"""
Audio Segment Extractor
Extracts audio segments based on speaker diarization results
Creates individual audio files for each speaker segment
"""

import json
import argparse
import os
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path

try:
    import torchaudio
    import torch
except ImportError as e:
    print(f"Error: Required dependencies not installed. Please install with:")
    print("pip install torch torchaudio")
    print(f"Missing: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioSegmentExtractor:
    """Extract audio segments based on diarization results"""
    
    def __init__(self, padding: float = 0.1):
        """
        Initialize the audio segment extractor
        
        Args:
            padding: Padding to add before/after each segment (seconds)
        """
        self.padding = padding
    
    def extract_segments(self, audio_file: str, diarization_file: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Extract audio segments based on diarization results
        
        Args:
            audio_file: Path to original audio file
            diarization_file: Path to diarization JSON file
            output_dir: Directory to save segments (default: same as audio file)
            
        Returns:
            Dictionary with extraction results
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        if not os.path.exists(diarization_file):
            raise FileNotFoundError(f"Diarization file not found: {diarization_file}")
        
        # Load diarization results
        with open(diarization_file, 'r', encoding='utf-8') as f:
            diarization_data = json.load(f)
        
        if "sentences" not in diarization_data:
            raise ValueError("Invalid diarization file: missing 'sentences' field")
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.dirname(audio_file)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load audio
        logger.info(f"Loading audio file: {audio_file}")
        waveform, sample_rate = torchaudio.load(audio_file)
        
        # Get base filename
        base_name = Path(audio_file).stem
        
        segments = diarization_data["sentences"]
        total_segments = len(segments)
        
        logger.info(f"Extracting {total_segments} segments to: {output_dir}")
        
        # Extract each segment
        extracted_segments = []
        successful_extractions = 0
        
        for i, segment in enumerate(segments, 1):
            try:
                start_time = segment["start_time"]
                end_time = segment["end_time"]
                speaker = segment["speaker"]
                
                # Add padding
                padded_start = max(0, start_time - self.padding)
                padded_end = min(waveform.shape[1] / sample_rate, end_time + self.padding)
                
                # Convert to samples
                start_sample = int(padded_start * sample_rate)
                end_sample = int(padded_end * sample_rate)
                
                # Extract segment
                segment_waveform = waveform[:, start_sample:end_sample]
                
                # Generate output filename
                segment_filename = f"{base_name}_{i:02d}_{i:02d}.mp3"
                segment_path = os.path.join(output_dir, segment_filename)
                
                # Save segment
                torchaudio.save(segment_path, segment_waveform, sample_rate)
                
                # Update segment info
                updated_segment = {
                    **segment,
                    "segment_file_path": segment_filename
                }
                extracted_segments.append(updated_segment)
                successful_extractions += 1
                
                logger.info(f"Extracted segment {i}/{total_segments}: {segment_filename}")
                
            except Exception as e:
                logger.error(f"Failed to extract segment {i}: {e}")
                # Add segment without file path
                extracted_segments.append(segment)
        
        # Create updated diarization data with segment file paths
        updated_diarization = {
            **diarization_data,
            "sentences": extracted_segments,
            "processing_info": {
                **diarization_data.get("processing_info", {}),
                "total_segments": total_segments,
                "segments_created": successful_extractions,
                "extraction_success_rate": round((successful_extractions / total_segments) * 100, 1) if total_segments > 0 else 0.0,
                "output_directory": output_dir,
                "padding_seconds": self.padding,
                "processed_at": __import__('datetime').datetime.now().isoformat() + "Z"
            }
        }
        
        logger.info(f"Extraction completed. Success rate: {updated_diarization['processing_info']['extraction_success_rate']}%")
        return updated_diarization
    
    def save_updated_diarization(self, updated_data: Dict[str, Any], output_file: str):
        """Save updated diarization data with segment file paths"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated diarization saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save updated diarization: {e}")
            raise


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Audio Segment Extraction Tool")
    
    parser.add_argument("audio_file", help="Path to original audio file")
    parser.add_argument("diarization_file", help="Path to diarization JSON file")
    parser.add_argument("-o", "--output-dir", help="Output directory for segments (default: same as audio file)")
    parser.add_argument("--updated-diarization", help="Output file for updated diarization JSON (default: auto-generated)")
    parser.add_argument("--padding", type=float, default=0.1,
                       help="Padding to add before/after each segment in seconds (default: 0.1)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Generate output filename for updated diarization if not provided
    if not args.updated_diarization:
        diarization_path = Path(args.diarization_file)
        args.updated_diarization = diarization_path.with_name(f"{diarization_path.stem}_with_segments.json")
    
    try:
        # Initialize extractor
        extractor = AudioSegmentExtractor(padding=args.padding)
        
        # Extract segments
        updated_data = extractor.extract_segments(
            args.audio_file, 
            args.diarization_file, 
            args.output_dir
        )
        
        # Save updated diarization data
        extractor.save_updated_diarization(updated_data, args.updated_diarization)
        
        # Print summary
        processing_info = updated_data.get("processing_info", {})
        print(f"\nSegment Extraction Results:")
        print(f"Audio file: {args.audio_file}")
        print(f"Total segments: {processing_info.get('total_segments', 0)}")
        print(f"Segments created: {processing_info.get('segments_created', 0)}")
        print(f"Success rate: {processing_info.get('extraction_success_rate', 0)}%")
        print(f"Output directory: {processing_info.get('output_directory', 'unknown')}")
        print(f"Updated diarization: {args.updated_diarization}")
        
        if processing_info.get('segments_created', 0) > 0:
            print(f"\n✅ Extraction completed successfully!")
            print(f"You can now run transcription with:")
            print(f"python audio2text_segments.py {args.updated_diarization}")
        else:
            print(f"\n❌ No segments were extracted!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
