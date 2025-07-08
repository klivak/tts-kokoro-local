#!/usr/bin/env python3
"""
Simple startup script for Kokoro TTS GUI
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import kokoro_onnx
        import soundfile
        import pygame
        import tkinter
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_model_files():
    """Check if model files exist"""
    model_file = "kokoro-v1.0.onnx"
    voices_file = "voices-v1.0.bin"
    
    if not os.path.exists(model_file) or not os.path.exists(voices_file):
        print("📥 Model files not found. Downloading...")
        try:
            subprocess.run([sys.executable, "download_model.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to download model files")
            return False
    
    return True



def main():
    """Main startup function"""
    print("🚀 Starting Kokoro TTS GUI...")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check model files
    if not check_model_files():
        return
    
    # Launch GUI
    try:
        from kokoro_tts_gui import main as launch_gui
        launch_gui()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

if __name__ == "__main__":
    main() 