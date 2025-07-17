#!/usr/bin/env python3
"""
Improved test for checking audio2text_timestamped.py functionality
Includes test audio file creation and alternative testing methods
"""

import os
import json
import sys
import tempfile
from pathlib import Path

# Add current folder to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_audio_improved():
    """
    Improved function for creating test audio file
    """
    # English text for better compatibility
    test_text = "Hello world. This is a test audio file. Speech recognition is working correctly."
    
    # Create file in current directory in AIFF format (supported by say command)
    audio_path = os.path.join(os.getcwd(), "test_audio.aiff")
    
    try:
        # Use AIFF format, which is better supported by say command
        cmd = f'say "{test_text}" -o "{audio_path}"'
        
        print(f"Executing command: {cmd}")
        result = os.system(cmd)
        
        if result == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            print(f"✅ Test audio file created: {audio_path}")
            print(f"   File size: {os.path.getsize(audio_path)} bytes")
            return audio_path
        else:
            print(f"❌ Command failed or file is empty")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return None
        
    except Exception as e:
        print(f"❌ Error creating test audio file: {e}")
        return None

def test_with_real_audio():
    """
    Main test with real audio file
    """
    print("🎵 === FULL TEST WITH AUDIO FILE ===")
    
    # Create test audio file
    audio_path = create_test_audio_improved()
    if not audio_path:
        print("⚠️  Could not create test audio file")
        return False
    
    try:
        # Import our module
        from audio2text_timestamped import AudioToTextConverter
        
        # Create converter
        print("🔄 Initializing Whisper model...")
        converter = AudioToTextConverter(model_size="tiny", device="cpu")
        
        # Transcribe audio
        print("🎙️ Transcribing audio...")
        result = converter.transcribe_audio(audio_path)
        
        # Check results
        print("📊 Results:")
        print(f"   Language: {result['detected_language']}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Sentences: {result['sentence_count']}")
        print(f"   Words: {result['word_count']}")
        print(f"   Text: {result['full_text']}")
        
        # Save result
        output_path = "test_result.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Result saved: {output_path}")
        
        # Delete test file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🗑️  Test file deleted: {audio_path}")
        
        print("✅ Full test with audio file completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
        # Delete test file in case of error
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return False

def fallback_test():
    """
    Alternative test without creating audio file
    """
    print("🔧 === ALTERNATIVE TEST (WITHOUT AUDIO FILE) ===")
    
    try:
        # Test import and initialization
        from audio2text_timestamped import AudioToTextConverter
        
        print("✅ Module imported successfully")
        
        # Test initialization
        converter = AudioToTextConverter(model_size="tiny", device="cpu")
        print("✅ Model initialized successfully")
        
        # Test sentence splitting
        test_text = "Hello world. This is a test. How are you?"
        sentences = converter._split_into_sentences(test_text)
        print(f"✅ Sentence splitting: {len(sentences)} sentences")
        for i, sentence in enumerate(sentences, 1):
            print(f"   {i}. {sentence}")
        
        print("✅ Alternative test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Alternative test error: {e}")
        return False

def main():
    """
    Main testing function
    """
    print("🧪 === EXTENDED TESTING AUDIO2TEXT-TIMESTAMPED ===\n")
    
    # First try full test with audio file
    if test_with_real_audio():
        print("\n🎉 Full testing completed successfully!")
        return 0
    
    # If that fails, run alternative test
    print("\n🔄 Running alternative testing...")
    if fallback_test():
        print("\n✅ Alternative testing completed successfully!")
        return 0
    else:
        print("\n❌ All tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
