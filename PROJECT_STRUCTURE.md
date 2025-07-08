# 📁 Project Structure

```
tts-kokoro-local/
├── 📄 README.md                    # Main documentation
├── 📄 requirements.txt             # Runtime dependencies
├── 📄 run.py                       # Main launcher
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 .gitignore                   # Git ignore rules
│
├── 📂 src/                         # Source code
│   └── 📄 kokoro_tts_gui.py        # Main GUI application
│
├── 📂 scripts/                     # Utility scripts
│   ├── 📄 download_model.py        # Model downloader
│   └── 📄 run.py                   # Alternative launcher
│
├── 📂 build/                       # Build system
│   ├── 📄 build_release.py         # Main build script
│   ├── 📄 build_windows.bat        # Windows build script
│   ├── 📄 build_macos.sh           # macOS build script
│   ├── 📄 test_build.py            # Build testing
│   └── 📄 requirements_build.txt   # Build dependencies
│
├── 📂 docs/                        # Documentation
│   ├── 📄 BUILD_GUIDE.md           # Build instructions
│   ├── 📄 MACOS_GUIDE.md           # macOS specific guide
│   ├── 📄 WINDOWS_GUIDE.md         # Windows specific guide
│   └── 📄 QUICK_START.md           # Quick start guide
│
├── 📂 models/                      # AI models (gitignored)
│   ├── 📄 kokoro-v1.0.onnx         # Main TTS model
│   └── 📄 voices-v1.0.bin          # Voice configurations
│
├── 📂 output/                      # Generated files (gitignored)
│   ├── 📂 audio_output/            # Generated audio files
│   └── 📂 voice_previews/          # Voice preview samples
│
└── 📂 release_*/                   # Build outputs (gitignored)
    ├── 📄 KokoroTTS.exe/.app       # Executable
    ├── 📄 Launch_KokoroTTS.*       # Launcher script
    └── 📄 README.md                # Release documentation
```

## 🎯 Key Benefits

### ✅ Better Organization
- **Separation of concerns**: Source, build, docs, models in separate folders
- **Clear structure**: Easy to find specific files
- **Scalability**: Easy to add new components

### ✅ Development Workflow
- **`run.py`**: Single entry point for users
- **`src/`**: All source code in one place
- **`scripts/`**: Utility scripts separated from main code
- **`build/`**: All build-related files together

### ✅ Distribution
- **`models/`**: Heavy model files in dedicated folder
- **`output/`**: Generated files don't clutter main directory
- **`docs/`**: All documentation organized

### ✅ Maintenance
- **Gitignore**: Proper exclusion of generated files
- **Dependencies**: Clear separation of runtime vs build dependencies
- **Platform support**: Dedicated scripts for each OS

## 🚀 Usage

### For End Users:
```bash
python run.py
```

### For Developers:
```bash
# Development
python src/kokoro_tts_gui.py

# Build
python build/build_release.py

# Test
python build/test_build.py
```

### For Contributors:
- **Source code**: `src/`
- **Documentation**: `docs/`
- **Build system**: `build/`
- **Utilities**: `scripts/`

---

**Version**: 2.0 - Organized Structure
**Date**: 2024
**Platforms**: Windows, macOS, Linux 