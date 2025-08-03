#!/usr/bin/env python3
"""
Complete Audio to Segmented Transcription Pipeline
Full pipeline: Audio → Speaker Diarization → Segment Extraction → Individual Transcription
"""

import json
import argparse
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentedTranscriptionPipeline:
    """Complete pipeline for segmented audio transcription"""
    
    def __init__(self, 
                 diarization_model: str = "pyannote/speaker-diarization-3.1",
                 whisper_model: str = "base",
                 segment_padding: float = 0.1):
        """
        Initialize the pipeline
        
        Args:
            diarization_model: Speaker diarization model
            whisper_model: Whisper model size
            segment_padding: Padding for audio segments (seconds)
        """
        self.diarization_model = diarization_model
        self.whisper_model = whisper_model
        self.segment_padding = segment_padding
    
    def run_speaker_diarization(self, audio_file: str, output_file: str = None) -> str:
        """
        Run speaker diarization on audio file
        
        Args:
            audio_file: Path to audio file
            output_file: Output JSON file path
            
        Returns:
            Path to diarization results file
        """
        if output_file is None:
            audio_path = Path(audio_file)
            output_file = audio_path.with_suffix('.json')
        
        logger.info(f"Running speaker diarization...")
        logger.info(f"Input: {audio_file}")
        logger.info(f"Output: {output_file}")
        
        # Check if speaker_diarization.py exists
        diarization_script = "speaker_diarization.py"
        if not os.path.exists(diarization_script):
            raise FileNotFoundError(f"Speaker diarization script not found: {diarization_script}")
        
        # Run speaker diarization
        cmd = [
            sys.executable, diarization_script,
            "diarize",  # Add the required subcommand
            audio_file,
            "--output", str(output_file),
            "--model", self.diarization_model
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Speaker diarization completed successfully")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Speaker diarization failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def extract_audio_segments(self, audio_file: str, diarization_file: str, output_dir: str = None) -> str:
        """
        Extract audio segments based on diarization
        
        Args:
            audio_file: Original audio file
            diarization_file: Diarization results
            output_dir: Output directory for segments
            
        Returns:
            Path to updated diarization file with segment paths
        """
        if output_dir is None:
            audio_path = Path(audio_file)
            output_dir = audio_path.parent / f"{audio_path.stem}_segments"
        
        logger.info(f"Extracting audio segments...")
        logger.info(f"Audio: {audio_file}")
        logger.info(f"Diarization: {diarization_file}")
        logger.info(f"Output dir: {output_dir}")
        
        # Check if extraction script exists
        extraction_script = "extract_audio_segments.py"
        if not os.path.exists(extraction_script):
            raise FileNotFoundError(f"Audio extraction script not found: {extraction_script}")
        
        # Generate output file for updated diarization
        diarization_path = Path(diarization_file)
        updated_diarization = diarization_path.with_name(f"{diarization_path.stem}_with_segments.json")
        
        # Run segment extraction
        cmd = [
            sys.executable, extraction_script,
            audio_file,
            diarization_file,
            "--output-dir", str(output_dir),
            "--updated-diarization", str(updated_diarization),
            "--padding", str(self.segment_padding)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Audio segment extraction completed successfully")
            return str(updated_diarization)
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def run_segment_transcription(self, segments_diarization_file: str, output_file: str = None) -> str:
        """
        Run transcription on extracted segments
        
        Args:
            segments_diarization_file: Diarization file with segment paths
            output_file: Output transcription file
            
        Returns:
            Path to final transcription file
        """
        if output_file is None:
            segments_path = Path(segments_diarization_file)
            output_file = segments_path.with_name(f"{segments_path.stem}_transcribed.json")
        
        logger.info(f"Running segment transcription...")
        logger.info(f"Segments: {segments_diarization_file}")
        logger.info(f"Output: {output_file}")
        
        # Check if transcription script exists
        transcription_script = "audio2text_segments.py"
        if not os.path.exists(transcription_script):
            raise FileNotFoundError(f"Segment transcription script not found: {transcription_script}")
        
        # Run segment transcription
        cmd = [
            sys.executable, transcription_script,
            segments_diarization_file,
            "--output", str(output_file),
            "--model", self.whisper_model
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Segment transcription completed successfully")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Segment transcription failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def run_complete_pipeline(self, audio_file: str, output_dir: str = None) -> Dict[str, str]:
        """
        Run the complete pipeline
        
        Args:
            audio_file: Input audio file
            output_dir: Output directory for all results
            
        Returns:
            Dictionary with paths to all generated files
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        audio_path = Path(audio_file)
        
        if output_dir is None:
            output_dir = audio_path.parent / f"{audio_path.stem}_pipeline"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Starting complete segmented transcription pipeline")
        logger.info(f"Input audio: {audio_file}")
        logger.info(f"Output directory: {output_dir}")
        
        results = {}
        
        try:
            # Step 1: Speaker Diarization
            logger.info("=" * 60)
            logger.info("STEP 1: Speaker Diarization")
            logger.info("=" * 60)
            
            diarization_file = output_dir / f"{audio_path.stem}_diarization.json"
            results["diarization"] = self.run_speaker_diarization(audio_file, str(diarization_file))
            
            # Step 2: Audio Segment Extraction
            logger.info("=" * 60)
            logger.info("STEP 2: Audio Segment Extraction")
            logger.info("=" * 60)
            
            segments_dir = output_dir / "segments"
            segments_diarization_file = self.extract_audio_segments(
                audio_file, 
                results["diarization"], 
                str(segments_dir)
            )
            results["segments_diarization"] = segments_diarization_file
            results["segments_directory"] = str(segments_dir)
            
            # Step 3: Segment Transcription
            logger.info("=" * 60)
            logger.info("STEP 3: Segment Transcription")
            logger.info("=" * 60)
            
            transcription_file = output_dir / f"{audio_path.stem}_final_transcription.json"
            results["final_transcription"] = self.run_segment_transcription(
                segments_diarization_file, 
                str(transcription_file)
            )
            
            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed at some step: {e}")
            raise
    
    def print_results_summary(self, results: Dict[str, str]):
        """Print summary of pipeline results"""
        print(f"\n🎉 Segmented Transcription Pipeline Results:")
        print(f"=" * 50)
        
        if "diarization" in results:
            print(f"📊 Speaker Diarization: {results['diarization']}")
        
        if "segments_directory" in results:
            print(f"🔊 Audio Segments: {results['segments_directory']}")
        
        if "segments_diarization" in results:
            print(f"📋 Segments Metadata: {results['segments_diarization']}")
        
        if "final_transcription" in results:
            print(f"📝 Final Transcription: {results['final_transcription']}")
            
            # Try to load and show summary stats
            try:
                with open(results['final_transcription'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                processing_info = data.get("processing_info", {})
                print(f"\n📈 Processing Statistics:")
                print(f"   • Total segments: {processing_info.get('total_segments', 'unknown')}")
                print(f"   • Successful transcriptions: {processing_info.get('successful_transcriptions', 'unknown')}")
                print(f"   • Success rate: {processing_info.get('transcription_success_rate', 'unknown')}%")
                print(f"   • Model used: {processing_info.get('whisper_model', 'unknown')}")
                
                if "language_detection" in processing_info:
                    lang_info = processing_info["language_detection"]
                    print(f"   • Detected language: {lang_info.get('detected_language', 'unknown')} ({lang_info.get('confidence', 'unknown')}% confidence)")
                
            except Exception as e:
                logger.debug(f"Could not load transcription stats: {e}")
        
        print(f"=" * 50)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Complete Segmented Audio Transcription Pipeline")
    
    parser.add_argument("audio_file", help="Input audio file")
    parser.add_argument("-o", "--output-dir", help="Output directory for all results")
    parser.add_argument("--diarization-model", default="pyannote/speaker-diarization-3.1",
                       help="Speaker diarization model (default: pyannote/speaker-diarization-3.1)")
    parser.add_argument("--whisper-model", default="base",
                       help="Whisper model size (default: base)")
    parser.add_argument("--segment-padding", type=float, default=0.1,
                       help="Padding for audio segments in seconds (default: 0.1)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize pipeline
        pipeline = SegmentedTranscriptionPipeline(
            diarization_model=args.diarization_model,
            whisper_model=args.whisper_model,
            segment_padding=args.segment_padding
        )
        
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(args.audio_file, args.output_dir)
        
        # Print results summary
        pipeline.print_results_summary(results)
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
