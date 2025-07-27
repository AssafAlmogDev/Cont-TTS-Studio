import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
print("Starting this may take 20-120 seconds.")
print("Tips in ko-fi.com/assafusa553")
import subprocess
import threading
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
from TTS.api import TTS
import uuid
import logging
import re
from num2words import num2words
import numpy as np

def run_gui():
    import logging
    import tkinter.messagebox as messagebox
    try:
        import numpy as np  # Required for recording
        app = CoquiApp()
        app.mainloop()
    except ImportError as e:
        logging.error(f"Missing required module: {str(e)}")
        messagebox.showerror("Fatal Error", f"Missing required module: {str(e)}. Please install numpy.")
    except Exception as e:
        logging.error(f"Application failed to start: {str(e)}")
        messagebox.showerror("Fatal Error", f"contTTS Studio failed to start: {str(e)}")


# Set up logging
logging.basicConfig(filename='contTTS_studio.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Professional color palette
PRIMARY_COLOR = "#1A2634"  # Dark navy (main background)
SECONDARY_COLOR = "#3A4A5A"  # Soft gray (secondary elements)
ACCENT_COLOR = "#2A8290"  # Professional teal (highlights)
TEXT_COLOR = "#F5F6F5"  # Off-white (general text)
HIGHLIGHT_COLOR = "#A3BFFA"  # Light blue (active states)
ERROR_COLOR = "#E57373"  # Soft red (errors)
DROPDOWN_TEXT_COLOR = "#000000"  # Black (dropdown text)
SHADE_LIGHT = "#4B5E74"  # Lighter shade for panels
SHADE_DARK = "#15202B"  # Darker shade for subtle contrasts
BORDER_COLOR = "#6B8299"  # Border shade for separation

VOICE_DIR = "voices"
TRAIN_DIR = "train_samples"

os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(TRAIN_DIR, exist_ok=True)

def convert_numbers_to_words(text):
    """Convert numbers in text to their word equivalents."""
    try:
        def replace_number(match):
            num = match.group(0)
            try:
                if '.' in num:
                    integer_part, decimal_part = num.split('.')
                    integer_words = num2words(int(integer_part), lang='en')
                    decimal_words = num2words(int(decimal_part), lang='en')
                    return f"{integer_words} point {decimal_words}"
                return num2words(int(num), lang='en')
            except (ValueError, TypeError):
                return num
        converted_text = re.sub(r'\b\d+(\.\d+)?\b', replace_number, text)
        logging.info(f"Converted numbers to words: {text} -> {converted_text}")
        return converted_text
    except Exception as e:
        logging.error(f"Number to words conversion failed: {str(e)}")
        return text

class CoquiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.info("Initializing contTTS Studio")
        try:
            self.title("contTTS Studio")
            self.attributes('-fullscreen', False)
            self.state('zoomed')
            self.configure(bg=PRIMARY_COLOR)
            self.tts_model = "tts_models/multilingual/multi-dataset/your_tts"
            self.voice_models = self._get_voice_models()
            self._set_styles()
            self._create_widgets()
            self._create_loading_screen()
            logging.info("Application initialized successfully")
        except Exception as e:
            logging.error(f"Initialization failed: {str(e)}")
            messagebox.showerror("Startup Error", f"Failed to start contTTS Studio: {str(e)}")
            self.destroy()

    def _set_styles(self):
        try:
            style = ttk.Style(self)
            style.theme_use("clam")
            style.configure("TNotebook", background=PRIMARY_COLOR, borderwidth=0, tabmargins=[0, 0, 0, 0])
            style.configure("TNotebook.Tab", background=SHADE_DARK, foreground=TEXT_COLOR, 
                           padding=[20, 12], font=("Segoe UI", 13, "bold"), bordercolor=BORDER_COLOR)
            style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], 
                     foreground=[("selected", TEXT_COLOR)], expand=[("selected", [0, 0, 0, 2])])
            style.configure("TFrame", background=PRIMARY_COLOR)
            style.configure("TLabel", background=PRIMARY_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 12))
            style.configure("TButton", background=ACCENT_COLOR, foreground=TEXT_COLOR, 
                           padding=10, font=("Segoe UI", 12, "bold"), bordercolor=BORDER_COLOR)
            style.map("TButton", background=[("active", HIGHLIGHT_COLOR)], foreground=[("active", TEXT_COLOR)])
            style.configure("TEntry", fieldbackground=SHADE_LIGHT, foreground=TEXT_COLOR, 
                           font=("Segoe UI", 12), bordercolor=BORDER_COLOR)
            style.configure("TCombobox", fieldbackground=SHADE_LIGHT, foreground=DROPDOWN_TEXT_COLOR, 
                           font=("Segoe UI", 12))
            style.map("TCombobox", fieldbackground=[("readonly", SHADE_LIGHT)], 
                     selectbackground=[("readonly", SHADE_LIGHT)], 
                     selectforeground=[("readonly", DROPDOWN_TEXT_COLOR)])
            style.configure("Vertical.TScrollbar", background=SHADE_DARK, troughcolor=PRIMARY_COLOR, 
                           arrowcolor=TEXT_COLOR, bordercolor=BORDER_COLOR)
            logging.info("Styles configured successfully")
        except Exception as e:
            logging.error(f"Style configuration failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to configure styles: {str(e)}")

    def _create_loading_screen(self):
        try:
            self.loading_frame = tk.Frame(self, bg=PRIMARY_COLOR)
            self.loading_label = tk.Label(self.loading_frame, text="Processing...", 
                                        font=("Segoe UI", 16, "bold"), bg=PRIMARY_COLOR, fg=TEXT_COLOR)
            self.loading_label.pack(pady=20)
            self.loading_frame.place_forget()
            self.loading_frame.bind("<Configure>", lambda e: self._center_loading())
            logging.info("Loading screen created")
        except Exception as e:
            logging.error(f"Loading screen setup failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to set up loading screen: {str(e)}")

    def _center_loading(self):
        try:
            self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
            logging.info("Loading screen centered")
        except Exception as e:
            logging.error(f"Failed to center loading screen: {str(e)}")
            messagebox.showerror("Error", f"Failed to center loading screen: {str(e)}")

    def _create_widgets(self):
        try:
            main_frame = ttk.Frame(self)
            main_frame.pack(expand=1, fill="both", padx=30, pady=30)

            header_frame = ttk.Frame(main_frame, style="TFrame")
            header_frame.pack(fill="x", pady=(0, 20))
            ttk.Label(header_frame, text="contTTS Studio", font=("Segoe UI", 24, "bold"), 
                     background=SHADE_DARK, foreground=TEXT_COLOR, padding=10).pack(fill="x")

            self.tabs = ttk.Notebook(main_frame)
            self.tts_tab = TTSFrame(self.tabs, self)
            self.clone_tab = CloneFrame(self.tabs, self)
            self.voices_tab = VoicesFrame(self.tabs, self)
            self.about_tab = AboutFrame(self.tabs, self)
            
            self.tabs.add(self.tts_tab, text="Text-to-Speech")
            self.tabs.add(self.clone_tab, text="Voice Cloning")
            self.tabs.add(self.voices_tab, text="Voice Management")
            self.tabs.add(self.about_tab, text="About")
            self.tabs.pack(expand=1, fill="both")

            logging.info("Widgets created successfully")
        except Exception as e:
            logging.error(f"Widget creation failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to create widgets: {str(e)}")

    def _get_voice_models(self):
        try:
            models = [f[:-4] for f in os.listdir(VOICE_DIR) if f.endswith(".wav")]
            logging.info(f"Voice models loaded: {models}")
            return models
        except Exception as e:
            logging.error(f"Failed to load voice models: {str(e)}")
            messagebox.showerror("Error", f"Failed to load voices: {str(e)}")
            return []

    def refresh_voices(self):
        try:
            self.voice_models = self._get_voice_models()
            self.tts_tab.update_voices()
            self.voices_tab.update_voice_list()
            logging.info("Voices refreshed")
        except Exception as e:
            logging.error(f"Voice refresh failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh voices: {str(e)}")

    def show_loading(self, text="Processing..."):
        try:
            self.loading_label.config(text=text)
            self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.update()
            logging.info(f"Showing loading screen: {text}")
        except Exception as e:
            logging.error(f"Failed to show loading screen: {str(e)}")
            messagebox.showerror("Error", f"Failed to show loading screen: {str(e)}")

    def hide_loading(self):
        try:
            self.loading_frame.place_forget()
            logging.info("Hiding loading screen")
        except Exception as e:
            logging.error(f"Failed to hide loading screen: {str(e)}")
            messagebox.showerror("Error", f"Failed to hide loading screen: {str(e)}")

