#!/usr/bin/env python3
"""
Audio to Text with Timestamps using Faster-Whisper
Converts audio files to JSON with sentences and their timestamps
"""

import json
import argparse
import os
import re
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

try:
    from faster_whisper import WhisperModel
    from faster_whisper.transcribe import Segment
except ImportError:
    print("Error: faster-whisper not installed. Please install with: pip install faster-whisper")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioToTextConverter:
    """Main class for converting audio to text with timestamps"""
    
    def __init__(self, model_size: str = "base", device: str = "auto"):
        """
        Initialize the converter
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to use (auto, cpu, cuda)
        """
        self.model_size = model_size
        self.device = device
        self.model: Optional[WhisperModel] = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            model_sizes = {
                'tiny': '~40 MB',
                'base': '~140 MB', 
                'small': '~460 MB',
                'medium': '~1.5 GB',
                'large-v2': '~3.0 GB',
                'large-v3': '~3.1 GB'
            }
            
            model_size_info = model_sizes.get(self.model_size, 'Unknown')
            
            logger.info(f"Loading Whisper model: {self.model_size} ({model_size_info})")
            
            if self.model_size in ['large-v2', 'large-v3']:
                logger.info("⚠️  Large model detected - first download may take 10-30 minutes depending on internet speed")
                logger.info("💡 Consider using 'medium' model for faster loading with good accuracy")
            
            self.model = WhisperModel(self.model_size, device=self.device)
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            if "Connection" in str(e) or "timeout" in str(e).lower():
                logger.error("💡 Network issue detected. Try:")
                logger.error("   1. Check internet connection")
                logger.error("   2. Use smaller model: -m medium")
                logger.error("   3. Try again later")
            raise
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex patterns
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        if not text.strip():
            return []
        
        # Pattern for sentence boundaries
        # Matches periods, exclamation marks, question marks followed by space and capital letter
        # or end of string
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        
        sentences = re.split(sentence_pattern, text.strip())
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _map_sentences_to_timestamps(self, segments: List[Segment], sentences: List[str]) -> List[Dict]:
        """
        Map sentences to their corresponding timestamps
        
        Args:
            segments: Whisper segments with word-level timestamps
            sentences: List of sentences
            
        Returns:
            List of sentence dictionaries with timestamps
        """
        if not sentences:
            return []
        
        result = []
        sentence_idx = 0
        current_sentence = sentences[0] if sentences else ""
        sentence_words = current_sentence.split()
        word_idx_in_sentence = 0
        sentence_start_time = None
        sentence_end_time = None
        
        for segment in segments:
            if not hasattr(segment, 'words') or not segment.words:
                continue
                
            for word_info in segment.words:
                word = word_info.word.strip()
                
                # Skip empty words
                if not word:
                    continue
                
                # Set sentence start time
                if sentence_start_time is None:
                    sentence_start_time = word_info.start
                
                # Update sentence end time
                sentence_end_time = word_info.end
                
                # Check if we've reached the end of current sentence
                word_idx_in_sentence += 1
                
                # If we've processed all words in current sentence
                if word_idx_in_sentence >= len(sentence_words):
                    # Add current sentence to result
                    if sentence_start_time is not None and sentence_end_time is not None:
                        result.append({
                            'sentence': current_sentence,
                            'start_time': round(sentence_start_time, 2),
                            'end_time': round(sentence_end_time, 2),
                            'duration': round(sentence_end_time - sentence_start_time, 2)
                        })
                    
                    # Move to next sentence
                    sentence_idx += 1
                    if sentence_idx < len(sentences):
                        current_sentence = sentences[sentence_idx]
                        sentence_words = current_sentence.split()
                        word_idx_in_sentence = 0
                        sentence_start_time = None
                        sentence_end_time = None
                    else:
                        break
        
        # Handle any remaining sentence
        if sentence_idx < len(sentences) and sentence_start_time is not None and sentence_end_time is not None:
            result.append({
                'sentence': sentences[sentence_idx],
                'start_time': round(sentence_start_time, 2),
                'end_time': round(sentence_end_time, 2),
                'duration': round(sentence_end_time - sentence_start_time, 2)
            })
        
        return result
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional, auto-detect if None)
            
        Returns:
            Dictionary with transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        if self.model is None:
            raise RuntimeError("Model not loaded. Please initialize the converter properly.")
        
        try:
            # Transcribe with word-level timestamps
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Convert segments to list
            segments_list = list(segments)
            
            if not segments_list:
                logger.warning("No speech detected in audio file")
                return {
                    'file_path': audio_path,
                    'detected_language': info.language,
                    'language_probability': round(info.language_probability, 2),
                    'duration': round(info.duration, 2),
                    'full_text': '',
                    'sentences': [],
                    'word_count': 0,
                    'sentence_count': 0
                }
            
            # Extract full text
            full_text = ' '.join([segment.text.strip() for segment in segments_list])
            
            # Split into sentences
            sentences = self._split_into_sentences(full_text)
            
            # Map sentences to timestamps
            sentence_timestamps = self._map_sentences_to_timestamps(segments_list, sentences)
            
            # Add language detection for each sentence (using overall detected language)
            for sentence_info in sentence_timestamps:
                sentence_info['language'] = info.language
                sentence_info['language_probability'] = round(info.language_probability, 2)
            
            result = {
                'file_path': audio_path,
                'detected_language': info.language,
                'language_probability': round(info.language_probability, 2),
                'duration': round(info.duration, 2),
                'full_text': full_text,
                'sentences': sentence_timestamps,
                'word_count': len(full_text.split()),
                'sentence_count': len(sentences)
            }
            
            logger.info(f"Transcription completed: {len(sentences)} sentences, {info.language} language")
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description='Convert audio to text with timestamps')
    parser.add_argument('audio_file', help='Path to audio file')
    parser.add_argument('-o', '--output', help='Output JSON file path (optional)')
    parser.add_argument('-m', '--model', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3'],
                       help='Whisper model size: tiny(~40MB,fast), base(~140MB,default), small(~460MB), medium(~1.5GB,recommended), large-v2(~3GB), large-v3(~3.1GB,best)')
    parser.add_argument('-l', '--language', help='Language code (optional, auto-detect if not specified)')
    parser.add_argument('-d', '--device', default='auto', choices=['auto', 'cpu', 'cuda'],
                       help='Device to use (default: auto)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        exit(1)
    
    try:
        # Warn about large models
        if args.model in ['large-v2', 'large-v3']:
            print(f"⚠️  Warning: {args.model} model is very large (~3GB)")
            print("📥 First download may take 10-30 minutes")
            print("💡 For faster results, consider using 'medium' model")
            print("🔄 Loading model... (this may take a while)")
            print()
        
        # Initialize converter
        converter = AudioToTextConverter(model_size=args.model, device=args.device)
        
        # Transcribe audio
        result = converter.transcribe_audio(args.audio_file, language=args.language)
        
        # Format JSON output
        json_indent = 2 if args.pretty else None
        json_output = json.dumps(result, ensure_ascii=False, indent=json_indent)
        
        # Save to file or print to stdout
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"Results saved to: {args.output}")
        else:
            print(json_output)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
