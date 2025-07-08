#!/usr/bin/env python3
"""
Main launcher for Kokoro TTS
Works with the new organized directory structure
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    print("🎙️ Kokoro TTS Launcher")
    print("=" * 30)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Add src directory to Python path
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Check if models exist
    models_dir = project_root / "models"
    model_file = models_dir / "kokoro-v1.0.onnx"
    voices_file = models_dir / "voices-v1.0.bin"
    
    if not model_file.exists() or not voices_file.exists():
        print("📥 Models not found. Downloading...")
        
        # Run download script
        download_script = project_root / "scripts" / "download_model.py"
        if download_script.exists():
            try:
                subprocess.run([sys.executable, str(download_script)], 
                             cwd=str(project_root), check=True)
            except subprocess.CalledProcessError:
                print("❌ Failed to download models")
                return False
        else:
            print("❌ Download script not found")
            return False
    
    # Check if output directories exist
    output_dir = project_root / "output"
    (output_dir / "audio_output").mkdir(parents=True, exist_ok=True)
    (output_dir / "voice_previews").mkdir(parents=True, exist_ok=True)
    
    print("✅ Starting Kokoro TTS...")
    
    # Import and run the main application
    try:
        from kokoro_tts_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to import GUI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 