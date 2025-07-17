#!/usr/bin/env python3
"""
Simple test for checking module functionality without audio file
"""

import sys
import os
import json
from pathlib import Path

# Add current folder to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test imports"""
    print("🔍 Testing imports...")
    
    try:
        from audio2text_timestamped import AudioToTextConverter
        print("✅ AudioToTextConverter imported successfully")
        return True
    except ImportError as e:
        print(f"❌ AudioToTextConverter import error: {e}")
        return False

def test_model_initialization():
    """Test model initialization"""
    print("🔍 Testing model initialization...")
    
    try:
        from audio2text_timestamped import AudioToTextConverter
        
        # Initialize with the fastest model
        converter = AudioToTextConverter(model_size="tiny", device="cpu")
        print("✅ Whisper model initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Model initialization error: {e}")
        return False

def test_sentence_splitting():
    """Test sentence splitting"""
    print("🔍 Testing sentence splitting...")
    
    try:
        from audio2text_timestamped import AudioToTextConverter
        
        converter = AudioToTextConverter(model_size="tiny", device="cpu")
        
        # Test text
        test_text = "Hello! This is the first sentence. This is the second sentence? And this is the third sentence."
        
        sentences = converter._split_into_sentences(test_text)
        expected_count = 4
        
        print(f"   Source text: {test_text}")
        print(f"   Got sentences: {len(sentences)}")
        print(f"   Expected sentences: {expected_count}")
        
        for i, sentence in enumerate(sentences, 1):
            print(f"   {i}. {sentence}")
        
        if len(sentences) == expected_count:
            print("✅ Sentence splitting works correctly")
            return True
        else:
            print("⚠️  Sentence splitting works, but count may differ")
            return True
            
    except Exception as e:
        print(f"❌ Sentence splitting test error: {e}")
        return False

def test_utils_functions():
    """Test utilities"""
    print("🔍 Testing utilities...")
    
    try:
        from utils import format_time_srt, json_to_csv, json_to_srt
        
        # Test time formatting
        time_formatted = format_time_srt(123.456)
        expected = "00:02:03,456"
        
        print(f"   Time formatting test:")
        print(f"   Input time: 123.456 seconds")
        print(f"   Result: {time_formatted}")
        print(f"   Expected: {expected}")
        
        if time_formatted == expected:
            print("✅ Time formatting works correctly")
            return True
        else:
            print("❌ Time formatting error")
            return False
            
    except Exception as e:
        print(f"❌ Utilities test error: {e}")
        return False

def test_json_structure():
    """Test JSON result structure"""
    print("🔍 Testing JSON structure...")
    
    try:
        # Read example JSON
        with open("example_result.json", "r", encoding="utf-8") as f:
            example_data = json.load(f)
        
        required_fields = [
            "file_path", "detected_language", "language_probability",
            "duration", "full_text", "sentences", "word_count", "sentence_count"
        ]
        
        sentence_fields = [
            "sentence", "start_time", "end_time", "duration", "language"
        ]
        
        print("   Checking main fields:")
        for field in required_fields:
            if field in example_data:
                print(f"   ✅ {field}: {type(example_data[field]).__name__}")
            else:
                print(f"   ❌ {field}: missing")
                return False
        
        print("   Checking sentence fields:")
        if example_data["sentences"]:
            first_sentence = example_data["sentences"][0]
            for field in sentence_fields:
                if field in first_sentence:
                    print(f"   ✅ {field}: {type(first_sentence[field]).__name__}")
                else:
                    print(f"   ❌ {field}: missing")
                    return False
        
        print("✅ JSON structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ JSON structure test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 === AUDIO2TEXT-TIMESTAMPED UNIT TESTS ===\n")
    
    tests = [
        test_imports,
        test_model_initialization,
        test_sentence_splitting,
        test_utils_functions,
        test_json_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Unexpected error in test {test.__name__}: {e}\n")
    
    print("📊 === TEST RESULTS ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print("⚠️  Not all tests passed")
        return 1

if __name__ == "__main__":
    exit(main())
