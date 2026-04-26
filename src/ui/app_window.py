import customtkinter as ctk
from tkinter import filedialog
import os
import asyncio
import threading

# Importaciones locales de la capa Core
from src.core.pdf_parser import extract_text_from_pdf
from src.core.text_manager import TextManager
from src.core.tts_engine import TTSEngine
from src.core.audio_player import AudioPlayer
from src.utils.hotkeys import HotkeyManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NimbusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nimbus-TTS - Estudio Inteligente")
        self.geometry("900x600")

        # Inicializar componentes lógicos
        self.audio_player = AudioPlayer()
        self.tts_engine = TTSEngine()
        self.text_manager = TextManager()
        
        # Inicializar y arrancar Hotkeys
        self.hotkey_manager = HotkeyManager(
            play_pause_callback=self.toggle_pause,
            stop_callback=self.stop_reading
        )
        self.hotkey_manager.start()
        
        self.setup_ui()

    def setup_ui(self):
        # Configurar grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (Configuracin) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Nimbus-TTS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=20)

        # Seleccin de Voz
        self.voice_label = ctk.CTkLabel(self.sidebar_frame, text="Seleccionar Voz:")
        self.voice_label.pack(padx=20, pady=(10, 0))
        
        self.voice_option = ctk.CTkOptionMenu(self.sidebar_frame, values=self.tts_engine.list_voices())
        self.voice_option.pack(padx=20, pady=10)

        # Velocidad
        self.speed_label = ctk.CTkLabel(self.sidebar_frame, text="Velocidad:")
        self.speed_label.pack(padx=20, pady=(10, 0))
        
        self.speed_slider = ctk.CTkSlider(self.sidebar_frame, from_=-50, to=50, number_of_steps=10)
        self.speed_slider.set(0)
        self.speed_slider.pack(padx=20, pady=10)

        # --- MAIN CONTENT ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Top Bar: Carga de Archivos
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.load_button = ctk.CTkButton(self.top_bar, text="Subir PDF", command=self.load_pdf)
        self.load_button.pack(side="left", padx=5)

        # Middle: TextBox
        self.textbox = ctk.CTkTextbox(self.main_frame, font=("Inter", 13))
        self.textbox.grid(row=1, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Pega tu texto aqu o sube un PDF...")

        # Bottom Bar: Controles de Audio
        self.controls_bar = ctk.CTkFrame(self.main_frame, height=80)
        self.controls_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.play_button = ctk.CTkButton(self.controls_bar, text="Reproducir", command=self.start_reading)
        self.play_button.pack(side="left", padx=10, pady=10)
        
        self.pause_button = ctk.CTkButton(self.controls_bar, text="Pausar/Reanudar", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=10, pady=10)
        
        self.stop_button = ctk.CTkButton(self.controls_bar, text="Detener", command=self.stop_reading, fg_color="red", hover_color="#b30000")
        self.stop_button.pack(side="left", padx=10, pady=10)

    # --- LGICA DE LA UI ---

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            text = extract_text_from_pdf(file_path)
            clean_text = self.text_manager.clean_text(text)
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", clean_text)

    def start_reading(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            return
        
        voice = self.voice_option.get()
        speed_val = int(self.speed_slider.get())
        rate = f"{'+' if speed_val >= 0 else ''}{speed_val}%"
        
        self.tts_engine.voice = voice
        self.tts_engine.rate = rate
        
        # Ejecutar generacin en un hilo separado para no bloquear la UI
        threading.Thread(target=self._generate_and_play, args=(text,), daemon=True).start()

    def _generate_and_play(self, text):
        temp_file = "temp_audio.mp3"
        # Usar un loop de asyncio para el hilo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(self.tts_engine.generate_audio(text, temp_file))
        if success:
            self.audio_player.load(temp_file)
            self.audio_player.play()

    def toggle_pause(self):
        if self.audio_player.is_playing():
            self.audio_player.pause()
        else:
            self.audio_player.unpause()

    def stop_reading(self):
        self.audio_player.stop()

    def destroy(self):
        """Sobrescribimos destroy para limpiar hotkeys."""
        self.hotkey_manager.stop_listening()
        super().destroy()

if __name__ == "__main__":
    app = NimbusApp()
    app.mainloop()
