import tkinter as tk
from tkinter import ttk
from deep_translator import GoogleTranslator
import threading
from gtts import gTTS
import os
import tempfile
import pygame
import time
import speech_recognition as sr
import atexit
from gtts.lang import tts_langs


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Translator")
        self.root.geometry("720x700")
        self.root.minsize(600, 600)
        self.root.configure(bg="#f5f5f5")

        try:
            self.root.iconbitmap("translator_icon.ico")
        except:
            pass

        # Audio and temp file management
        self.audio_files = []
        self.setup_audio()
        self.setup_translator()
        self.setup_ui()
        self.center_window()

        # Cleanup on exit
        atexit.register(self.cleanup)

    def cleanup(self):
        """Clean up temporary audio files"""
        for file in self.audio_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

    # ----------------------- AUDIO SETUP -----------------------
    def setup_audio(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
            pygame.mixer.music.set_volume(1.0)
        except Exception as e:
            self.status_label.config(
                text=f"⚠️ Audio system might not work: {str(e)}", foreground="#FF9800"
            )

    def setup_translator(self):
        try:
            self.translator = GoogleTranslator(source="english", target="hindi")
            self.languages_dict = self.translator.get_supported_languages(as_dict=True)
            self.languages = sorted(list(self.languages_dict.keys()))

            # Get supported TTS languages
            self.tts_languages = tts_langs()

        except Exception as e:
            self.status_label.config(
                text=f"⚠️ Failed to initialize translator: {str(e)}",
                foreground="#FF9800",
            )
            self.languages_dict = {"english": "en", "hindi": "hi"}  # Fallback
            self.languages = list(self.languages_dict.keys())
            self.tts_languages = {"en": "English", "hi": "Hindi"}

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.current_audio_file = None

    # ----------------------- UTILITIES -----------------------
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def animate_status(self, message, color):
        """Animated status with dots"""

        def _animate():
            for i in range(6):
                self.status_label.config(text=message + "." * (i % 4), foreground=color)
                self.root.update()
                time.sleep(0.4)

        threading.Thread(target=_animate, daemon=True).start()

    # ----------------------- TRANSLATION -----------------------
    def translate_text(self, text: str, src="english", dest="hindi"):
        if not text.strip():
            return ""

        # Normalize language names
        src = src.lower()
        dest = dest.lower()

        try:
            # Check if languages are supported
            if src not in self.languages_dict:
                self.status_label.config(
                    text=f"⚠️ Source language '{src}' not supported",
                    foreground="#FF9800",
                )
                return ""

            if dest not in self.languages_dict:
                self.status_label.config(
                    text=f"⚠️ Target language '{dest}' not supported",
                    foreground="#FF9800",
                )
                return ""

            return GoogleTranslator(source=src, target=dest).translate(text)

        except Exception as e:
            self.status_label.config(
                text=f"⚠️ Translation error: {str(e)}", foreground="#FF9800"
            )
            return ""

    def perform_translation(self):
        src_lang = self.src_lang.get()
        dest_lang = self.dest_lang.get()
        text = self.source_text.get(1.0, tk.END).strip()
        if not text:
            return

        def _translate():
            self.translate_btn.config(state=tk.DISABLED, text="Translating...")
            self.animate_status("Translating", "#FF9800")

            try:
                translated = self.translate_text(text, src_lang, dest_lang)
                if translated:
                    self.dest_text.delete(1.0, tk.END)
                    self.dest_text.insert(tk.END, translated)
                    self.status_label.config(
                        text="✅ Translation complete!", foreground="#4CAF50"
                    )
            finally:
                self.translate_btn.config(state=tk.NORMAL, text="TRANSLATE →")
                self.root.after(3000, lambda: self.status_label.config(text=""))

        threading.Thread(target=_translate, daemon=True).start()

    # ----------------------- SPEECH -----------------------
    def speak_text(self, text, language):
        if not text.strip():
            return

        def _speak():
            try:
                # Stop any currently playing audio
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

                # Close any open file handles
                if hasattr(self, "current_audio_file") and self.current_audio_file:
                    try:
                        if os.path.exists(self.current_audio_file):
                            pygame.mixer.music.unload()
                    except:
                        pass

                # Get language code with fallback to English
                lang_name = language.lower()
                lang_code = self.languages_dict.get(lang_name, "en")

                # Check if TTS is supported for this language
                if lang_code not in self.tts_languages:
                    self.status_label.config(
                        text=f"⚠️ TTS not available for {language}, using English",
                        foreground="#FF9800",
                    )
                    lang_code = "en"  # Fallback to English

                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                    temp_file = fp.name
                    try:
                        tts = gTTS(text=text, lang=lang_code, slow=False)
                        tts.save(temp_file)
                    except Exception as e:
                        self.status_label.config(
                            text=f"⚠️ Could not generate speech: {str(e)}",
                            foreground="#FF9800",
                        )
                        return

                    # Track the file for cleanup
                    self.audio_files.append(temp_file)
                    self.current_audio_file = temp_file

                # Ensure file is fully written and closed before loading
                time.sleep(0.1)

                try:
                    pygame.mixer.music.load(self.current_audio_file)
                    pygame.mixer.music.play()

                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)

                except Exception as e:
                    self.status_label.config(
                        text=f"⚠️ Could not play audio: {str(e)}", foreground="#FF9800"
                    )

            except Exception as e:
                self.status_label.config(
                    text=f"⚠️ Could not speak: {str(e)}", foreground="#FF9800"
                )

        threading.Thread(target=_speak, daemon=True).start()

    def start_voice_input(self):
        if self.listening:
            return

        def _listen():
            self.listening = True
            self.voice_btn.config(text="🎙️ Listening...", bg="#FF5722", fg="white")
            self.status_label.config(
                text="🎤 Adjusting microphone...", foreground="#FF5722"
            )
            self.root.update()

            try:
                with self.microphone as source:
                    self.recognizer.dynamic_energy_threshold = True
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.5)

                    self.status_label.config(
                        text="🎧 Listening... Speak clearly", foreground="#4285F4"
                    )
                    self.root.update()

                    audio = self.recognizer.listen(
                        source, timeout=5, phrase_time_limit=8
                    )

                    self.status_label.config(
                        text="⌛ Processing speech...", foreground="#FF9800"
                    )
                    self.root.update()

                    try:
                        lang_name = self.src_lang.get().lower()
                        lang_code = self.languages_dict.get(lang_name, "en")

                        # Check if speech recognition is supported for this language
                        if lang_code not in [
                            "en",
                            "hi",
                            "es",
                            "fr",
                            "de",
                            "it",
                            "pt",
                            "ru",
                            "zh-CN",
                            "ja",
                            "ko",
                        ]:
                            self.status_label.config(
                                text="⚠️ Speech recognition may not work for this language",
                                foreground="#FF9800",
                            )
                            lang_code = "en"  # Fallback to English

                        text = self.recognizer.recognize_google(
                            audio, language=lang_code
                        )

                        if text.strip():
                            self.source_text.delete(1.0, tk.END)
                            self.source_text.insert(tk.END, text.capitalize())
                            self.status_label.config(
                                text="✅ Voice input successful!", foreground="#4CAF50"
                            )
                            self.perform_translation()
                        else:
                            self.status_label.config(
                                text="⚠️ No speech detected", foreground="#F44336"
                            )

                    except sr.UnknownValueError:
                        self.status_label.config(
                            text="❌ Could not understand audio", foreground="#F44336"
                        )
                    except sr.RequestError as e:
                        self.status_label.config(
                            text=f"🚫 API Error: {e}", foreground="#F44336"
                        )

            except Exception as e:
                self.status_label.config(
                    text=f"⚠️ Error: {str(e)}", foreground="#F44336"
                )

            finally:
                self.listening = False
                self.voice_btn.config(text="🎤 Voice Input", bg="#4CC210", fg="white")
                self.root.after(3000, lambda: self.status_label.config(text=""))

        threading.Thread(target=_listen, daemon=True).start()

    # ----------------------- UI -----------------------
    def swap_languages(self):
        src, dest = self.src_lang.get(), self.dest_lang.get()
        self.src_lang.set(dest)
        self.dest_lang.set(src)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(main_frame, bg="#4CC210", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            header_frame,
            text=" Translator",
            font=("Arial", 20, "bold"),
            bg="#4CC210",
            fg="white",
        ).pack(pady=15)

        # Source Section with scrollbar
        source_frame = tk.LabelFrame(
            main_frame,
            text=" Source Text ",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            bd=2,
            relief=tk.GROOVE,
            padx=5,
            pady=5,
        )
        source_frame.pack(fill=tk.BOTH, pady=(0, 10), expand=True)

        # Create a frame for text and scrollbar
        text_frame = tk.Frame(source_frame, bg="#ffffff")
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar to source text
        scroll_source = tk.Scrollbar(text_frame)
        scroll_source.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_text = tk.Text(
            text_frame,
            height=6,
            font=("Arial", 11),
            wrap=tk.WORD,
            bd=1,
            relief=tk.SOLID,
            padx=8,
            pady=8,
            yscrollcommand=scroll_source.set,
        )
        self.source_text.pack(fill=tk.BOTH, expand=True)

        scroll_source.config(command=self.source_text.yview)

        # Button frame for source section
        source_btn_frame = tk.Frame(source_frame, bg="#ffffff")
        source_btn_frame.pack(fill=tk.X, pady=(5, 5))

        # Centered container for buttons
        button_container = tk.Frame(source_btn_frame, bg="#ffffff")
        button_container.pack(expand=True)

        self.voice_btn = tk.Button(
            button_container,
            text="Voice Input",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            bd=0,
            padx=12,
            pady=6,
            relief="flat",
            activebackground="#45a049",
            activeforeground="white",
            command=self.start_voice_input,
        )
        self.voice_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Add Speak Source button
        tk.Button(
            button_container,
            text="Speak Source",
            font=("Arial", 10, "bold"),
            bg="#64B5F6",
            fg="white",
            bd=0,
            padx=12,
            pady=6,
            relief="flat",
            activebackground="#5d9cec",
            activeforeground="white",
            command=lambda: self.speak_text(
                self.source_text.get(1.0, tk.END).strip(), self.src_lang.get()
            ),
        ).pack(side=tk.LEFT)

        lang_controls = tk.Frame(source_frame, bg="#ffffff")
        lang_controls.pack(fill=tk.X, pady=(0, 0))

        tk.Label(lang_controls, text="From:", font=("Arial", 9), bg="#ffffff").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.src_lang = tk.StringVar(value="english")
        self.src_combobox = ttk.Combobox(
            lang_controls,
            textvariable=self.src_lang,
            values=self.languages,
            font=("Arial", 9),
            width=16,
            state="readonly",
        )
        self.src_combobox.pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            lang_controls,
            text="<──────────────────>",
            font=("Arial", 10, "bold"),
            bg="#4CC210",
            fg="white",
            bd=0,
            command=self.swap_languages,  # keep your function
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(lang_controls, text="To:", font=("Arial", 9), bg="#ffffff").pack(
            side=tk.LEFT, padx=(2, 5)
        )
        self.dest_lang = tk.StringVar(value="hindi")
        self.dest_combobox = ttk.Combobox(
            lang_controls,
            textvariable=self.dest_lang,
            values=self.languages,
            font=("Arial", 9),
            width=16,
            state="readonly",
        )
        self.dest_combobox.pack(side=tk.LEFT)

        self.translate_btn = tk.Button(
            lang_controls,
            text="TRANSLATE →",
            font=("Arial", 10, "bold"),
            bg="#4CC210",
            fg="white",
            bd=0,
            padx=15,
            command=self.perform_translation,
        )
        self.translate_btn.pack(side=tk.RIGHT)

        # Destination Section with scrollbar
        dest_frame = tk.LabelFrame(
            main_frame,
            text=" Translated Text ",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            bd=2,
            relief=tk.GROOVE,
            padx=5,
            pady=5,
        )
        dest_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for text and scrollbar
        dest_text_frame = tk.Frame(dest_frame, bg="#ffffff")
        dest_text_frame.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar to destination text
        scroll_dest = tk.Scrollbar(dest_text_frame)
        scroll_dest.pack(side=tk.RIGHT, fill=tk.Y)

        self.dest_text = tk.Text(
            dest_text_frame,
            height=6,
            font=("Arial", 11),
            wrap=tk.WORD,
            bd=1,
            relief=tk.SOLID,
            padx=8,
            pady=8,
            yscrollcommand=scroll_dest.set,
        )
        self.dest_text.pack(fill=tk.BOTH, expand=True)

        scroll_dest.config(command=self.dest_text.yview)

        # Button frame for destination section
        dest_btn_frame = tk.Frame(dest_frame, bg="#ffffff")
        dest_btn_frame.pack(fill=tk.X, pady=(5, 5))

        tk.Button(
            dest_btn_frame,
            text="Speak Translation",
            font=("Arial", 10, "bold"),
            bg="#64B5F6",
            fg="white",
            bd=0,
            padx=12,
            pady=5,
            command=lambda: self.speak_text(
                self.dest_text.get(1.0, tk.END).strip(), self.dest_lang.get()
            ),
        ).pack()

        # Status Bar
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#4285F4",
            height=1,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

        # Footer
        tk.Label(
            main_frame,
            text="© 2025 Translator | Powered by Google Translate API\n Made By Om Bhabal",
            font=("Arial", 8),
            fg="#757575",
            bg="#f5f5f5",
        ).pack(pady=(5, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
