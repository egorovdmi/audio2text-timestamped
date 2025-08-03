#!/usr/bin/env python3
"""
Check available pyannote speaker diarization models
"""

import requests
from huggingface_hub import list_models

def check_pyannote_models():
    """List all available pyannote speaker diarization models"""
    
    print("Available Pyannote Speaker Diarization Models:")
    print("=" * 60)
    
    try:
        # Get all pyannote models
        models = list_models(author="pyannote", task="speaker-diarization")
        
        diarization_models = []
        for model in models:
            if "speaker-diarization" in model.id:
                try:
                    # Get model info
                    response = requests.get(f"https://huggingface.co/api/models/{model.id}")
                    if response.status_code == 200:
                        model_info = response.json()
                        downloads = model_info.get('downloads', 0)
                        diarization_models.append({
                            'id': model.id,
                            'downloads': downloads,
                            'created_at': model_info.get('createdAt', 'Unknown')
                        })
                except:
                    diarization_models.append({
                        'id': model.id,
                        'downloads': 0,
                        'created_at': 'Unknown'
                    })
        
        # Sort by downloads (popularity)
        diarization_models.sort(key=lambda x: x['downloads'], reverse=True)
        
        print(f"Found {len(diarization_models)} speaker diarization models:\n")
        
        for i, model in enumerate(diarization_models, 1):
            print(f"{i}. {model['id']}")
            print(f"   Downloads: {model['downloads']:,}")
            print(f"   Created: {model['created_at'][:10] if model['created_at'] != 'Unknown' else 'Unknown'}")
            print()
        
        # Check segmentation models too (they affect quality)
        print("\n" + "=" * 60)
        print("Available Segmentation Models (affect diarization quality):")
        print("=" * 60)
        
        seg_models = list_models(author="pyannote", search="segmentation")
        for model in seg_models:
            if "segmentation" in model.id:
                print(f"- {model.id}")
        
    except Exception as e:
        print(f"Error fetching models: {e}")


if __name__ == "__main__":
    check_pyannote_models()