class TTSFrame(ttk.Frame):
    def __init__(self, container, app):
        super().__init__(container)
        self.app = app
        try:
            self.tts = TTS(model_name=self.app.tts_model, gpu=False)
            logging.info("TTS model initialized")
        except Exception as e:
            logging.error(f"TTS initialization failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize TTS: {str(e)}")
            return

        self.voice_var = tk.StringVar()
        self.lang_var = tk.StringVar(value="en")
        
        content_frame = ttk.Frame(self, style="TFrame", padding=20)
        content_frame.pack(expand=1, fill="both")

        ttk.Label(content_frame, text="Text to Synthesize:", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        text_frame = ttk.Frame(content_frame, style="TFrame", relief="flat")
        text_frame.pack(padx=10, pady=5, fill="both")
        self.text_entry = tk.Text(text_frame, height=10, wrap=tk.WORD, bg=SHADE_LIGHT, 
                                 fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=("Segoe UI", 12), 
                                 relief="flat", borderwidth=1)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_entry.yview)
        self.text_entry.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text_entry.pack(side="left", fill="both", expand=True)

        control_frame = ttk.Frame(content_frame, style="TFrame")
        control_frame.pack(pady=20, fill="x")

        ttk.Label(control_frame, text="Voice:").grid(row=0, column=0, padx=(0, 15))
        self.voice_dropdown = ttk.Combobox(control_frame, textvariable=self.voice_var, 
                                          state="readonly", width=25)
        self.voice_dropdown.grid(row=0, column=1, padx=(0, 30))

        ttk.Label(control_frame, text="Language:").grid(row=0, column=2, padx=(0, 15))
        ttk.Entry(control_frame, textvariable=self.lang_var, width=8).grid(row=0, column=3, padx=(0, 30))

        button_frame = ttk.Frame(control_frame, style="TFrame")
        button_frame.grid(row=0, column=4, columnspan=2)
        ttk.Button(button_frame, text="Speak", command=self.speak).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Download", command=self.download).pack(side="left", padx=10)

        self.update_voices()
        logging.info("TTSFrame initialized")

    def update_voices(self):
        try:
            self.voice_dropdown['values'] = self.app.voice_models
            if self.app.voice_models:
                self.voice_var.set(self.app.voice_models[0])
            logging.info("Voices updated in TTSFrame")
        except Exception as e:
            logging.error(f"Failed to update voices in TTSFrame: {str(e)}")
            messagebox.showerror("Error", f"Failed to update voices: {str(e)}")

    def speak(self):
        threading.Thread(target=self._speak_thread, daemon=True).start()

    def _speak_thread(self):
        try:
            self._synthesize("temp_play.wav")
            subprocess.call(["start", "temp_play.wav"], shell=True)
            logging.info("Audio played successfully")
        except Exception as e:
            logging.error(f"Speak failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")

    def download(self):
        try:
            file = filedialog.asksaveasfilename(defaultextension=".mp3",
                                               filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav"), ("M4A", "*.m4a")])
            if file:
                threading.Thread(target=self._download_thread, args=(file,), daemon=True).start()
        except Exception as e:
            logging.error(f"Download selection failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to select file: {str(e)}")

    def _download_thread(self, file):
        try:
            self._synthesize(file)
            logging.info(f"Audio downloaded to {file}")
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to download: {str(e)}")

    def _synthesize(self, out_file):
        try:
            text = self.text_entry.get("1.0", tk.END).strip()
            if not text:
                self.app.hide_loading()
                messagebox.showerror("Error", "Please enter text to synthesize.")
                logging.warning("No text provided for synthesis")
                return
            text = convert_numbers_to_words(text)
            speaker = os.path.join(VOICE_DIR, self.voice_var.get() + ".wav")
            self.app.show_loading("Synthesizing audio...")
            self.tts.tts_to_file(text=text, speaker_wav=speaker, file_path=out_file, 
                                language=self.lang_var.get())
            logging.info(f"Synthesized audio to {out_file}")
        except Exception as e:
            self.app.hide_loading()
            logging.error(f"Synthesis failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to synthesize: {str(e)}")
        finally:
            self.app.hide_loading()

class CloneFrame(ttk.Frame):
    def __init__(self, container, app):
        super().__init__(container)
        self.app = app
        self.sample_paths = []
        self.name_var = tk.StringVar()
        self.is_recording = False
        self.recording_thread = None
        self.recording = None

        content_frame = ttk.Frame(self, style="TFrame", padding=20)
        content_frame.pack(expand=1, fill="both")

        ttk.Label(content_frame, text="Voice Cloning", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        name_frame = ttk.Frame(content_frame, style="TFrame")
        name_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(name_frame, text="Voice Name:").pack(side="left")
        ttk.Entry(name_frame, textvariable=self.name_var, width=35).pack(side="left", padx=15)

        button_frame = ttk.Frame(content_frame, style="TFrame")
        button_frame.pack(pady=15)
        ttk.Button(button_frame, text="Upload Sample", command=self.upload_sample).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Start Recording", command=self.start_recording).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Stop Recording", command=self.stop_recording).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_sample).grid(row=0, column=3, padx=10)

        ttk.Label(content_frame, text="Audio Samples:").pack(pady=(10, 5))
        listbox_frame = ttk.Frame(content_frame, style="TFrame")
        listbox_frame.pack(padx=10, pady=5, fill="both")
        self.sample_listbox = tk.Listbox(listbox_frame, height=8, bg=SHADE_LIGHT, fg=TEXT_COLOR, 
                                        font=("Segoe UI", 11), relief="flat", borderwidth=1)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.sample_listbox.yview)
        self.sample_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sample_listbox.pack(side="left", fill="both", expand=True)

        ttk.Button(content_frame, text="Clone Voice", command=self.clone_voice).pack(pady=20)
        logging.info("CloneFrame initialized")

    def upload_sample(self):
        try:
            files = filedialog.askopenfilenames(filetypes=[("Audio/Video", "*.mp4 *.wav")])
            for f in files:
                name = f"{uuid.uuid4()}.wav"
                wav_path = os.path.join(TRAIN_DIR, name)
                if f.endswith(".mp4"):
                    self.app.show_loading("Converting video to audio...")
                    AudioSegment.from_file(f).export(wav_path, format="wav")
                else:
                    self.app.show_loading("Copying audio file...")
                    shutil.copy(f, wav_path)
                self.sample_paths.append(wav_path)
                self.sample_listbox.insert(tk.END, os.path.basename(f))
                logging.info(f"Uploaded sample: {f}")
            self.app.hide_loading()
        except Exception as e:
            self.app.hide_loading()
            logging.error(f"Failed to upload sample: {str(e)}")
            messagebox.showerror("Error", f"Failed to add sample: {str(e)}")

    def start_recording(self):
        try:
            if self.is_recording:
                messagebox.showinfo("Info", "Recording is already in progress.")
                return
            self.is_recording = True
            fs = 44100
            messagebox.showinfo("Recording", "Recording started. Click 'Stop Recording' to finish.")
            self.app.show_loading("Recording audio...")
            self.recording = []
            self.recording_thread = threading.Thread(target=self._record_thread, args=(fs,), daemon=True)
            self.recording_thread.start()
            logging.info("Started recording")
        except Exception as e:
            self.is_recording = False
            self.app.hide_loading()
            logging.error(f"Failed to start recording: {str(e)}")
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def _record_thread(self, fs):
        try:
            stream = sd.InputStream(samplerate=fs, channels=1)
            stream.start()
            while self.is_recording:
                data = stream.read(1024)[0]
                self.recording.append(data)
            stream.stop()
            stream.close()
        except Exception as e:
            self.is_recording = False
            self.app.hide_loading()
            logging.error(f"Recording thread failed: {str(e)}")
            messagebox.showerror("Error", f"Recording failed: {str(e)}")

    def stop_recording(self):
        try:
            if not self.is_recording:
                messagebox.showinfo("Info", "No recording is in progress.")
                return
            self.is_recording = False
            self.recording_thread.join()
            fs = 44100
            name = f"recorded_{uuid.uuid4()}.wav"
            wav_path = os.path.join(TRAIN_DIR, name)
            recording_array = np.concatenate(self.recording)
            sf.write(wav_path, recording_array, fs)
            self.sample_paths.append(wav_path)
            self.sample_listbox.insert(tk.END, name)
            self.recording = None
            self.app.hide_loading()
            logging.info(f"Stopped recording and saved: {name}")
            messagebox.showinfo("Success", "Recording saved successfully.")
        except Exception as e:
            self.app.hide_loading()
            logging.error(f"Failed to stop recording: {str(e)}")
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")

    def delete_sample(self):
        try:
            selected = self.sample_listbox.curselection()
            if selected:
                index = selected[0]
                os.remove(self.sample_paths[index])
                logging.info(f"Deleted sample: {self.sample_paths[index]}")
                del self.sample_paths[index]
                self.sample_listbox.delete(index)
        except Exception as e:
            logging.error(f"Failed to delete sample: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete sample: {str(e)}")

    def clone_voice(self):
        try:
            if not self.name_var.get():
                messagebox.showerror("Error", "Please provide a voice name.")
                logging.warning("No voice name provided")
                return
            if not self.sample_paths:
                messagebox.showerror("Error", "Please upload or record at least one audio sample.")
                logging.warning("No audio samples provided")
                return
            self.app.show_loading("Cloning voice...")
            combined = AudioSegment.empty()
            for path in self.sample_paths:
                combined += AudioSegment.from_file(path)
            out_path = os.path.join(VOICE_DIR, f"{self.name_var.get()}.wav")
            combined.export(out_path, format="wav")
            self.sample_paths.clear()
            self.sample_listbox.delete(0, tk.END)
            self.app.refresh_voices()
            messagebox.showinfo("Success", "Voice cloned successfully!")
            logging.info(f"Voice cloned: {out_path}")
        except Exception as e:
            logging.error(f"Voice cloning failed: {str(e)}")
            messagebox.showerror("Error", f"Cloning failed: {str(e)}")
        finally:
            self.app.hide_loading()

