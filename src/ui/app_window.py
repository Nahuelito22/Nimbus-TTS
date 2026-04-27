import customtkinter as ctk
from tkinter import filedialog, messagebox
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
from src.core.piper_engine import PiperEngine
from src.core.kokoro_engine import KokoroEngine
from src.core.ai_manager import AIManager
from src.utils.hotkeys import HotkeyManager
from src.utils.config_manager import ConfigManager
from src.ui.settings_window import SettingsWindow
from tkinterdnd2 import TkinterDnD, DND_FILES
import pystray
from PIL import Image, ImageDraw

ctk.set_appearance_mode("Dark") # Fallback inicial
ctk.set_default_color_theme("blue")

class NimbusApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        
        # Inicializar soporte para Drag & Drop
        self.TkdndVersion = TkinterDnD._require(self)

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
        self.piper_engine = PiperEngine(models_dir=self.config_manager.get("models_path"))
        self.ai_manager = AIManager(self.config_manager)
        self.tts_engine = TTSEngine(
            voice=self.config_manager.get("voice"),
            rate=self.config_manager.get("rate")
        )
        
        self.kokoro_engine = KokoroEngine(self.config_manager.get("models_path"))

        # Estados de texto
        self.original_text = ""
        self.summary_text = ""
        self.current_view = "Original" # "Original" o "Resumen"
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

        # Inicializar System Tray
        self.tray_icon = None
        self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        self.tray_thread.start()
        
        # Interceptar el cierre de ventana (X)
        self.protocol("WM_DELETE_WINDOW", self.withdraw_window)
        
        print("Nimbus-TTS iniciado correctamente.")

    def setup_ui(self):
        # Configurar grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (Configuracin) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Nimbus-TTS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=20)

        # Selector de Modo (Nube / Local)
        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="Modo de Motor:")
        self.mode_label.pack(padx=20, pady=(10, 0))
        
        self.mode_switch = ctk.CTkSegmentedButton(self.sidebar_frame, values=["Nube", "Local"], command=self.change_engine_mode)
        initial_mode = "Local" if self.config_manager.get("use_offline_mode") else "Nube"
        self.mode_switch.set(initial_mode)
        self.mode_switch.pack(padx=20, pady=5, fill="x")

        # Selector de Voz
        self.voice_label = ctk.CTkLabel(self.sidebar_frame, text="Voz:")
        self.voice_label.pack(padx=20, pady=(10, 0))
        
        self.voice_option = ctk.CTkOptionMenu(self.sidebar_frame, values=self._get_voices_for_mode(initial_mode), command=self.change_voice)
        
        # Restaurar la voz guardada
        if initial_mode == "Local":
            saved_local = self.config_manager.get("local_voice")
            if saved_local in self._get_voices_for_mode("Local"):
                self.voice_option.set(saved_local)
        else:
            saved_voice = self.config_manager.get("voice")
            if saved_voice in self._get_voices_for_mode("Nube"):
                self.voice_option.set(saved_voice)
                
        self.voice_option.pack(padx=20, pady=10, fill="x")

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

        # Botón de Configuración
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Configuracion", command=self.open_settings, fg_color="gray25", hover_color="gray35")
        self.settings_button.pack(padx=20, pady=20)

        # --- MAIN CONTENT ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1) # Fila para el textbox

        # Top Bar: Carga de Archivos
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.load_button = ctk.CTkButton(self.top_bar, text="Subir PDF", command=self.load_pdf)
        self.load_button.pack(side="left", padx=5)

        # Historial de Recientes
        self.recent_files = self.config_manager.get("recent_files")
        self.history_menu = ctk.CTkOptionMenu(self.top_bar, values=["Recientes"] + self.recent_files, command=self._load_recent_file)
        self.history_menu.set("Recientes")
        self.history_menu.pack(side="left", padx=5)

        self.summary_btn = ctk.CTkButton(self.top_bar, text="Resumen IA", command=self.generate_ai_summary, fg_color="#7d56f5", hover_color="#6344c7")
        self.summary_btn.pack(side="left", padx=5)

        # Fila 1: Selector de Vista (Oculto hasta que haya texto)
        self.view_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.view_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.view_selector = ctk.CTkSegmentedButton(self.view_frame, values=["Texto Original", "Resumen IA"], command=self._switch_view)
        self.view_selector.set("Texto Original")
        self.view_selector.pack(side="left", padx=5)
        self.view_frame.grid_remove() # Ocultar inicialmente

        # Fila 2: TextBox
        self.textbox = ctk.CTkTextbox(self.main_frame, font=("Inter", 13))
        self.textbox.grid(row=2, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Pega tu texto aqu o sube un PDF...")
        
        # Configurar tag de resaltado
        self.textbox.tag_config("highlight", background="#2a5a8a", foreground="white")

        # Bottom Bar: Controles de Audio
        self.controls_bar = ctk.CTkFrame(self.main_frame, height=80)
        self.controls_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        self.play_button = ctk.CTkButton(self.controls_bar, text="Reproducir", command=self.start_reading)
        self.play_button.pack(side="left", padx=10, pady=10)
        
        self.pause_button = ctk.CTkButton(self.controls_bar, text="Pausar/Reanudar", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=10, pady=10)
        
        self.stop_button = ctk.CTkButton(self.controls_bar, text="Detener", command=self.stop_reading, fg_color="red", hover_color="#b30000")
        self.stop_button.pack(side="left", padx=10, pady=10)

        # Configurar Drag & Drop en toda la ventana o solo en el textbox
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    # --- LGICA DE LA UI ---

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self._process_file(file_path)
            
    def _update_textbox(self, text):
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)

    def _switch_view(self, view_name):
        self.stop_reading()
        if view_name == "Texto Original":
            self.current_view = "Original"
            self._update_textbox(self.original_text)
        else:
            self.current_view = "Resumen"
            if self.summary_text:
                self._update_textbox(self.summary_text)
            else:
                self._update_textbox("No hay resumen generado todavía. Pulsa 'Resumen IA'.")

    def generate_ai_summary(self):
        text_to_summarize = self.original_text or self.textbox.get("0.0", "end").strip()
        if not text_to_summarize or len(text_to_summarize) < 50:
            print("Texto demasiado corto para resumir.")
            return

        def _thread_logic():
            self.summary_btn.configure(state="disabled", text="Generando...")
            resumen, modelo = self.ai_manager.summarize(text_to_summarize)
            
            if resumen:
                self.summary_text = f"--- RESUMEN GENERADO POR {modelo.upper()} ---\n\n{resumen}"
                self.current_view = "Resumen"
                self.after(0, lambda: self.view_selector.set("Resumen IA"))
                self.after(0, lambda: self._update_textbox(self.summary_text))
                self.after(0, lambda: self.view_frame.grid())
            else:
                self.after(0, lambda: messagebox.showerror("Error de IA", "No se pudo generar el resumen. Verifica tus API Keys en Ajustes."))
            
            self.after(0, lambda: self.summary_btn.configure(state="normal", text="Resumen IA"))

        threading.Thread(target=_thread_logic, daemon=True).start()

    def handle_drop(self, event):
        """Maneja el evento de soltar un archivo en la ventana."""
        file_path = event.data
        
        # En Windows, las rutas con espacios vienen encerradas en {}
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        if file_path.lower().endswith(".pdf"):
            self._process_file(file_path)
        else:
            print("Archivo no soportado (solo PDF)")

    def _process_file(self, file_path):
        """Procesa y carga el texto de un archivo PDF."""
        raw_text = extract_text_from_pdf(file_path)
        clean_text = self.text_manager.clean_text(raw_text)
        
        self.original_text = clean_text
        self.summary_text = ""
        self.current_view = "Original"
        self.view_selector.set("Texto Original")
        self.view_frame.grid()
        self._update_textbox(clean_text)
        
        # Actualizar historial
        self._update_history(file_path)

    def _update_history(self, file_path):
        """Actualiza la lista de archivos recientes."""
        history = self.config_manager.get("recent_files") or []
        if file_path in history:
            history.remove(file_path)
        history.insert(0, file_path)
        history = history[:5] # Guardar últimos 5
        self.config_manager.set("recent_files", history)
        
        # Actualizar menú
        self.history_menu.configure(values=["Recientes"] + history)
        self.history_menu.set("Recientes")

    def _load_recent_file(self, file_path):
        """Carga un archivo desde el historial."""
        if file_path == "Recientes":
            return
            
        if os.path.exists(file_path):
            self._process_file(file_path)
        else:
            messagebox.showerror("Error", "El archivo ya no existe en esa ubicación.")
            # Opcional: eliminar del historial
            history = self.config_manager.get("recent_files")
            if file_path in history:
                history.remove(file_path)
                self.config_manager.set("recent_files", history)
                self.history_menu.configure(values=["Recientes"] + history)

    def start_reading(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            return
        
        # Detener cualquier lectura activa y limpiar
        self.stop_reading()
        self.stop_event.clear()
        self.is_paused = False
        
        # Limpiar resaltados previos
        self.textbox.tag_remove("highlight", "1.0", "end")
        
        # Tomar valores actuales
        # Actualizamos desde la configuracin del manager para asegurar consistencia
        is_offline = self.config_manager.get("use_offline_mode")
        if not is_offline:
            self.tts_engine.voice = self.config_manager.get("voice")
            
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
                
            ext = ".wav" if self.config_manager.get("use_offline_mode") else ".mp3"
            temp_file = os.path.join(self.temp_dir, f"temp_chunk_{i}{ext}")
            self.current_temp_files.append(temp_file)
            
            # Generar audio (Online u Offline) basado en la selección actual
            if self.config_manager.get("use_offline_mode"):
                full_voice_id = self.config_manager.get("local_voice")
                
                if "[Premium] Kokoro" in full_voice_id:
                    success = self.kokoro_engine.generate_audio(chunk['text'], temp_file)
                else:
                    # Limpiar el prefijo [Piper] para obtener el ID real del archivo
                    real_voice_id = full_voice_id.replace("[Piper] ", "")
                    success = self.piper_engine.generate_audio(chunk['text'], temp_file, real_voice_id)
                
                if not success:
                    print(f"Error: Falló la síntesis local con {full_voice_id}.")
            else:
                success = loop.run_until_complete(self.tts_engine.generate_audio(chunk['text'], temp_file))
                
            if success and not self.stop_event.is_set():
                self.audio_queue.put((temp_file, chunk['start'], chunk['end']))

    def _consumer_thread(self):
        """Reproduce los archivos de audio de la cola en orden."""
        while not self.stop_event.is_set():
            try:
                # Espera hasta 1 segundo por un nuevo archivo
                audio_data = self.audio_queue.get(timeout=1.0)
                audio_file, start_idx, end_idx = audio_data
            except queue.Empty:
                continue

            if self.stop_event.is_set():
                break

            # Resaltar texto en el hilo principal
            self.after(0, lambda s=start_idx, e=end_idx: self._highlight_text(s, e))

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
        
        # Limpiar resaltado
        self.textbox.tag_remove("highlight", "1.0", "end")
        
        # Vaciar la cola
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        # Limpieza de archivos temporales
        self._cleanup_temp_files()

    def _highlight_text(self, start, end):
        """Resalta el texto y hace scroll hasta la posicin."""
        self.textbox.tag_remove("highlight", "1.0", "end")
        
        # Convertir offsets de caracteres a ndices de tkinter (linea.columna)
        start_idx = f"1.0 + {start}c"
        end_idx = f"1.0 + {end}c"
        
        self.textbox.tag_add("highlight", start_idx, end_idx)
        self.textbox.see(start_idx)

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
    
    def _get_voices_for_mode(self, mode):
        """Devuelve las voces correspondientes al modo seleccionado con prefijos claros."""
        if mode == "Local":
            # Voces de Piper con prefijo
            voices = [f"[Piper] {v}" for v in self.piper_engine.list_local_voices()]
            
            # Añadir Kokoro si está instalado
            if self.kokoro_engine.is_installed():
                voices.append("[Premium] Kokoro")
                
            return voices if voices else ["Sin voces descargadas"]
        else:
            return self.tts_engine.list_voices()

    def update_voice_options(self):
        """Refresca la lista de voces en la ventana principal (llamado desde Ajustes)."""
        mode = "Local" if self.config_manager.get("use_offline_mode") else "Nube"
        new_values = self._get_voices_for_mode(mode)
        self.voice_option.configure(values=new_values)

    def change_engine_mode(self, mode):
        """Cambia entre el motor de la nube y el motor local."""
        is_offline = (mode == "Local")
        self.config_manager.set("use_offline_mode", is_offline)
        
        # Actualizar lista de voces
        new_values = self._get_voices_for_mode(mode)
        self.voice_option.configure(values=new_values)
        
        # Seleccionar la voz guardada para ese modo
        if is_offline:
            saved_local = self.config_manager.get("local_voice")
            if saved_local in new_values:
                self.voice_option.set(saved_local)
            else:
                self.voice_option.set(new_values[0])
        else:
            saved_voice = self.config_manager.get("voice")
            if saved_voice in new_values:
                self.voice_option.set(saved_voice)
            else:
                self.voice_option.set(new_values[0])
            self.tts_engine.voice = self.voice_option.get()

    def change_voice(self, new_voice):
        if self.mode_switch.get() == "Local":
            if new_voice != "Sin voces descargadas":
                self.config_manager.set("local_voice", new_voice)
        else:
            self.config_manager.set("voice", new_voice)
            self.tts_engine.voice = new_voice

    def change_speed(self, speed):
        rate = f"{'+' if int(speed) >= 0 else ''}{int(speed)}%"
        self.config_manager.set("rate", rate)

    def open_settings(self):
        # Abrir la ventana de configuraciones
        settings_win = SettingsWindow(self, self.config_manager, self.hotkey_manager)
        settings_win.grab_set() # Hacerla modal (bloquea la principal hasta cerrar)

    def setup_tray(self):
        """Inicializa el icono de la bandeja del sistema."""
        try:
            menu = pystray.Menu(
                pystray.MenuItem("Mostrar Nimbus", self.show_window, default=True),
                pystray.MenuItem("Reproducir/Pausar", self.toggle_pause),
                pystray.MenuItem("Detener", self.stop_reading),
                pystray.MenuItem("Salir", self.quit_app)
            )
            
            icon_img = self._create_tray_icon_image()
            self.tray_icon = pystray.Icon("nimbus_tts", icon_img, "Nimbus-TTS", menu)
            self.tray_icon.run()
        except Exception as e:
            print(f"Error al iniciar el tray: {e}")

    def _create_tray_icon_image(self):
        """Crea una imagen simple para el icono del tray."""
        width = 64
        height = 64
        # Fondo oscuro
        image = Image.new('RGB', (width, height), (30, 30, 30))
        dc = ImageDraw.Draw(image)
        # Círculo azul Nimbus
        dc.ellipse([8, 8, 56, 56], fill=(42, 90, 138))
        return image

    def withdraw_window(self):
        """Oculta la ventana principal y la envía al tray."""
        self.withdraw()
        
    def show_window(self, icon=None, item=None):
        """Muestra la ventana principal."""
        self.after(0, self.deiconify)
        self.after(0, self.focus_force)

    def quit_app(self, icon=None, item=None):
        """Cierra la aplicación completamente."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.destroy)

    def destroy(self):
        """Sobrescribimos destroy para limpiar hotkeys, archivos y tray."""
        print("Cerrando Nimbus-TTS y limpiando temporales...")
        if self.tray_icon:
            self.tray_icon.stop()
            
        self.stop_reading()
        self.hotkey_manager.stop_listening()
        
        # Intento final de borrar toda la carpeta temp
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass
            
        super().destroy()

if __name__ == "__main__":
    app = NimbusApp()
    app.mainloop()
