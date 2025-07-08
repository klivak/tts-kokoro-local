# 🪟 Kokoro TTS для Windows

## Швидкий старт

### 1. Встановлення Python
1. Завантажте Python 3.10+ з [python.org](https://www.python.org/downloads/)
2. **ВАЖЛИВО**: Поставте галочку "Add Python to PATH" під час встановлення
3. Перезавантажте командний рядок

### 2. Клонування та запуск
```cmd
# Клонуйте репозиторій
git clone <your-repo-url>
cd tts-kokoro-local

# Встановіть залежності
pip install -r requirements.txt

# Запустіть програму
python run.py
```

## Створення релізу для Windows

### 1. Встановлення залежностей для збірки
```cmd
pip install -r requirements_build.txt
```

### 2. Запуск збірки
```cmd
# Запустіть build скрипт
build_windows.bat

# Або вручну
python build_release.py
```

### 3. Результат
Після успішної збірки ви отримаєте:
- `release_windows\KokoroTTS.exe` - основний додаток
- `release_windows\Launch_KokoroTTS.bat` - лаунчер
- `release_windows\README.md` - документація

## Запуск релізу

### Метод 1: Через лаунчер
```cmd
cd release_windows
Launch_KokoroTTS.bat
```

### Метод 2: Прямий запуск
```cmd
cd release_windows
KokoroTTS.exe
```

### Метод 3: Подвійний клік
Просто двічі клацніть на `KokoroTTS.exe` або `Launch_KokoroTTS.bat`

## Вирішення проблем

### "MSVCP140.dll was not found"
Встановіть Microsoft Visual C++ Redistributable:
1. Завантажте з [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Запустіть інсталятор
3. Перезавантажте систему

### "Windows protected your PC"
1. Натисніть "More info"
2. Натисніть "Run anyway"
3. Це нормально для неподписаних додатків

### Антивірус блокує файл
1. Додайте папку в виключення антивірусу
2. Або тимчасово вимкніть захист реального часу

### Помилка "Python was not found"
1. Переконайтеся, що Python встановлено
2. Додайте Python до PATH:
   - Пошук → "Environment Variables"
   - Додайте шлях до Python у PATH

## Створення інсталятора

### NSIS (рекомендовано)
```cmd
# Встановіть NSIS
# Завантажте з https://nsis.sourceforge.io/

# Створіть скрипт installer.nsi
# Скомпілюйте інсталятор
```

### Inno Setup
```cmd
# Встановіть Inno Setup
# Завантажте з https://jrsoftware.org/isinfo.php

# Створіть скрипт setup.iss
# Скомпілюйте інсталятор
```

## Системні вимоги

- Windows 10/11 (64-bit)
- Python 3.8+ (для розробки)
- ~300MB вільного місця
- Інтернет для завантаження моделей

## Особливості Windows

- Підтримка Windows 10/11
- Автоматичне виявлення аудіо пристроїв
- Інтеграція з провідником Windows
- Підтримка високих DPI дисплеїв

## Розповсюдження

### ZIP архів
```cmd
# Стисніть папку release_windows
7z a KokoroTTS_Windows.zip release_windows\*
```

### Portable версія
- Просто скопіюйте папку `release_windows`
- Не потребує встановлення
- Працює з USB флешки

---

**Примітка**: Релізні файли працюють без встановлення Python на цільовій машині. 