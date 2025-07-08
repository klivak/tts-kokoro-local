# 🏗️ Kokoro TTS - Build Guide

Цей посібник показує, як створити автономні виконувані файли для різних платформ.

## 📋 Системні вимоги

### Загальні вимоги:
- Python 3.8+ 
- Git
- Інтернет-з'єднання (для завантаження моделей)

### Специфічні вимоги по платформах:

#### Windows:
- Windows 10/11
- Visual Studio Build Tools (автоматично встановлюється з Python)

#### macOS:
- macOS 10.15+ (Catalina або новіше)
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (опціонально для DMG): `brew install create-dmg`

#### Linux:
- Ubuntu 18.04+ або еквівалент
- Базові інструменти розробки: `sudo apt install build-essential`

## 🚀 Швидкий старт

### 1. Підготовка
```bash
# Клонуйте репозиторій
git clone <your-repo-url>
cd tts-kokoro-local

# Встановіть залежності для збірки
pip install -r requirements_build.txt

# Завантажте моделі (якщо ще не завантажені)
python download_model.py
```

### 2. Збірка для вашої платформи

#### Windows:
```cmd
# Запустіть build скрипт
build_windows.bat

# Або вручну
python build_release.py
```

#### macOS:
```bash
# Зробіть скрипт виконуваним
chmod +x build_macos.sh

# Запустіть збірку
./build_macos.sh

# Або вручну
python3 build_release.py
```

#### Linux:
```bash
# Вручну
python3 build_release.py
```

## 📦 Структура релізу

Після успішної збірки ви отримаєте:

### Windows (`release_windows/`):
```
release_windows/
├── KokoroTTS.exe           # Основний додаток
├── Launch_KokoroTTS.bat    # Лаунчер
└── README.md               # Документація
```

### macOS (`release_macos/`):
```
release_macos/
├── KokoroTTS.app/          # Додаток macOS
├── Launch_KokoroTTS.command # Лаунчер
└── README.md               # Документація
```

### Linux (`release_linux/`):
```
release_linux/
├── KokoroTTS               # Виконуваний файл
├── launch_kokoro_tts.sh    # Лаунчер
└── README.md               # Документація
```

## 🔧 Налаштування збірки

### Додаткові файли в збірку
Відредагуйте `build_release.py` для додавання файлів:

```python
datas=[
    ('kokoro-v1.0.onnx', '.'),
    ('voices-v1.0.bin', '.'),
    ('README.md', '.'),
    ('your_file.txt', '.'),  # Додайте свій файл
],
```

### Зміна іконки
1. **Windows**: Додайте `icon.ico` у корінь проєкту
2. **macOS**: Додайте `icon.icns` у корінь проєкту
3. **Linux**: Іконки не підтримуються PyInstaller

### Оптимізація розміру
Додайте до команди PyInstaller:
```python
"--exclude-module", "matplotlib",
"--exclude-module", "scipy",
"--exclude-module", "pandas",
```

## 🎯 Тестування релізу

### Перед релізом:
1. **Функціональність**: Перевірте всі голоси та функції
2. **Продуктивність**: Протестуйте на різних текстах
3. **Сумісність**: Перевірте на чистій системі

### Тестові сценарії:
```
✅ Запуск програми
✅ Генерація аудіо для кожного голосу
✅ Збереження файлів
✅ Попередній перегляд голосів
✅ Зміна швидкості мовлення
✅ Робота з довгими текстами
✅ Перевірка статистики
```

## 📤 Розповсюдження

### Windows:
1. **ZIP архів**: Стисніть папку `release_windows/`
2. **Installer**: Використайте NSIS або Inno Setup
3. **Portable**: Просто розповсюджуйте папку

### macOS:
1. **ZIP архів**: Стисніть папку `release_macos/`
2. **DMG**: Використайте `create-dmg` (включено в `build_macos.sh`)
3. **App Store**: Потрібен Apple Developer Account

### Linux:
1. **TAR.GZ**: `tar -czf KokoroTTS.tar.gz release_linux/`
2. **AppImage**: Використайте `appimage-builder`
3. **Flatpak**: Створіть маніфест Flatpak

## 🐛 Вирішення проблем

### Помилки збірки:

#### "ModuleNotFoundError: No module named 'kokoro_onnx'"
```bash
pip install kokoro-onnx
```

#### "PyInstaller command not found"
```bash
pip install pyinstaller
```

#### macOS: "cannot be opened because the developer cannot be verified"
```bash
# Для користувачів:
# Right-click → Open → Open

# Для розробників:
codesign --force --deep --sign - KokoroTTS.app
```

#### Windows: "MSVCP140.dll was not found"
Встановіть Microsoft Visual C++ Redistributable

### Помилки виконання:

#### "Failed to load model"
Перевірте наявність файлів моделі в папці з виконуваним файлом

#### "Audio device not found"
Перевірте аудіо драйвери та налаштування системи

## 📊 Розміри релізів

Приблизні розміри після збірки:

- **Windows**: ~200-300 MB
- **macOS**: ~250-350 MB  
- **Linux**: ~200-300 MB

## 🔄 Автоматизація

### GitHub Actions (приклад):
```yaml
name: Build Releases

on:
  release:
    types: [published]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements_build.txt
      - run: python download_model.py
      - run: python build_release.py
      - uses: actions/upload-artifact@v3
        with:
          name: windows-release
          path: release_windows/
```

## 📞 Підтримка

При виникненні проблем:

1. Перевірте системні вимоги
2. Оновіть Python та pip
3. Очистіть кеш pip: `pip cache purge`
4. Перезавантажте систему
5. Створіть issue з логами помилок

---

**Версія**: 1.0
**Останнє оновлення**: 2024
**Платформи**: Windows, macOS, Linux 