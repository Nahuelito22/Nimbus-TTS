import customtkinter as ctk
from tkinter import filedialog
import os
import asyncio
import threading
import queue
import time
import shutil

# Importaciones locales de la capa Core
from src.core.pdf_parser import extract_text_from_pdf
from src.core.text_manager import TextManager
from src.core.tts_engine import TTSEngine
from src.core.audio_player import AudioPlayer
from src.utils.hotkeys import HotkeyManager
from src.utils.config_manager import ConfigManager
from src.ui.settings_window import SettingsWindow

ctk.set_appearance_mode("Dark") # Fallback inicial
ctk.set_default_color_theme("blue")

class NimbusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nimbus-TTS - Estudio Inteligente")
        self.geometry("900x600")

        # Inicializar gestor de configuracin
        self.config_manager = ConfigManager()
        ctk.set_appearance_mode(self.config_manager.get("appearance_mode"))

        # Configurar carpeta temporal
        self.temp_dir = os.path.join(os.getcwd(), "temp")
        self._init_temp_dir()

        # Inicializar componentes lógicos
        self.audio_player = AudioPlayer()
        self.tts_engine = TTSEngine(
            voice=self.config_manager.get("voice"),
            rate=self.config_manager.get("rate")
        )
        self.text_manager = TextManager()
        
        # Variables de control de reproduccin por fragmentos
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.is_paused = False
        self.current_temp_files = []
        
        # Inicializar y arrancar Hotkeys con la config guardada
        self.hotkey_manager = HotkeyManager(
            play_pause_callback=self.toggle_pause,
            stop_callback=self.stop_reading
        )
        self.hotkey_manager.update_hotkeys(
            self.config_manager.get("hotkey_play_pause"),
            self.config_manager.get("hotkey_stop")
        )
        
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
        
        self.voice_option = ctk.CTkOptionMenu(self.sidebar_frame, values=self.tts_engine.list_voices(), command=self.change_voice)
        self.voice_option.set(self.config_manager.get("voice"))
        self.voice_option.pack(padx=20, pady=10)

        # Velocidad
        self.speed_label = ctk.CTkLabel(self.sidebar_frame, text="Velocidad:")
        self.speed_label.pack(padx=20, pady=(10, 0))
        
        # Convertir rate string (e.g. "+10%") a float para el slider
        rate_str = self.config_manager.get("rate").replace("%", "")
        initial_speed = int(rate_str) if rate_str else 0
        
        self.speed_slider = ctk.CTkSlider(self.sidebar_frame, from_=-50, to=50, number_of_steps=10, command=self.change_speed)
        self.speed_slider.set(initial_speed)
        self.speed_slider.pack(padx=20, pady=10)

        # Espacio flexible para empujar el botn de ajustes al fondo
        self.sidebar_spacer = ctk.CTkLabel(self.sidebar_frame, text="")
        self.sidebar_spacer.pack(expand=True, fill="both")

        # Botn de Configuracin
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Configuracin", command=self.open_settings, fg_color="gray25", hover_color="gray35")
        self.settings_button.pack(padx=20, pady=20)

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
        
        # Detener cualquier lectura activa y limpiar
        self.stop_reading()
        self.stop_event.clear()
        self.is_paused = False
        
        # Tomar valores actuales
        self.tts_engine.voice = self.voice_option.get()
        speed_val = int(self.speed_slider.get())
        self.tts_engine.rate = f"{'+' if speed_val >= 0 else ''}{speed_val}%"

        # Dividir el texto en fragmentos (chunks)
        chunks = self.text_manager.get_chunks(text, max_chars=800)
        
        # Iniciar hilos Productor (Genera TTS) y Consumidor (Reproduce)
        threading.Thread(target=self._producer_thread, args=(chunks,), daemon=True).start()
        threading.Thread(target=self._consumer_thread, daemon=True).start()

    def _producer_thread(self, chunks):
        """Genera los archivos de audio en segundo plano y los encola."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for i, chunk in enumerate(chunks):
            if self.stop_event.is_set():
                break
                
            temp_file = os.path.join(self.temp_dir, f"temp_chunk_{i}.mp3")
            self.current_temp_files.append(temp_file)
            
            # Generar audio
            success = loop.run_until_complete(self.tts_engine.generate_audio(chunk, temp_file))
            if success and not self.stop_event.is_set():
                self.audio_queue.put(temp_file)

    def _consumer_thread(self):
        """Reproduce los archivos de audio de la cola en orden."""
        while not self.stop_event.is_set():
            try:
                # Espera hasta 1 segundo por un nuevo archivo, si no hay sigue comprobando stop_event
                audio_file = self.audio_queue.get(timeout=1.0)
            except queue.Empty:
                # Si la cola est vaca pero el productor termin (ya no hay ms chunks), salimos
                # (Una mejora futura es sealizar el fin desde el productor, por ahora usamos el timeout)
                continue

            if self.stop_event.is_set():
                break

            # Cargar y reproducir el chunk
            if self.audio_player.load(audio_file):
                self.audio_player.play()

                # Esperar a que termine de reproducir este chunk
                while (self.audio_player.is_playing() or self.is_paused) and not self.stop_event.is_set():
                    time.sleep(0.1)

            self.audio_queue.task_done()

    def toggle_pause(self):
        if self.audio_player.is_playing():
            self.audio_player.pause()
            self.is_paused = True
        else:
            self.audio_player.unpause()
            self.is_paused = False

    def stop_reading(self):
        self.stop_event.set()
        self.is_paused = False
        self.audio_player.stop()
        
        # Vaciar la cola
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        # Limpieza de archivos temporales (opcional, en un hilo pequeo para evitar demoras)
        threading.Thread(target=self._cleanup_temp_files, daemon=True).start()

    def _cleanup_temp_files(self):
        """Intenta borrar los archivos temporales actuales."""
        time.sleep(0.5) # Dar tiempo a que el player libere el archivo
        for f in list(self.current_temp_files):
            try:
                if os.path.exists(f):
                    os.remove(f)
                    if f in self.current_temp_files:
                        self.current_temp_files.remove(f)
            except Exception:
                pass

    def _init_temp_dir(self):
        """Crea la carpeta temp si no existe y la limpia al iniciar."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            print(f"Error al inicializar carpeta temporal: {e}")

    # --- CONFIGURACIN ---
    
    def change_voice(self, voice):
        self.config_manager.set("voice", voice)

    def change_speed(self, speed):
        rate = f"{'+' if int(speed) >= 0 else ''}{int(speed)}%"
        self.config_manager.set("rate", rate)

    def open_settings(self):
        # Abrir la ventana de configuraciones
        settings_win = SettingsWindow(self, self.config_manager, self.hotkey_manager)
        settings_win.grab_set() # Hacerla modal (bloquea la principal hasta cerrar)

    def destroy(self):
        """Sobrescribimos destroy para limpiar hotkeys y archivos."""
        self.stop_reading()
        self.hotkey_manager.stop_listening()
        super().destroy()

if __name__ == "__main__":
    app = NimbusApp()
    app.mainloop()
