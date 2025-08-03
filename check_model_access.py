#!/usr/bin/env python3
"""
Check access to HuggingFace gated models
Verifies that authentication works and model is accessible
"""

import sys
import os

try:
    from huggingface_hub import HfApi, model_info
    from huggingface_hub.utils import HfHubHTTPError
    import requests
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install huggingface_hub requests")
    sys.exit(1)


def check_model_access(model_name="pyannote/speaker-diarization-3.1"):
    """Check if we have access to the specified model"""
    
    print(f"Checking access to model: {model_name}")
    print("=" * 50)
    
    try:
        # Initialize HuggingFace API
        api = HfApi()
        
        # Check if we're authenticated
        try:
            user_info = api.whoami()
            print(f"✓ Authenticated as: {user_info['name']}")
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            print("Run: huggingface-cli login")
            return False
        
        # Try to get model info
        try:
            info = model_info(model_name)
            print(f"✓ Model found: {model_name}")
            print(f"  - Model ID: {info.id}")
            print(f"  - Private: {info.private}")
            print(f"  - Gated: {getattr(info, 'gated', 'Unknown')}")
            
            if hasattr(info, 'cardData') and info.cardData:
                license_info = info.cardData.get('license', 'Unknown')
                print(f"  - License: {license_info}")
                
        except HfHubHTTPError as e:
            if e.response.status_code == 401:
                print(f"✗ Access denied (401): Model is gated")
                print(f"  Visit: https://huggingface.co/{model_name}")
                print("  Click 'Agree and access repository'")
                return False
            elif e.response.status_code == 404:
                print(f"✗ Model not found (404)")
                return False
            else:
                print(f"✗ HTTP Error {e.response.status_code}: {e}")
                return False
        except Exception as e:
            print(f"✗ Error accessing model: {e}")
            return False
        
        # Try to actually access the model files
        try:
            from pyannote.audio import Pipeline
            print("\n" + "=" * 30)
            print("Testing model loading...")
            
            # This will fail if we don't have access
            pipeline = Pipeline.from_pretrained(
                model_name,
                use_auth_token=True
            )
            print("✓ Model loaded successfully!")
            print("✓ You have full access to this model")
            return True
            
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            if "gated" in str(e).lower() or "access" in str(e).lower():
                print("  This suggests you need to accept the model license")
                print(f"  Visit: https://huggingface.co/{model_name}")
            return False
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main function"""
    model_name = "pyannote/speaker-diarization-3.1"
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    
    success = check_model_access(model_name)
    
    if success:
        print(f"\n🎉 Success! You can use {model_name}")
    else:
        print(f"\n❌ Access denied to {model_name}")
        print("\nSteps to fix:")
        print("1. huggingface-cli login")
        print(f"2. Visit https://huggingface.co/{model_name}")
        print("3. Click 'Agree and access repository'")
        print("4. Wait a few minutes for access to propagate")
        print("5. Run this script again")


if __name__ == "__main__":
    main()
