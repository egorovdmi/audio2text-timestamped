#!/usr/bin/env python3
"""
Speaker Diarization Module
Analyzes audio files to identify different speakers and their speaking intervals
Uses pyannote/speaker-diarization-3.1 model
"""

import json
import argparse
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings

# Suppress warnings from pyannote
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import torch
    import torchaudio
    from pyannote.audio import Pipeline
    from pyannote.core import Annotation
except ImportError as e:
    print(f"Error: Required dependencies not installed. Please install with:")
    print("pip install pyannote.audio torch torchaudio")
    print(f"Missing: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpeakerDiarizer:
    """Main class for speaker diarization using pyannote.audio"""
    
    def __init__(self, 
                 model_name: str = "pyannote/speaker-diarization-3.1",
                 device: str = "auto",
                 min_segment_duration: float = 0.5,
                 max_gap_duration: float = 0.3,
                 num_speakers: Optional[int] = None,
                 min_speakers: Optional[int] = None,
                 max_speakers: Optional[int] = None):
        """
        Initialize the speaker diarizer
        
        Args:
            model_name: Pyannote model name
            device: Device to use (auto, cpu, cuda, mps)
            min_segment_duration: Minimum duration for a speech segment (seconds)
            max_gap_duration: Maximum gap to merge adjacent segments (seconds)
            num_speakers: Exact number of speakers (if known)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.min_segment_duration = min_segment_duration
        self.max_gap_duration = max_gap_duration
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.pipeline: Optional[Pipeline] = None
        self._load_pipeline()
    
    def _get_device(self, device: str) -> str:
        """Determine the best device to use"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon GPU
            else:
                return "cpu"
        return device
    
    def _load_pipeline(self):
        """Load the pyannote speaker diarization pipeline"""
        try:
            logger.info(f"Loading speaker diarization model: {self.model_name}")
            logger.info(f"Using device: {self.device}")
            
            # Try to load from local cache first, then from HuggingFace Hub
            try:
                # First attempt: load from local cache without authentication
                logger.info("Attempting to load from local cache...")
                self.pipeline = Pipeline.from_pretrained(
                    self.model_name,
                    use_auth_token=False,
                    local_files_only=True
                )
                logger.info("Model loaded from local cache")
                
            except Exception as cache_error:
                logger.info("Model not found in local cache, downloading from HuggingFace Hub...")
                logger.info("This requires authentication and internet connection")
                
                # Second attempt: download from HuggingFace Hub with authentication
                try:
                    auth_token = self._get_auth_token()
                    
                    # Suppress the authentication warning by capturing stderr temporarily
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.pipeline = Pipeline.from_pretrained(
                            self.model_name,
                            use_auth_token=auth_token
                        )
                    
                    logger.info("Model downloaded and cached locally for future use")
                    
                except Exception as download_error:
                    logger.error(f"Failed to download model: {download_error}")
                    raise download_error
            
            # Move to device if not CPU
            if self.device != "cpu":
                self.pipeline = self.pipeline.to(torch.device(self.device))
            
            logger.info("Speaker diarization model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.error("\nTroubleshooting:")
            logger.error("1. Authenticate with HuggingFace:")
            logger.error("   huggingface-cli login")
            logger.error("2. Accept the model license at:")
            logger.error(f"   https://huggingface.co/{self.model_name}")
            logger.error("   Click 'Agree and access repository'")
            logger.error("3. Make sure you have access to gated models")
            raise
    
    def _get_auth_token(self):
        """Get HuggingFace authentication token"""
        try:
            # Try to get token from huggingface_hub
            from huggingface_hub import HfApi
            api = HfApi()
            # This will use the stored token from huggingface-cli login
            return True  # Let huggingface_hub handle the token automatically
        except Exception:
            # Fallback: try environment variable
            import os
            token = os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
            if token:
                return token
            else:
                return True  # Let the library handle it
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio file duration in seconds"""
        try:
            waveform, sample_rate = torchaudio.load(audio_file)
            duration = waveform.shape[1] / sample_rate
            return float(duration)
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            return 0.0
    
    def _post_process_segments(self, diarization: Annotation) -> List[Dict[str, Any]]:
        """
        Post-process diarization results
        - Filter short segments
        - Merge close segments from same speaker
        - Convert to our JSON format
        """
        segments = []
        
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            start_time = float(segment.start)
            end_time = float(segment.end)
            duration = end_time - start_time
            
            # Filter out very short segments
            if duration < self.min_segment_duration:
                continue
            
            segments.append({
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "duration": round(duration, 2),
                "speaker": str(speaker)
            })
        
        # Sort by start time
        segments.sort(key=lambda x: x["start_time"])
        
        # Merge close segments from same speaker
        merged_segments = self._merge_close_segments(segments)
        
        return merged_segments
    
    def _merge_close_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge segments from same speaker that are close together"""
        if not segments:
            return segments
        
        merged = [segments[0]]
        
        for current in segments[1:]:
            last = merged[-1]
            
            # Check if same speaker and gap is small
            gap = current["start_time"] - last["end_time"]
            if (current["speaker"] == last["speaker"] and 
                gap <= self.max_gap_duration):
                
                # Merge segments
                last["end_time"] = current["end_time"]
                last["duration"] = round(last["end_time"] - last["start_time"], 2)
                # Update sentence to reflect merged segment
                last["sentence"] = f"[Speaker {last['speaker']}]"
            else:
                merged.append(current)
        
        return merged
    
    def diarize_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with diarization results
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        if self.pipeline is None:
            raise RuntimeError("Pipeline not loaded. Call _load_pipeline() first.")
        
        logger.info(f"Processing audio file: {audio_file}")
        
        # Get audio duration
        duration = self._get_audio_duration(audio_file)
        logger.info(f"Audio duration: {duration:.2f} seconds")
        
        # Prepare diarization parameters
        diarization_params = {}
        
        if self.num_speakers is not None:
            diarization_params['num_speakers'] = self.num_speakers
            logger.info(f"Using fixed number of speakers: {self.num_speakers}")
        else:
            if self.min_speakers is not None:
                diarization_params['min_speakers'] = self.min_speakers
                logger.info(f"Minimum speakers constraint: {self.min_speakers}")
            if self.max_speakers is not None:
                diarization_params['max_speakers'] = self.max_speakers
                logger.info(f"Maximum speakers constraint: {self.max_speakers}")
        
        # Run diarization
        try:
            if diarization_params:
                diarization = self.pipeline(audio_file, **diarization_params)
            else:
                diarization = self.pipeline(audio_file)
            
            # Post-process results
            segments = self._post_process_segments(diarization)
            
            # Count unique speakers
            speakers = set(seg["speaker"] for seg in segments)
            speakers_detected = len(speakers)
            
            result = {
                "file_path": os.path.basename(audio_file),
                "duration": round(duration, 2),
                "speakers_detected": speakers_detected,
                "sentence_count": len(segments),  # Add sentence count for compatibility
                "sentences": segments
            }
            
            # Add speaker constraints info if used
            if diarization_params:
                result["diarization_params"] = diarization_params
            
            logger.info(f"Diarization completed. Found {speakers_detected} speakers in {len(segments)} sentences")
            return result
            
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            raise
    
    @staticmethod
    def get_cache_info():
        """Get information about HuggingFace cache location and size"""
        try:
            from huggingface_hub import scan_cache_dir
            
            cache_info = scan_cache_dir()
            cache_size_gb = cache_info.size_on_disk / (1024 ** 3)
            
            print(f"HuggingFace Cache Location: {cache_info.cache_dir}")
            print(f"Total Cache Size: {cache_size_gb:.2f} GB")
            print(f"Number of repos: {len(cache_info.repos)}")
            
            # Look for pyannote models in cache
            pyannote_models = []
            for repo in cache_info.repos:
                if 'pyannote' in repo.repo_id:
                    size_mb = repo.size_on_disk / (1024 ** 2)
                    pyannote_models.append(f"  - {repo.repo_id}: {size_mb:.1f} MB")
            
            if pyannote_models:
                print("\nCached Pyannote Models:")
                for model in pyannote_models:
                    print(model)
            else:
                print("\nNo Pyannote models found in cache")
                
            return cache_info
            
        except ImportError:
            print("Install huggingface_hub to check cache: pip install huggingface_hub")
            return None
        except Exception as e:
            print(f"Error checking cache: {e}")
            return None
    
    @staticmethod
    def clear_cache():
        """Clear HuggingFace cache (use with caution!)"""
        try:
            from huggingface_hub import scan_cache_dir
            
            cache_info = scan_cache_dir()
            print(f"Cache location: {cache_info.cache_dir}")
            print("Warning: This will delete all cached models!")
            
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() == 'yes':
                cache_info.delete_revisions().execute()
                print("Cache cleared successfully")
            else:
                print("Cache clear cancelled")
                
        except ImportError:
            print("Install huggingface_hub to clear cache: pip install huggingface_hub")
        except Exception as e:
            print(f"Error clearing cache: {e}")

    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save diarization results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Speaker Diarization Tool")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Diarization command (default)
    diarize_parser = subparsers.add_parser('diarize', help='Run speaker diarization')
    diarize_parser.add_argument("audio_file", help="Path to audio file")
    diarize_parser.add_argument("-o", "--output", help="Output JSON file (default: auto-generated)")
    diarize_parser.add_argument("--model", default="pyannote/speaker-diarization-3.1", 
                               help="Pyannote model name")
    diarize_parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "mps"],
                               help="Device to use")
    diarize_parser.add_argument("--min-duration", type=float, default=0.5,
                               help="Minimum segment duration in seconds")
    diarize_parser.add_argument("--max-gap", type=float, default=0.3,
                               help="Maximum gap to merge segments in seconds")
    diarize_parser.add_argument("--num-speakers", type=int,
                               help="Exact number of speakers (if known)")
    diarize_parser.add_argument("--min-speakers", type=int,
                               help="Minimum number of speakers")
    diarize_parser.add_argument("--max-speakers", type=int,
                               help="Maximum number of speakers")
    diarize_parser.add_argument("--verbose", "-v", action="store_true",
                               help="Enable verbose logging")
    
    # Cache management commands
    cache_parser = subparsers.add_parser('cache', help='Manage model cache')
    cache_subparsers = cache_parser.add_subparsers(dest='cache_command')
    
    cache_subparsers.add_parser('info', help='Show cache information')
    cache_subparsers.add_parser('clear', help='Clear model cache')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, assume diarization with first argument as audio file
    if args.command is None:
        # Handle legacy usage: python speaker_diarization.py audio_file.mp3
        if len(sys.argv) >= 2 and not sys.argv[1].startswith('-'):
            args.command = 'diarize'
            args.audio_file = sys.argv[1]
            args.output = None
            args.model = "pyannote/speaker-diarization-3.1"
            args.device = "auto"
            args.min_duration = 0.5
            args.max_gap = 0.3
            args.num_speakers = None
            args.min_speakers = None
            args.max_speakers = None
            args.verbose = False
        else:
            parser.print_help()
            return
    
    # Handle cache commands
    if args.command == 'cache':
        if args.cache_command == 'info':
            SpeakerDiarizer.get_cache_info()
        elif args.cache_command == 'clear':
            SpeakerDiarizer.clear_cache()
        else:
            cache_parser.print_help()
        return
    
    # Handle diarization command
    if args.command == 'diarize':
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Generate output filename if not provided
        if not args.output:
            audio_path = Path(args.audio_file)
            args.output = audio_path.with_suffix('.diarization.json')
        
        try:
            # Initialize diarizer
            diarizer = SpeakerDiarizer(
                model_name=args.model,
                device=args.device,
                min_segment_duration=args.min_duration,
                max_gap_duration=args.max_gap,
                num_speakers=args.num_speakers,
                min_speakers=args.min_speakers,
                max_speakers=args.max_speakers
            )
            
            # Process audio
            results = diarizer.diarize_audio(args.audio_file)
            
            # Save results
            diarizer.save_results(results, args.output)
            
            # Print summary
            print(f"\nDiarization Results:")
            print(f"File: {results['file_path']}")
            print(f"Duration: {results['duration']} seconds")
            print(f"Speakers detected: {results['speakers_detected']}")
            print(f"Sentences: {len(results['sentences'])}")
            print(f"Output saved to: {args.output}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            exit(1)


if __name__ == "__main__":
    main()
