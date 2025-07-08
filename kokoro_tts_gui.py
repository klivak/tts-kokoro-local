import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import tempfile
import pygame
import soundfile as sf
from pathlib import Path
import time

# Basic audio processing only
import wave

# Try to import kokoro_onnx, handle if not installed
try:
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False

class KokoroTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kokoro TTS Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Variables
        self.kokoro = None
        self.current_audio_file = None
        self.is_generating = False
        self.preview_samples = {}
        
        # Available voices for different languages with readable names
        self.voices = {
            'English (US) - Female': {
                'af_alloy': 'Alloy (Нейтральний)',
                'af_aoede': 'Aoede (М\'який)',
                'af_bella': 'Bella (Теплий)',
                'af_heart': 'Heart (Сердечний)',
                'af_jessica': 'Jessica (Класичний)',
                'af_kore': 'Kore (Енергійний)',
                'af_nicole': 'Nicole (Професійний)',
                'af_nova': 'Nova (Сучасний)',
                'af_river': 'River (Спокійний)',
                'af_sarah': 'Sarah (Дружелюбний)',
                'af_sky': 'Sky (Легкий)'
            },
            'English (US) - Male': {
                'am_adam': 'Adam (Впевнений)',
                'am_echo': 'Echo (Резонансний)',
                'am_eric': 'Eric (Дружній)',
                'am_fenrir': 'Fenrir (Сильний)',
                'am_liam': 'Liam (Теплий)',
                'am_michael': 'Michael (Класичний)',
                'am_onyx': 'Onyx (Глибокий)',
                'am_puck': 'Puck (Жвавий)'
            },
            'English (GB)': {
                'bf_alice': 'Alice (Британська)',
                'bf_emma': 'Emma (Елегантна)',
                'bf_isabella': 'Isabella (Витончена)',
                'bf_lily': 'Lily (Ніжна)',
                'bm_daniel': 'Daniel (Джентльмен)',
                'bm_fable': 'Fable (Розповідач)',
                'bm_george': 'George (Аристократ)',
                'bm_lewis': 'Lewis (Формальний)'
            },
            'French': {
                'ff_siwis': 'Siwis (Класична французька)'
            },
            'Italian': {
                'if_sara': 'Sara (Італійська жінка)',
                'im_nicola': 'Nicola (Італійський чоловік)'
            },
            'Japanese': {
                'jf_alpha': 'Alpha (Аніме дівчина)',
                'jf_gongitsune': 'Gongitsune (Казкова)',
                'jf_nezumi': 'Nezumi (Миша)',
                'jf_tebukuro': 'Tebukuro (Рукавичка)',
                'jm_kumo': 'Kumo (Хмара)'
            },
            'Chinese': {
                'zf_xiaobei': 'Xiaobei (Північна)',
                'zf_xiaoni': 'Xiaoni (Мила)',
                'zf_xiaoxiao': 'Xiaoxiao (Маленька)',
                'zf_xiaoyi': 'Xiaoyi (Мала)',
                'zm_yunjian': 'Yunjian (Хмарний меч)',
                'zm_yunxi': 'Yunxi (Хмарний захід)',
                'zm_yunxia': 'Yunxia (Хмарна зоря)',
                'zm_yunyang': 'Yunyang (Хмарне сонце)'
            }
        }
        
        self.setup_ui()
        self.initialize_kokoro()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Kokoro TTS Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Voice selection
        voice_frame = ttk.LabelFrame(main_frame, text="Voice Selection", padding="10")
        voice_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        voice_frame.columnconfigure(1, weight=1)
        voice_frame.columnconfigure(3, weight=1)
        
        # Language selection
        ttk.Label(voice_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(voice_frame, textvariable=self.language_var, 
                                          values=list(self.voices.keys()), state="readonly")
        self.language_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Voice selection
        ttk.Label(voice_frame, text="Voice:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly")
        self.voice_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Voice preview button
        self.preview_btn = ttk.Button(voice_frame, text="🔊", width=3, 
                                     command=self.preview_voice,
                                     state=tk.DISABLED)
        self.preview_btn.grid(row=0, column=4, sticky=tk.W)
        
        # Speed control
        ttk.Label(voice_frame, text="Speed:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(voice_frame, from_=0.5, to=2.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL)
        speed_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(10, 0))
        
        self.speed_label = ttk.Label(voice_frame, text="1.0x")
        self.speed_label.grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        speed_scale.configure(command=self.update_speed_label)
        
        # Text input
        text_frame = ttk.LabelFrame(main_frame, text="Text Input", padding="10")
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=70, height=15)
        self.text_area.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Character count and time estimation
        stats_frame = ttk.Frame(text_frame)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        stats_frame.columnconfigure(1, weight=1)
        
        self.char_count_label = ttk.Label(stats_frame, text="Символів: 0")
        self.char_count_label.grid(row=0, column=0, sticky=tk.W)
        
        self.time_estimate_label = ttk.Label(stats_frame, text="Приблизний час: 0 сек")
        self.time_estimate_label.grid(row=0, column=1, sticky=tk.E)
        
        # Generation time estimate
        self.gen_time_label = ttk.Label(stats_frame, text="Час генерації: ~0 сек", foreground="blue")
        self.gen_time_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Bind text change event
        self.text_area.bind('<KeyRelease>', self.update_text_stats)
        self.text_area.bind('<ButtonRelease>', self.update_text_stats)
        self.text_area.bind('<FocusIn>', self.update_text_stats)
        
        # Add context menu for copy/paste
        self.create_context_menu()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Generate button
        self.generate_btn = ttk.Button(button_frame, text="Generate Speech", 
                                      command=self.generate_speech)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Play button
        self.play_btn = ttk.Button(button_frame, text="Play Audio", 
                                  command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_audio, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        self.save_btn = ttk.Button(button_frame, text="Save Audio", 
                                  command=self.save_audio, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W)
        
        # Set default values
        if self.voices:
            self.language_combo.set(list(self.voices.keys())[0])
            self.on_language_change(None)
            
    def initialize_kokoro(self):
        """Initialize Kokoro TTS model"""
        if not KOKORO_AVAILABLE:
            messagebox.showerror("Error", 
                               "Kokoro ONNX library not found. Please install it with:\n"
                               "pip install kokoro-onnx")
            return
            
        # Check for model files
        model_file = "kokoro-v1.0.onnx"
        voices_file = "voices-v1.0.bin"
        
        if not os.path.exists(model_file):
            messagebox.showwarning("Model Not Found", 
                                 f"Model file '{model_file}' not found.\n"
                                 "Please download it from:\n"
                                 "https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx")
            return
            
        if not os.path.exists(voices_file):
            messagebox.showwarning("Voices Not Found", 
                                 f"Voices file '{voices_file}' not found.\n"
                                 "Please download it from:\n"
                                 "https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin")
            return
            
        try:
            self.kokoro = Kokoro(model_file, voices_file)
            self.status_label.config(text="Kokoro TTS initialized successfully")
            
            # Enable preview button if English is selected
            if self.language_var.get().startswith('English'):
                self.preview_btn.config(state=tk.NORMAL)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize Kokoro TTS: {str(e)}")
            
    def create_context_menu(self):
        """Create context menu for text area"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копіювати", command=self.copy_text)
        self.context_menu.add_command(label="Вставити", command=self.paste_text_with_update)
        self.context_menu.add_command(label="Вирізати", command=self.cut_text_with_update)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Вибрати все", command=self.select_all_text)
        self.context_menu.add_command(label="Очистити", command=self.clear_text)
        
        # Bind right-click to show context menu
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
        # Bind keyboard shortcuts
        self.text_area.bind("<Control-c>", lambda e: self.copy_text())
        self.text_area.bind("<Control-v>", lambda e: self.paste_text_with_update())
        self.text_area.bind("<Control-x>", lambda e: self.cut_text_with_update())
        self.text_area.bind("<Control-a>", lambda e: self.select_all_text())
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass
            
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.text_area.event_generate("<<Paste>>")
        except tk.TclError:
            pass
            
    def paste_text_with_update(self):
        """Paste text and update stats"""
        self.paste_text()
        self.root.after(10, self.update_text_stats)  # Small delay to ensure text is pasted
            
    def cut_text(self):
        """Cut selected text to clipboard"""
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass
            
    def cut_text_with_update(self):
        """Cut text and update stats"""
        self.cut_text()
        self.root.after(10, self.update_text_stats)  # Small delay to ensure text is cut
            
    def select_all_text(self):
        """Select all text in text area"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        
    def clear_text(self):
        """Clear all text in text area"""
        self.text_area.delete("1.0", tk.END)
        self.update_text_stats()
        
    def on_language_change(self, event):
        """Update voice options when language changes"""
        language = self.language_var.get()
        if language in self.voices:
            voice_dict = self.voices[language]
            # Show readable names but store technical names as values
            readable_names = list(voice_dict.values())
            self.voice_combo['values'] = readable_names
            if readable_names:
                self.voice_combo.set(readable_names[0])
            
            # Enable preview button only for English languages
            if language.startswith('English') and self.kokoro:
                self.preview_btn.config(state=tk.NORMAL)
            else:
                self.preview_btn.config(state=tk.DISABLED)
                
    def update_speed_label(self, value):
        """Update speed label"""
        self.speed_label.config(text=f"{float(value):.1f}x")
        # Update time estimation when speed changes
        self.update_text_stats()
        
    def update_text_stats(self, event=None):
        """Update character count and time estimation"""
        text = self.text_area.get("1.0", tk.END).strip()
        char_count = len(text)
        
        # Update character count
        self.char_count_label.config(text=f"Символів: {char_count}")
        
        # Estimate reading time
        if char_count == 0:
            self.time_estimate_label.config(text="Приблизний час: 0 сек")
            self.gen_time_label.config(text="Час генерації: ~0 сек")
            return
            
        # Get current speed multiplier
        speed = self.speed_var.get()
        
        # Calculate estimated time
        # Based on real Kokoro TTS performance:
        # 2900 characters = 2:25 (145 seconds) = ~1200 characters per minute
        # We'll use 1200 characters per minute as base (realistic estimate)
        
        base_chars_per_minute = 1200
        estimated_minutes = char_count / base_chars_per_minute
        
        # Adjust for speed setting
        estimated_minutes = estimated_minutes / speed
        
        # Convert to seconds
        estimated_seconds = estimated_minutes * 60
        
        # Format time display
        if estimated_seconds < 60:
            time_text = f"Приблизний час: {estimated_seconds:.0f} сек"
        elif estimated_seconds < 3600:
            minutes = int(estimated_seconds // 60)
            seconds = int(estimated_seconds % 60)
            time_text = f"Приблизний час: {minutes}:{seconds:02d}"
        else:
            hours = int(estimated_seconds // 3600)
            minutes = int((estimated_seconds % 3600) // 60)
            seconds = int(estimated_seconds % 60)
            time_text = f"Приблизний час: {hours}:{minutes:02d}:{seconds:02d}"
            
        self.time_estimate_label.config(text=time_text)
        
        # Calculate generation time estimate
        # Based on testing: roughly 0.15-0.25 seconds per second of audio
        # We'll use 0.2 seconds per second of audio as estimate
        generation_seconds = estimated_seconds * 0.2
        
        if generation_seconds < 60:
            gen_time_text = f"Час генерації: ~{generation_seconds:.0f} сек"
        else:
            gen_minutes = int(generation_seconds // 60)
            gen_seconds = int(generation_seconds % 60)
            gen_time_text = f"Час генерації: ~{gen_minutes}:{gen_seconds:02d}"
            
        self.gen_time_label.config(text=gen_time_text)
        

    def preview_voice(self):
        """Preview selected voice with sample text"""
        if not self.kokoro:
            messagebox.showerror("Error", "Kokoro TTS not initialized")
            return
            
        readable_voice = self.voice_var.get()
        if not readable_voice:
            messagebox.showwarning("Warning", "Please select a voice")
            return
            
        # Get technical voice ID
        voice_id = self.get_voice_id(readable_voice)
        if not voice_id:
            messagebox.showerror("Error", "Invalid voice selection")
            return
            
        # Check if we already have a preview for this voice
        if voice_id in self.preview_samples:
            try:
                pygame.mixer.music.load(self.preview_samples[voice_id])
                pygame.mixer.music.play()
                self.status_label.config(text=f"Playing preview: {readable_voice}")
                return
            except:
                # If file doesn't exist or can't be played, regenerate
                pass
        
        # Generate preview sample
        sample_text = "Hello! This is a voice preview sample. How do you like this voice?"
        
        # Disable preview button during generation
        self.preview_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Generating voice preview...")
        
        # Run generation in separate thread
        threading.Thread(target=self._generate_preview_thread, 
                        args=(sample_text, voice_id, readable_voice), daemon=True).start()
        
    def _generate_preview_thread(self, text, voice_id, readable_voice):
        """Generate voice preview in background thread"""
        try:
            # Generate audio sample
            samples, sample_rate = self.kokoro.create(text, voice=voice_id, speed=1.0)
            
            # Create previews directory if it doesn't exist
            previews_dir = os.path.join(os.getcwd(), "voice_previews")
            os.makedirs(previews_dir, exist_ok=True)
            
            # Save preview file
            preview_file = os.path.join(previews_dir, f"preview_{voice_id}.wav")
            sf.write(preview_file, samples, sample_rate)
            
            # Store in cache
            self.preview_samples[voice_id] = preview_file
            
            # Update UI in main thread
            self.root.after(0, self._preview_complete, preview_file, readable_voice)
            
        except Exception as e:
            self.root.after(0, self._preview_error, str(e))
            
    def _preview_complete(self, preview_file, readable_voice):
        """Handle successful preview generation"""
        try:
            pygame.mixer.music.load(preview_file)
            pygame.mixer.music.play()
            self.status_label.config(text=f"Playing preview: {readable_voice}")
        except Exception as e:
            self.status_label.config(text=f"Preview generation failed: {str(e)}")
        finally:
            self.preview_btn.config(state=tk.NORMAL)
            
    def _preview_error(self, error_msg):
        """Handle preview generation error"""
        self.preview_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Preview generation failed")
        messagebox.showerror("Error", f"Failed to generate voice preview: {error_msg}")
        
    def get_voice_id(self, readable_name):
        """Get technical voice ID from readable name"""
        language = self.language_var.get()
        if language in self.voices:
            voice_dict = self.voices[language]
            for voice_id, readable in voice_dict.items():
                if readable == readable_name:
                    return voice_id
        return None
        
    def generate_speech(self):
        """Generate speech from text"""
        if not self.kokoro:
            messagebox.showerror("Error", "Kokoro TTS not initialized")
            return
            
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to generate speech")
            return
            
        readable_voice = self.voice_var.get()
        if not readable_voice:
            messagebox.showwarning("Warning", "Please select a voice")
            return
            
        # Get technical voice ID
        voice_id = self.get_voice_id(readable_voice)
        if not voice_id:
            messagebox.showerror("Error", "Invalid voice selection")
            return
            
        # Disable buttons during generation
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Generating speech...")
        
        # Record start time for generation measurement
        self.generation_start_time = time.time()
        
        # Run generation in separate thread
        threading.Thread(target=self._generate_speech_thread, 
                        args=(text, voice_id, self.speed_var.get()), daemon=True).start()
        
    def _generate_speech_thread(self, text, voice, speed):
        """Generate speech in background thread"""
        try:
            # Generate audio
            samples, sample_rate = self.kokoro.create(text, voice=voice, speed=speed)
            
            # Calculate actual generation time
            generation_time = time.time() - self.generation_start_time
            
            # Create audio directory if it doesn't exist
            audio_dir = os.path.join(os.getcwd(), "audio_output")
            os.makedirs(audio_dir, exist_ok=True)
            
            # Save to file in audio directory
            timestamp = int(time.time())
            temp_file = os.path.join(audio_dir, f"kokoro_generated_{timestamp}.wav")
            sf.write(temp_file, samples, sample_rate)
            
            # Update UI in main thread
            self.root.after(0, self._generation_complete, temp_file, generation_time)
            
        except Exception as e:
            self.root.after(0, self._generation_error, str(e))
            
    def _generation_complete(self, audio_file, generation_time):
        """Handle successful generation"""
        self.current_audio_file = audio_file
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)

        
        # Update status with actual generation time
        if generation_time < 60:
            time_str = f"{generation_time:.1f} сек"
        else:
            minutes = int(generation_time // 60)
            seconds = generation_time % 60
            time_str = f"{minutes}:{seconds:04.1f}"
            
        self.status_label.config(text=f"Генерація завершена за {time_str}")
        
    def _generation_error(self, error_msg):
        """Handle generation error"""
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Generation failed")
        messagebox.showerror("Error", f"Failed to generate speech: {error_msg}")
        
    def play_audio(self):
        """Play generated audio"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            messagebox.showwarning("Warning", "No audio file to play")
            return
            
        try:
            pygame.mixer.music.load(self.current_audio_file)
            pygame.mixer.music.play()
            self.play_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Playing audio...")
            
            # Check if audio is still playing
            self._check_audio_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")
            
    def _check_audio_status(self):
        """Check if audio is still playing"""
        if pygame.mixer.music.get_busy():
            self.root.after(100, self._check_audio_status)
        else:
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Audio playback finished")
            
    def stop_audio(self):
        """Stop audio playback"""
        pygame.mixer.music.stop()
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Audio stopped")
        
    def save_audio(self):
        """Save generated audio to WAV file"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            messagebox.showwarning("Warning", "No audio file to save")
            return
            
        # Generate default filename based on text and voice
        text = self.text_area.get("1.0", tk.END).strip()
        voice = self.voice_var.get()
        
        # Create safe filename from first few words
        text_preview = text[:50].replace('\n', ' ').replace('\r', ' ')
        # Remove special characters
        safe_text = ''.join(c for c in text_preview if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_text:
            safe_text = "kokoro_speech"
        
        # Get voice name without description
        voice_name = voice.split(' (')[0] if voice else "unknown"
        
        # Create default filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"{safe_text[:30]}_{voice_name}_{timestamp}.wav"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if file_path:
            try:
                # Copy WAV file directly
                import shutil
                shutil.copy2(self.current_audio_file, file_path)
                self.status_label.config(text=f"Audio saved to: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Audio saved to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")
                self.status_label.config(text="Save failed")

def main():
    root = tk.Tk()
    app = KokoroTTSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 