class VoicesFrame(ttk.Frame):
    def __init__(self, container, app):
        super().__init__(container)
        self.app = app
        self.voice_var = tk.StringVar()

        content_frame = ttk.Frame(self, style="TFrame", padding=20)
        content_frame.pack(expand=1, fill="both")

        ttk.Label(content_frame, text="Voice Management", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        voice_frame = ttk.Frame(content_frame, style="TFrame")
        voice_frame.pack(pady=15, padx=10, fill="x")
        ttk.Label(voice_frame, text="Available Voices:").pack(side="left")
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, 
                                         state="readonly", width=35)
        self.voice_dropdown.pack(side="left", padx=15)

        ttk.Button(content_frame, text="Delete Voice", command=self.delete_voice).pack(pady=20)

        self.update_voice_list()
        logging.info("VoicesFrame initialized")

    def update_voice_list(self):
        try:
            self.voice_dropdown['values'] = self.app.voice_models
            if self.app.voice_models:
                self.voice_var.set(self.app.voice_models[0])
            logging.info("Voice list updated in VoicesFrame")
        except Exception as e:
            logging.error(f"Failed to update voice list: {str(e)}")
            messagebox.showerror("Error", f"Failed to update voice list: {str(e)}")

    def delete_voice(self):
        try:
            voice = self.voice_var.get()
            if not voice:
                messagebox.showerror("Error", "No voice selected.")
                logging.warning("No voice selected for deletion")
                return
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{voice}'?")
            if confirm:
                self.app.show_loading("Deleting voice...")
                os.remove(os.path.join(VOICE_DIR, voice + ".wav"))
                self.app.refresh_voices()
                messagebox.showinfo("Success", f"Voice '{voice}' deleted successfully.")
                logging.info(f"Voice deleted: {voice}")
        except Exception as e:
            logging.error(f"Failed to delete voice: {str(e)}")
            messagebox.showerror("Error", f"Could not delete: {str(e)}")
        finally:
            self.app.hide_loading()

class AboutFrame(ttk.Frame):
    def __init__(self, container, app):
        super().__init__(container)
        self.app = app

        content_frame = ttk.Frame(self, style="TFrame", padding=20)
        content_frame.pack(expand=1, fill="both")

        ttk.Label(content_frame, text="About contTTS Studio", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        ttk.Label(content_frame, text="contTTS Studio was made using open-source Coqui TTS.", 
                 font=("Segoe UI", 12, "italic"), foreground=TEXT_COLOR, background=PRIMARY_COLOR, 
                 wraplength=600).pack(pady=10)
        
        ttk.Label(content_frame, text="Using MLCommons/peoples_speech voices for the pre-installed.", 
                 font=("Segoe UI", 12, "italic"), foreground=HIGHLIGHT_COLOR, background=PRIMARY_COLOR, 
                 wraplength=600).pack(pady=10)
        
        ttk.Label(content_frame, text="Tip me at ko-fi.com/asafusa553", 
                 font=("Segoe UI", 12, "italic"), foreground=HIGHLIGHT_COLOR, background=PRIMARY_COLOR, 
                 wraplength=600).pack(pady=10)

        logging.info("AboutFrame initialized")

if __name__ == '__main__':
    run_gui()