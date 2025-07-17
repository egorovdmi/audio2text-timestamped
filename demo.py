#!/usr/bin/env python3
"""
Simple demo of audio2text_timestamped.py
"""

import json
import sys
import os
from pathlib import Path

# Add current folder to path for import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio2text_timestamped import AudioToTextConverter

def main():
    """Main function for demonstration"""
    
    print("=== Audio2Text with Timestamps Demo ===")
    print()
    
    # Check for audio file
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
    else:
        print("Usage: python demo.py <path_to_audio_file>")
        print()
        print("Example:")
        print("python demo.py audio.mp3")
        print("python demo.py audio.wav")
        print("python demo.py audio.m4a")
        return
    
    if not os.path.exists(audio_path):
        print(f"❌ Error: File '{audio_path}' not found")
        return
    
    try:
        print(f"🎵 Processing file: {audio_path}")
        print("⏳ Loading Whisper model...")
        
        # Create converter with base model
        converter = AudioToTextConverter(model_size="base", device="auto")
        
        print("🎙️ Starting transcription...")
        
        # Transcribe audio
        result = converter.transcribe_audio(audio_path)
        
        print("✅ Transcription completed!")
        print()
        
        # Output main information
        print("📊 MAIN INFORMATION:")
        print(f"   📁 File: {result['file_path']}")
        print(f"   🌐 Language: {result['detected_language']} (probability: {result['language_probability']:.2f})")
        print(f"   ⏱️ Duration: {result['duration']:.2f} seconds ({result['duration']/60:.1f} minutes)")
        print(f"   📝 Sentences: {result['sentence_count']}")
        print(f"   🔤 Words: {result['word_count']}")
        print(f"   🗣️ Speech rate: {result['word_count']/(result['duration']/60):.1f} words/minute")
        print()
        
        # Output full text
        print("📜 FULL TEXT:")
        print(f'   "{result["full_text"]}"')
        print()
        
        # Output sentences with timestamps
        print("⏰ SENTENCES WITH TIMESTAMPS:")
        for i, sentence in enumerate(result['sentences'], 1):
            start_time = sentence['start_time']
            end_time = sentence['end_time']
            duration = sentence['duration']
            text = sentence['sentence']
            
            # Format time
            start_min = int(start_time // 60)
            start_sec = start_time % 60
            end_min = int(end_time // 60)
            end_sec = end_time % 60
            
            print(f"   {i:2d}. [{start_min:02d}:{start_sec:05.2f} - {end_min:02d}:{end_sec:05.2f}] ({duration:.2f}s)")
            print(f"       {text}")
            print()
        
        # Save result to JSON
        output_path = Path(audio_path).stem + "_transcript.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Result saved to: {output_path}")
        print()
        
        # Suggest additional options
        print("🔧 ADDITIONAL OPTIONS:")
        print(f"   • Convert to CSV: python utils.py {output_path} --csv transcript.csv")
        print(f"   • Convert to SRT: python utils.py {output_path} --srt transcript.srt")
        print(f"   • Statistics: python utils.py {output_path} --stats")
        print(f"   • Search text: python utils.py {output_path} --search 'search text'")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
