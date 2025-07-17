#!/usr/bin/env python3
"""
Utility for displaying Whisper model information
"""

def show_model_info():
    """Show available models information"""
    
    models = [
        {
            'name': 'tiny',
            'size': '~40 MB',
            'speed': '⚡⚡⚡⚡⚡',
            'accuracy': '⭐⭐',
            'use_case': 'Quick tests, preliminary processing'
        },
        {
            'name': 'base',
            'size': '~140 MB',
            'speed': '⚡⚡⚡⚡',
            'accuracy': '⭐⭐⭐',
            'use_case': 'Default, good balance'
        },
        {
            'name': 'small',
            'size': '~460 MB',
            'speed': '⚡⚡⚡',
            'accuracy': '⭐⭐⭐⭐',
            'use_case': 'Improved accuracy'
        },
        {
            'name': 'medium',
            'size': '~1.5 GB',
            'speed': '⚡⚡',
            'accuracy': '⭐⭐⭐⭐⭐',
            'use_case': 'Recommended for production'
        },
        {
            'name': 'large-v2',
            'size': '~3.0 GB',
            'speed': '⚡',
            'accuracy': '⭐⭐⭐⭐⭐⭐',
            'use_case': 'High accuracy, slow'
        },
        {
            'name': 'large-v3',
            'size': '~3.1 GB',
            'speed': '⚡',
            'accuracy': '⭐⭐⭐⭐⭐⭐⭐',
            'use_case': 'Maximum accuracy (best)'
        }
    ]
    
    print("🤖 === AVAILABLE WHISPER MODELS ===\n")
    
    for model in models:
        print(f"📌 {model['name'].upper()}")
        print(f"   💾 Size: {model['size']}")
        print(f"   🚀 Speed: {model['speed']}")
        print(f"   🎯 Accuracy: {model['accuracy']}")
        print(f"   💡 Use case: {model['use_case']}")
        print()
    
    print("🔧 === RECOMMENDATIONS ===")
    print("🚀 For quick tests: tiny, base")
    print("⚖️  Balance of speed and accuracy: small, medium")
    print("🎯 Maximum accuracy: large-v3")
    print("⚠️  First download of large models: 10-30 minutes")
    print()
    
    print("📝 === USAGE EXAMPLES ===")
    print("# Quick test")
    print("python audio2text_timestamped.py audio.mp3 -m tiny")
    print()
    print("# Recommended model")
    print("python audio2text_timestamped.py audio.mp3 -m medium")
    print()
    print("# Maximum accuracy")
    print("python audio2text_timestamped.py audio.mp3 -m large-v3")
    print()

def show_troubleshooting():
    """Show troubleshooting information"""
    print("🔧 === TROUBLESHOOTING ===\n")
    
    print("❓ Problem: Model takes long to load")
    print("✅ Solution:")
    print("   1. This is normal for large models (large-v2, large-v3)")
    print("   2. First download takes 10-30 minutes")
    print("   3. Use medium model for balance")
    print()
    
    print("❓ Problem: No internet or slow download")
    print("✅ Solution:")
    print("   1. Use smaller model: -m base or -m small")
    print("   2. Try again later")
    print("   3. Check internet connection")
    print()
    
    print("❓ Problem: Not enough memory")
    print("✅ Solution:")
    print("   1. Use smaller model: -m small or -m base")
    print("   2. Close other programs")
    print("   3. Use CPU instead of GPU: -d cpu")
    print()

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("Usage:")
        print("python model_info.py          - show model information")
        print("python model_info.py trouble  - show troubleshooting")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == 'trouble':
        show_troubleshooting()
    else:
        show_model_info()

if __name__ == "__main__":
    main()
