import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import tempfile
import pygame
import soundfile as sf
from pathlib import Path

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
        self.voice_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
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
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize Kokoro TTS: {str(e)}")
            
    def create_context_menu(self):
        """Create context menu for text area"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копіювати", command=self.copy_text)
        self.context_menu.add_command(label="Вставити", command=self.paste_text)
        self.context_menu.add_command(label="Вирізати", command=self.cut_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Вибрати все", command=self.select_all_text)
        self.context_menu.add_command(label="Очистити", command=self.clear_text)
        
        # Bind right-click to show context menu
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
        # Bind keyboard shortcuts
        self.text_area.bind("<Control-c>", lambda e: self.copy_text())
        self.text_area.bind("<Control-v>", lambda e: self.paste_text())
        self.text_area.bind("<Control-x>", lambda e: self.cut_text())
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
            
    def cut_text(self):
        """Cut selected text to clipboard"""
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass
            
    def select_all_text(self):
        """Select all text in text area"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        
    def clear_text(self):
        """Clear all text in text area"""
        self.text_area.delete("1.0", tk.END)
        
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
                
    def update_speed_label(self, value):
        """Update speed label"""
        self.speed_label.config(text=f"{float(value):.1f}x")
        
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
        
        # Run generation in separate thread
        threading.Thread(target=self._generate_speech_thread, 
                        args=(text, voice_id, self.speed_var.get()), daemon=True).start()
        
    def _generate_speech_thread(self, text, voice, speed):
        """Generate speech in background thread"""
        try:
            # Generate audio
            samples, sample_rate = self.kokoro.create(text, voice=voice, speed=speed)
            
            # Create audio directory if it doesn't exist
            audio_dir = os.path.join(os.getcwd(), "audio_output")
            os.makedirs(audio_dir, exist_ok=True)
            
            # Save to file in audio directory
            import time
            timestamp = int(time.time())
            temp_file = os.path.join(audio_dir, f"kokoro_generated_{timestamp}.wav")
            sf.write(temp_file, samples, sample_rate)
            
            # Update UI in main thread
            self.root.after(0, self._generation_complete, temp_file)
            
        except Exception as e:
            self.root.after(0, self._generation_error, str(e))
            
    def _generation_complete(self, audio_file):
        """Handle successful generation"""
        self.current_audio_file = audio_file
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Speech generated successfully")
        
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
        """Save generated audio to file"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            messagebox.showwarning("Warning", "No audio file to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Copy temporary file to selected location
                import shutil
                shutil.copy2(self.current_audio_file, file_path)
                messagebox.showinfo("Success", f"Audio saved to: {file_path}")
                self.status_label.config(text=f"Audio saved to: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")

def main():
    root = tk.Tk()
    app = KokoroTTSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 