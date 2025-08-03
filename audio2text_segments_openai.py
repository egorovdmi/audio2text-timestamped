#!/usr/bin/env python3
"""
Audio Segment Transcription with OpenAI Whisper
Transcribes individual audio segments using OpenAI Whisper with MPS support
"""

import json
import argparse
import os
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path

try:
    import whisper
    import torch
    import torchaudio
except ImportError as e:
    print(f"Error: Required dependencies not installed. Please install with:")
    print("pip install openai-whisper torch torchaudio")
    print(f"Missing: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentTranscriberOpenAI:
    """Transcribe audio segments with OpenAI Whisper (supports MPS)"""
    
    def __init__(self, model_name: str = "base", device: str = "auto", language: str = None):
        """
        Initialize the segment transcriber
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large, large-v3)
            device: Device to use for inference ("auto", "cpu", "cuda", "mps")
            language: Language code for transcription (auto-detect if None)
        """
        self.model_name = model_name
        self.device = self._determine_device(device)
        self.language = language
        self.model = None
        
        # Load model
        self._load_model()
    
    def _determine_device(self, device: str) -> str:
        """Determine the best device to use"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info("MPS (Metal Performance Shaders) available - using Apple Silicon GPU acceleration!")
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading OpenAI Whisper model: {self.model_name}")
            logger.info(f"Using device: {self.device}")
            
            # Load OpenAI Whisper model
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("OpenAI Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _transcribe_segment(self, audio_file: str) -> Dict[str, Any]:
        """
        Transcribe a single audio segment
        
        Args:
            audio_file: Path to audio segment file
            
        Returns:
            Dictionary with transcription results
        """
        if not os.path.exists(audio_file):
            logger.warning(f"Audio file not found: {audio_file}")
            return {
                "text": "",
                "language": "unknown",
                "language_probability": 0.0,
                "error": "File not found"
            }
        
        try:
            # Transcribe the audio segment with OpenAI Whisper
            result = self.model.transcribe(
                audio_file,
                language=self.language,
                word_timestamps=False,  # We don't need word-level timestamps
                verbose=False
            )
            
            # Extract text and language info
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            # Calculate confidence from segments if available
            language_probability = 0.0
            if "segments" in result and result["segments"]:
                # Average the probability across all segments
                probs = []
                for seg in result["segments"]:
                    if "avg_logprob" in seg:
                        # Convert log probability to probability (approximate)
                        prob = min(1.0, max(0.0, (seg["avg_logprob"] + 1.0)))
                        probs.append(prob)
                if probs:
                    language_probability = sum(probs) / len(probs)
            else:
                # Fallback confidence estimation
                language_probability = 0.8 if text else 0.0
            
            return {
                "text": text,
                "language": detected_language,
                "language_probability": round(language_probability, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to transcribe {audio_file}: {e}")
            return {
                "text": "",
                "language": "unknown", 
                "language_probability": 0.0,
                "error": str(e)
            }
    
    def process_segments(self, diarization_file: str) -> Dict[str, Any]:
        """
        Process all segments from diarization results
        
        Args:
            diarization_file: Path to JSON file with diarization results
            
        Returns:
            Dictionary with complete transcription results
        """
        if not os.path.exists(diarization_file):
            raise FileNotFoundError(f"Diarization file not found: {diarization_file}")
        
        logger.info(f"Processing segments from: {diarization_file}")
        
        # Load diarization results
        try:
            with open(diarization_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load diarization file: {e}")
        
        if "sentences" not in data:
            raise ValueError("Invalid diarization file: missing 'sentences' field")
        
        segments = data["sentences"]
        total_segments = len(segments)
        base_dir = os.path.dirname(diarization_file)
        
        logger.info(f"Found {total_segments} segments to process")
        
        # Process each segment
        processed_segments = []
        successful_transcriptions = 0
        language_detections = {}
        
        for i, segment in enumerate(segments, 1):
            logger.info(f"Processing segment {i}/{total_segments}")
            
            # Get segment file path
            segment_file_path = segment.get("segment_file_path")
            if not segment_file_path:
                logger.warning(f"Segment {i} missing file path, skipping")
                processed_segments.append({
                    **segment,
                    "text": "",
                    "language": "unknown",
                    "confidence": 0.0,
                    "error": "Missing file path"
                })
                continue
            
            # Construct full path
            if not os.path.isabs(segment_file_path):
                # Look for segments directory relative to diarization file
                segments_dir = os.path.join(base_dir, "segments")
                if os.path.exists(segments_dir):
                    full_path = os.path.join(segments_dir, segment_file_path)
                else:
                    full_path = os.path.join(base_dir, segment_file_path)
            else:
                full_path = segment_file_path
            
            # Transcribe segment
            transcription_result = self._transcribe_segment(full_path)
            
            # Update segment with transcription
            updated_segment = {
                **segment,
                "text": transcription_result["text"],
                "language": transcription_result["language"],
                "confidence": transcription_result["language_probability"]
            }
            
            if "error" in transcription_result:
                updated_segment["error"] = transcription_result["error"]
            else:
                successful_transcriptions += 1
                
                # Track language detection
                detected_lang = transcription_result["language"]
                if detected_lang in language_detections:
                    language_detections[detected_lang] += 1
                else:
                    language_detections[detected_lang] = 1
            
            processed_segments.append(updated_segment)
        
        # Determine overall language
        overall_language = "unknown"
        overall_confidence = 0.0
        
        if language_detections:
            overall_language = max(language_detections, key=language_detections.get)
            total_successful = sum(language_detections.values())
            overall_confidence = round((language_detections[overall_language] / total_successful) * 100, 1)
        
        # Create result structure
        result = {
            **data,  # Include original data
            "sentences": processed_segments,
            "processing_info": {
                **data.get("processing_info", {}),
                "transcription_model": f"openai-whisper-{self.model_name}",
                "transcription_device": self.device,
                "total_segments": total_segments,
                "successful_transcriptions": successful_transcriptions,
                "transcription_success_rate": round((successful_transcriptions / total_segments) * 100, 1) if total_segments > 0 else 0.0,
                "language_detection": {
                    "detected_language": overall_language,
                    "confidence": overall_confidence,
                    "distribution": language_detections
                },
                "transcription_completed_at": __import__('datetime').datetime.now().isoformat() + "Z"
            }
        }
        
        logger.info(f"Transcription completed. Success rate: {result['processing_info']['transcription_success_rate']}%")
        logger.info(f"Detected language: {overall_language} ({overall_confidence}% confidence)")
        
        return result
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save transcription results to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Audio Segment Transcription Tool (OpenAI Whisper with MPS)")
    
    parser.add_argument("diarization_file", help="Path to diarization JSON file with segment paths")
    parser.add_argument("-o", "--output", help="Output file for transcription results")
    parser.add_argument("-m", "--model", default="base",
                       help="Whisper model size (tiny, base, small, medium, large, large-v3)")
    parser.add_argument("-l", "--language", help="Language code for transcription (auto-detect if not specified)")
    parser.add_argument("-d", "--device", default="auto",
                       help="Device to use (auto, cpu, cuda, mps)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.diarization_file)
        args.output = input_path.with_name(f"{input_path.stem}_transcribed_openai.json")
    
    try:
        # Initialize transcriber
        transcriber = SegmentTranscriberOpenAI(
            model_name=args.model,
            device=args.device,
            language=args.language
        )
        
        # Process segments
        results = transcriber.process_segments(args.diarization_file)
        
        # Save results
        transcriber.save_results(results, args.output)
        
        # Print summary
        processing_info = results.get("processing_info", {})
        print(f"\n🎉 Segment Transcription Results (OpenAI Whisper):")
        print(f"=" * 50)
        print(f"📁 Input file: {args.diarization_file}")
        print(f"📝 Output file: {args.output}")
        print(f"🤖 Model used: {processing_info.get('transcription_model', 'unknown')}")
        print(f"💻 Device used: {processing_info.get('transcription_device', 'unknown')}")
        print(f"📊 Total segments: {processing_info.get('total_segments', 0)}")
        print(f"✅ Successful transcriptions: {processing_info.get('successful_transcriptions', 0)}")
        print(f"📈 Success rate: {processing_info.get('transcription_success_rate', 0)}%")
        
        if "language_detection" in processing_info:
            lang_info = processing_info["language_detection"]
            print(f"🌍 Detected language: {lang_info.get('detected_language', 'unknown')} ({lang_info.get('confidence', 0)}% confidence)")
        
        print(f"=" * 50)
        
        if processing_info.get('successful_transcriptions', 0) > 0:
            print(f"✅ Transcription completed successfully!")
            if processing_info.get('transcription_device') == 'mps':
                print(f"🚀 Used Apple Silicon GPU acceleration (MPS)!")
        else:
            print(f"❌ No segments were successfully transcribed!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
