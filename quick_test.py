#!/usr/bin/env python3
"""
Quick test for demonstrating script functionality
"""

import os
import sys
import subprocess

def main():
    """Main quick test function"""
    print("🚀 === QUICK TEST AUDIO2TEXT-TIMESTAMPED ===\n")
    
    # Check if test file already exists
    test_file = "test_simple.aiff"
    
    if not os.path.exists(test_file):
        print(f"📝 Creating test audio file: {test_file}")
        result = os.system(f'say "Hello world. This is a quick test of speech recognition." -o {test_file}')
        
        if result != 0 or not os.path.exists(test_file):
            print("❌ Could not create test audio file")
            return 1
        
        print(f"✅ Test audio file created: {test_file}")
    else:
        print(f"📁 Using existing test file: {test_file}")
    
    # Run demonstration
    print("\n🎯 Starting demonstration...")
    
    try:
        # Run demo.py
        python_path = "/Users/dmitry.egorov/projects/playground/video-localization-pipeline/audio2text-timestamped/.venv/bin/python"
        cmd = [python_path, "demo.py", test_file]
        
        subprocess.run(cmd, check=True)
        
        print("\n🎉 Quick test completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running test: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
