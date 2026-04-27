import customtkinter as ctk
from src.core.piper_engine import PiperEngine
import threading

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_manager, hotkey_manager):
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        self.piper_engine = parent.piper_engine # Usar la instancia de la app principal
        
        self.title("Configuracion de Nimbus-TTS")
        self.geometry("500x650")
        self.after(100, self.lift)
        
        self.after(100, self.lift)
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        # Crear Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_general = self.tabview.add("General")
        self.tab_models = self.tabview.add("Voces Locales (HF)")
        self.tabview.add("Inteligencia Artificial")
        self.tabview.set("General")
        
        self._setup_general_tab()
        self._setup_models_tab()
        self._setup_ai_tab()

    def _setup_general_tab(self):
        # Usar un Frame desplazable para evitar que se corten los elementos
        self.scroll_general = ctk.CTkScrollableFrame(self.tab_general, fg_color="transparent")
        self.scroll_general.pack(fill="both", expand=True)
        
        tab = self.scroll_general
        tab.grid_columnconfigure(0, weight=1)
        padx, pady = 20, 10

        # --- APARIENCIA ---
        ctk.CTkLabel(tab, text="Apariencia", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=padx, pady=(20, 5), sticky="w")
        
        self.appearance_mode_option = ctk.CTkOptionMenu(tab, values=["System", "Dark", "Light"], command=self.change_appearance_mode)
        self.appearance_mode_option.set(self.config_manager.get("appearance_mode"))
        self.appearance_mode_option.grid(row=1, column=0, padx=padx, pady=pady, sticky="ew")
        
        # --- ATAJOS DE TECLADO ---
        ctk.CTkLabel(tab, text="Atajos de Teclado", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=padx, pady=(20, 5), sticky="w")
        
        ctk.CTkLabel(tab, text="Reproducir / Pausar:").grid(row=3, column=0, padx=padx, pady=(5, 0), sticky="w")
        self.pp_entry = ctk.CTkEntry(tab)
        self.pp_entry.insert(0, self.config_manager.get("hotkey_play_pause"))
        self.pp_entry.grid(row=4, column=0, padx=padx, pady=pady, sticky="ew")
        
        ctk.CTkLabel(tab, text="Detener:").grid(row=5, column=0, padx=padx, pady=(5, 0), sticky="w")
        self.stop_entry = ctk.CTkEntry(tab)
        self.stop_entry.insert(0, self.config_manager.get("hotkey_stop"))
        self.stop_entry.grid(row=6, column=0, padx=padx, pady=pady, sticky="ew")
        
        # Botón Guardar
        self.save_button = ctk.CTkButton(tab, text="Guardar Cambios", command=self.save_and_close)
        self.save_button.grid(row=7, column=0, padx=padx, pady=30, sticky="ew")

    def _setup_models_tab(self):
        # Usar un Frame desplazable para evitar que se corten los elementos
        self.scroll_models = ctk.CTkScrollableFrame(self.tab_models, fg_color="transparent")
        self.scroll_models.pack(fill="both", expand=True)
        
        tab = self.scroll_models
        tab.grid_columnconfigure(0, weight=1)
        padx, pady = 20, 10

        ctk.CTkLabel(tab, text="Gestor de Modelos (Hugging Face)", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=padx, pady=(10, 5), sticky="w")
        
        # Texto explicativo
        info_text = ("Piper es un motor TTS optimizado para funcionar sin internet (Offline). "
                     "Estos modelos descargan archivos pequeños (.onnx) que corren muy rápido en tu CPU. "
                     "En el futuro se podrían soportar motores más pesados.")
        
        ctk.CTkLabel(tab, text=info_text, wraplength=450, justify="left", text_color="gray").grid(row=1, column=0, padx=padx, pady=(0, 15), sticky="w")
        
        # Voces disponibles para descargar (Carga asíncrona)
        self.available_voices = ["Cargando catálogo..."]
        
        ctk.CTkLabel(tab, text="Descargar nueva voz:").grid(row=2, column=0, padx=padx, pady=(5, 0), sticky="w")
        self.download_option = ctk.CTkOptionMenu(tab, values=self.available_voices)
        self.download_option.grid(row=3, column=0, padx=padx, pady=pady, sticky="ew")
        
        # Lanzar hilo para cargar voces
        threading.Thread(target=self._load_remote_voices, daemon=True).start()
        
        self.btn_download = ctk.CTkButton(tab, text="Descargar de Hugging Face", command=self._start_download)
        self.btn_download.grid(row=4, column=0, padx=padx, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(tab, text="", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=padx, pady=2)

        # Voces locales ya descargadas
        ctk.CTkLabel(tab, text="Voces locales instaladas:", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, padx=padx, pady=(20, 5), sticky="w")
        
        self.local_voices_option = ctk.CTkOptionMenu(tab, values=self._get_local_voices_list(), state="disabled")
        self.local_voices_option.set("Revisa el menú de la ventana principal")
        self.local_voices_option.grid(row=7, column=0, padx=padx, pady=pady, sticky="ew")

        # --- CARPETA DE MODELOS ---
        ctk.CTkLabel(tab, text="Carpeta de Almacenamiento:", font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, padx=padx, pady=(20, 5), sticky="w")
        
        self.path_entry = ctk.CTkEntry(tab, placeholder_text="Selecciona carpeta...")
        self.path_entry.insert(0, self.config_manager.get("models_path"))
        self.path_entry.configure(state="readonly")
        self.path_entry.grid(row=9, column=0, padx=padx, pady=(0, 5), sticky="ew")
        
        self.btn_browse = ctk.CTkButton(tab, text="Cambiar Carpeta", fg_color="gray30", command=self._browse_models_dir)
        self.btn_browse.grid(row=10, column=0, padx=padx, pady=5, sticky="ew")

    def _setup_ai_tab(self):
        tab = self.tabview.tab("Inteligencia Artificial")
        tab.grid_columnconfigure(0, weight=1)
        padx, pady = 20, 10

        ctk.CTkLabel(tab, text="Configuración de Resúmenes", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=padx, pady=(15, 5), sticky="w")
        ctk.CTkLabel(tab, text="Configura tus llaves de API para usar IA.", text_color="gray").grid(row=1, column=0, padx=padx, pady=(0, 15), sticky="w")

        # --- GEMINI ---
        ctk.CTkLabel(tab, text="Google Gemini API Key:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=padx, pady=(10, 0), sticky="w")
        self.gemini_entry = ctk.CTkEntry(tab, placeholder_text="AIza...", show="*")
        self.gemini_entry.insert(0, self.config_manager.get("gemini_api_key"))
        self.gemini_entry.grid(row=3, column=0, padx=padx, pady=5, sticky="ew")

        # --- OPENAI ---
        ctk.CTkLabel(tab, text="OpenAI API Key:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=padx, pady=(10, 0), sticky="w")
        self.openai_entry = ctk.CTkEntry(tab, placeholder_text="sk-...", show="*")
        self.openai_entry.insert(0, self.config_manager.get("openai_api_key"))
        self.openai_entry.grid(row=5, column=0, padx=padx, pady=5, sticky="ew")

        # --- PREFERENCIA ---
        ctk.CTkLabel(tab, text="Proveedor Preferido:", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, padx=padx, pady=(15, 0), sticky="w")
        self.ai_provider_option = ctk.CTkOptionMenu(tab, values=["Gemini", "OpenAI"])
        self.ai_provider_option.set(self.config_manager.get("preferred_ai_provider"))
        self.ai_provider_option.grid(row=7, column=0, padx=padx, pady=5, sticky="ew")

        # Info de Fallback
        info_text = "💡 Nimbus intentará usar tu proveedor preferido.\nSi falla (sin créditos o error), intentará con el otro\nautomáticamente."
        ctk.CTkLabel(tab, text=info_text, text_color="gray", justify="left").grid(row=8, column=0, padx=padx, pady=20, sticky="w")

    def _get_local_voices_list(self):
        list_v = self.piper_engine.list_local_voices()
        return list_v if list_v else ["Ninguna descargada"]

    def _start_download(self):
        voice = self.download_option.get()
        self.status_label.configure(text=f"Descargando {voice}... (esto puede tardar)", text_color="blue")
        self.btn_download.configure(state="disabled")
        
        threading.Thread(target=self._download_thread, args=(voice,), daemon=True).start()

    def _download_thread(self, voice):
        success = self.piper_engine.download_voice(voice)
        if success:
            self.after(0, lambda: self._on_download_success(voice))
        else:
            self.after(0, lambda: self._on_download_error())

    def _on_download_success(self, voice):
        self.status_label.configure(text=f"¡{voice} descargada correctamente!", text_color="green")
        self.btn_download.configure(state="normal")
        self.local_voices_option.configure(values=self._get_local_voices_list())
        self.local_voices_option.set(voice)
        self.config_manager.set("local_voice", voice)

    def _on_download_error(self):
        self.status_label.configure(text="Error en la descarga. Revisa tu conexión.", text_color="red")
        self.btn_download.configure(state="normal")


    def _browse_models_dir(self):
        from tkinter import filedialog
        new_dir = filedialog.askdirectory(initialdir=self.config_manager.get("models_path"))
        if new_dir:
            self.config_manager.set("models_path", new_dir)
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, new_dir)
            self.path_entry.configure(state="readonly")
            
            # Actualizar motor
            self.piper_engine.update_models_dir(new_dir)
            # Actualizar lista de voces descargadas
            self.local_voices_option.configure(values=self._get_local_voices_list())
            # Actualizar UI principal si es posible
            if hasattr(self.parent, "change_engine_mode"):
                self.parent.change_engine_mode(self.parent.mode_switch.get())

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        self.config_manager.set("appearance_mode", new_appearance_mode)

    def save_and_close(self):
        # Guardar atajos
        self.config_manager.set("hotkey_play_pause", self.pp_entry.get())
        self.config_manager.set("hotkey_stop", self.stop_entry.get())
        
        # Guardar IA
        self.config_manager.set("gemini_api_key", self.gemini_entry.get())
        self.config_manager.set("openai_api_key", self.openai_entry.get())
        self.config_manager.set("preferred_ai_provider", self.ai_provider_option.get())
        
        # Guardar y cerrar
        self.config_manager.save_config()
        self.hotkey_manager.update_hotkeys(self.pp_entry.get().strip().lower(), self.stop_entry.get().strip().lower())
        self.destroy()
    def _load_remote_voices(self):
        """Carga el catálogo de voces desde Hugging Face en segundo plano."""
        try:
            voices = self.piper_engine.get_available_spanish_voices()
            if voices:
                self.available_voices = voices
                self.after(0, lambda: self.download_option.configure(values=self.available_voices))
                self.after(0, lambda: self.download_option.set(self.available_voices[0]))
            else:
                self.after(0, lambda: self.download_option.configure(values=["Error al cargar catálogo"]))
        except Exception as e:
            print(f"Error cargando voces remotas: {e}")
            self.after(0, lambda: self.download_option.configure(values=["Error de conexión"]))
