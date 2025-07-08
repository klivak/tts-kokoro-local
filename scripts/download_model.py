#!/usr/bin/env python3
"""
Download script for Kokoro TTS model files
"""

import os
import requests
from pathlib import Path
import sys

def download_file(url, filename):
    """Download a file from URL with progress bar"""
    print(f"Downloading {filename}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        
        with open(filename, 'wb') as file:
            if total_size == 0:
                file.write(response.content)
            else:
                downloaded = 0
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    file.write(data)
                    
                    # Show progress
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes")
                    sys.stdout.flush()
                    
        print(f"\n✅ {filename} downloaded successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error downloading {filename}: {e}")
        return False
        
    return True

def main():
    """Main function to download model files"""
    print("🔄 Kokoro TTS Model Downloader")
    print("=" * 40)
    
    # Get project root and models directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    models_dir = project_root / "models"
    
    # Create models directory if it doesn't exist
    models_dir.mkdir(exist_ok=True)
    
    # Change to models directory
    os.chdir(models_dir)
    
    # Model files URLs
    files_to_download = [
        {
            "url": "https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx",
            "filename": "kokoro-v1.0.onnx",
            "description": "Kokoro TTS Model"
        },
        {
            "url": "https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin",
            "filename": "voices-v1.0.bin",
            "description": "Voices configuration"
        }
    ]
    
    # Check if files already exist
    for file_info in files_to_download:
        filename = file_info["filename"]
        if os.path.exists(filename):
            print(f"⚠️  {filename} already exists. Skipping download.")
        else:
            success = download_file(file_info["url"], filename)
            if not success:
                print(f"❌ Failed to download {filename}")
                return False
    
    print(f"\n🎉 All model files are ready in {models_dir}!")
    print("You can now run the TTS application:")
    print("   python run.py")
    
    return True

if __name__ == "__main__":
    main() 