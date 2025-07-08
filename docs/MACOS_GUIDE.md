# 🍎 Kokoro TTS для macOS

## Швидкий старт

### 1. Встановлення Python
```bash
# Встановіть Python через Homebrew (рекомендовано)
brew install python@3.10

# Або завантажте з python.org
```

### 2. Встановлення Xcode Command Line Tools
```bash
xcode-select --install
```

### 3. Клонування та запуск
```bash
# Клонуйте репозиторій
git clone <your-repo-url>
cd tts-kokoro-local

# Встановіть залежності
pip3 install -r requirements.txt

# Запустіть програму
python3 run.py
```

## Створення релізу для macOS

### 1. Встановлення залежностей для збірки
```bash
pip3 install -r requirements_build.txt
```

### 2. Запуск збірки
```bash
# Зробіть скрипт виконуваним
chmod +x build_macos.sh

# Запустіть збірку
./build_macos.sh
```

### 3. Результат
Після успішної збірки ви отримаєте:
- `release_macos/KokoroTTS.app` - основний додаток
- `release_macos/Launch_KokoroTTS.command` - лаунчер
- `release_macos/README.md` - документація

## Запуск релізу

### Метод 1: Через лаунчер
```bash
cd release_macos
./Launch_KokoroTTS.command
```

### Метод 2: Прямий запуск
```bash
cd release_macos
open KokoroTTS.app
```

## Вирішення проблем

### "KokoroTTS.app cannot be opened because the developer cannot be verified"
1. Натисніть правою кнопкою на `KokoroTTS.app`
2. Виберіть "Open" з контекстного меню
3. Натисніть "Open" у діалозі безпеки

### Для розробників (підписання):
```bash
codesign --force --deep --sign - KokoroTTS.app
```

### Створення DMG для розповсюдження
```bash
# Встановіть create-dmg
brew install create-dmg

# Запустіть збірку (DMG створюється автоматично)
./build_macos.sh
```

## Системні вимоги

- macOS 10.15+ (Catalina або новіше)
- Python 3.8+
- ~300MB вільного місця
- Інтернет для завантаження моделей

## Особливості macOS

- Додаток упаковується як `.app` bundle
- Підтримка Retina дисплеїв
- Інтеграція з системним аудіо
- Автоматичне управління залежностями

---

**Примітка**: Для Apple Silicon (M1/M2) збірка відбувається автоматично з оптимізацією для ARM64. 