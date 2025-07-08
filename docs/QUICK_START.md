# 🚀 Kokoro TTS - Швидкий старт

## Для користувачів (найпростіший спосіб)

### 1. Завантажте готовий релізний файл
- Перейдіть до [Releases](../../releases)
- Завантажте архів для вашої операційної системи:
  - `KokoroTTS_Windows.zip` для Windows
  - `KokoroTTS_macOS.zip` для macOS
  - `KokoroTTS_Linux.tar.gz` для Linux

### 2. Розпакуйте та запустіть
#### Windows:
```
1. Розпакуйте ZIP архів
2. Відкрийте папку release_windows
3. Двічі клацніть на Launch_KokoroTTS.bat
```

#### macOS:
```
1. Розпакуйте ZIP архів
2. Відкрийте папку release_macos
3. Двічі клацніть на Launch_KokoroTTS.command
```

#### Linux:
```bash
# Розпакуйте архів
tar -xzf KokoroTTS_Linux.tar.gz

# Перейдіть до папки та запустіть
cd release_linux
./launch_kokoro_tts.sh
```

### 3. Використання
1. Виберіть мову та голос
2. Введіть текст
3. Натисніть "Generate Speech"
4. Прослухайте або збережіть результат

---

## Для розробників

### Запуск з коду
```bash
# Клонуйте репозиторій
git clone <repo-url>
cd tts-kokoro-local

# Встановіть залежності
pip install -r requirements.txt

# Запустіть
python run.py
```

### Створення релізу
```bash
# Встановіть залежності для збірки
pip install -r requirements_build.txt

# Протестуйте перед збіркою
python test_build.py

# Створіть релізний файл
python build_release.py
```

---

## Системні вимоги

### Мінімальні:
- **Windows**: 10/11 (64-bit)
- **macOS**: 10.15+ (Catalina)
- **Linux**: Ubuntu 18.04+
- **RAM**: 4GB
- **Диск**: 500MB вільного місця

### Рекомендовані:
- **RAM**: 8GB+
- **Диск**: 1GB вільного місця
- **Процесор**: 4+ ядер

---

## Підтримка

### Часті проблеми:
1. **Не запускається**: Перевірте системні вимоги
2. **Немає звуку**: Перевірте аудіо налаштування
3. **Повільно працює**: Закрийте інші програми

### Отримання допомоги:
- Прочитайте README.md
- Перевірте BUILD_GUIDE.md
- Створіть issue на GitHub

---

**Версія**: 1.0 | **Мова**: Українська | **Підтримка**: Windows, macOS, Linux 