import customtkinter as ctk
from src.core.piper_engine import PiperEngine
import threading

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_manager, hotkey_manager):
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        self.piper_engine = parent.piper_engine
        self.kokoro_engine = parent.kokoro_engine
        
        # Mapeo de labels a IDs
        self.voice_label_to_id = {}
        
        # Carga inicial rápida de caché
        cached_voices = self.piper_engine.get_cached_voices_if_any()
        if cached_voices:
            self._build_available_labels(cached_voices)
        else:
            self.available_voices_labels = ["Cargando catálogo..."]
        
        self.title("Configuración de Nimbus-TTS")
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

        # --- TÍTULO Y DESCRIPCIÓN ---
        ctk.CTkLabel(tab, text="Gestor de Modelos Offline", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=padx, pady=(15, 5), sticky="w")
        desc = "Descarga voces para leer sin internet. Tienes voces Estándar (Piper) y calidad Premium (Kokoro)."
        ctk.CTkLabel(tab, text=desc, wraplength=450, justify="left", text_color="gray").grid(row=1, column=0, padx=padx, pady=(0, 20), sticky="w")
        
        # --- 1. DESCARGAR ---
        ctk.CTkLabel(tab, text="1. Descargar nueva voz:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=padx, pady=(5, 5), sticky="w")
        
        self.download_option = ctk.CTkOptionMenu(tab, values=self.available_voices_labels)
        self.download_option.grid(row=3, column=0, padx=padx, pady=5, sticky="ew")
        
        self.btn_download = ctk.CTkButton(tab, text="Descargar Voz Seleccionada", command=self._start_download)
        self.btn_download.grid(row=4, column=0, padx=padx, pady=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(tab, text="", text_color="#3498db")
        self.status_label.grid(row=5, column=0, padx=padx, pady=0)

        # --- 2. DESCARGADOS ---
        ctk.CTkLabel(tab, text="2. Voces ya descargadas:", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, padx=padx, pady=(20, 5), sticky="w")
        
        self.local_voices_option = ctk.CTkOptionMenu(tab, values=self._get_local_voices_list())
        self.local_voices_option.grid(row=7, column=0, padx=padx, pady=5, sticky="ew")

        # --- 3. CARPETA ---
        ctk.CTkLabel(tab, text="3. Carpeta de Almacenamiento", font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, padx=padx, pady=(25, 5), sticky="w")
        
        self.path_entry = ctk.CTkEntry(tab)
        self.path_entry.insert(0, self.piper_engine.models_dir)
        self.path_entry.configure(state="readonly")
        self.path_entry.grid(row=9, column=0, padx=padx, pady=5, sticky="ew")
        
        self.btn_browse = ctk.CTkButton(tab, text="Cambiar Ubicación", fg_color="gray30", command=self._browse_models_dir)
        self.btn_browse.grid(row=10, column=0, padx=padx, pady=(5, 20), sticky="ew")

        # Hilo para cargar el catálogo completo
        threading.Thread(target=self._load_remote_voices, daemon=True).start()

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
        # Listar voces de Piper con prefijo
        piper_v = [f"[Piper] {v}" for v in self.piper_engine.list_local_voices()]
        
        # Añadir Kokoro con prefijo Premium si está instalada
        if self.kokoro_engine.is_installed():
            piper_v.append("[Premium] Kokoro")
            
        return piper_v if piper_v else ["Ninguna descargada"]

    def _start_download(self):
        label = self.download_option.get()
        if label == "Cargando catálogo..." or "Error" in label:
            return
            
        voice_id = self.voice_label_to_id.get(label)
        if not voice_id:
            return
            
        self.status_label.configure(text=f"Descargando {label}... (esto puede tardar)", text_color="blue")
        self.btn_download.configure(state="disabled")
        
        threading.Thread(target=self._download_thread, args=(voice_id,), daemon=True).start()

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
    def _build_available_labels(self, voices_data):
        """Construye la lista de etiquetas incluyendo Kokoro."""
        self.voice_label_to_id = {v["label"]: v["id"] for v in voices_data}
        
        # Añadir Kokoro a la lista de DESCARGAS si no está instalada
        if not self.kokoro_engine.is_installed():
            self.voice_label_to_id["[Premium] Kokoro (340MB)"] = "KOKORO_ID"
            
        self.available_voices_labels = list(self.voice_label_to_id.keys())

    def _load_remote_voices(self):
        """Carga el catálogo en segundo plano."""
        try:
            voices_data = self.piper_engine.get_available_spanish_voices()
            if voices_data and self.winfo_exists():
                self._build_available_labels(voices_data)
                self.after(0, self._safe_update_catalog)
            elif self.winfo_exists():
                self.after(0, lambda: self.download_option.configure(values=["Error al cargar catálogo"]) if self.winfo_exists() else None)
        except Exception as e:
            print(f"Error cargando voces remotas: {e}")
            if self.winfo_exists():
                self.after(0, lambda: self.download_option.configure(values=["Error de conexión"]) if self.winfo_exists() else None)

    def _safe_update_catalog(self):
        """Actualización segura de la UI."""
        if self.winfo_exists():
            self.download_option.configure(values=self.available_voices_labels)
            self.download_option.set(self.available_voices_labels[0])

    def _start_download(self):
        label = self.download_option.get()
        if label == "Cargando catálogo..." or "Error" in label:
            return
            
        if "[Premium] Kokoro" in label:
            self._start_kokoro_download()
            return

        voice_id = self.voice_label_to_id.get(label)
        if voice_id:
            self.btn_download.configure(state="disabled", text="Descargando...")
            self.status_label.configure(text=f"Bajando {label}...", text_color="#3498db")
            threading.Thread(target=self._download_thread, args=(voice_id, label), daemon=True).start()

    def _download_thread(self, voice_id, label):
        success = self.piper_engine.download_voice(voice_id)
        if success and self.winfo_exists():
            self.after(0, lambda: self._on_download_success(label))
        elif self.winfo_exists():
            self.after(0, lambda: self.btn_download.configure(state="normal", text="Error. Reintentar") if self.winfo_exists() else None)

    def _on_download_success(self, label):
        self.btn_download.configure(state="normal", text="Descargar Voz Seleccionada")
        self.status_label.configure(text=f"¡{label} lista!", text_color="green")
        self.local_voices_option.configure(values=self._get_local_voices_list())
        if hasattr(self.parent, "update_voice_options"):
            self.parent.update_voice_options()

    def _start_kokoro_download(self):
        self.btn_download.configure(state="disabled", text="Descargando Kokoro...")
        self.status_label.configure(text="Bajando Motor Premium (340MB)...", text_color="#3498db")
        threading.Thread(target=self._kokoro_download_thread, daemon=True).start()

    def _kokoro_download_thread(self):
        success = self.kokoro_engine.download_model()
        if success and self.winfo_exists():
            self.after(0, self._safe_on_kokoro_success)
        elif self.winfo_exists():
            self.after(0, lambda: self.btn_download.configure(state="normal", text="Error. Reintentar Kokoro") if self.winfo_exists() else None)

    def _safe_on_kokoro_success(self):
        if self.winfo_exists():
            self.btn_download.configure(text="Descargar Voz Seleccionada", state="normal")
            self.status_label.configure(text="¡Kokoro Premium instalado!", text_color="green")
            # Actualizar listas
            self.local_voices_option.configure(values=self._get_local_voices_list())
            # Quitar Kokoro de la lista de descargas
            cached_voices = self.piper_engine.get_cached_voices_if_any()
            if cached_voices:
                self._build_available_labels(cached_voices)
                self.download_option.configure(values=self.available_voices_labels)
                self.download_option.set(self.available_voices_labels[0])
            
            if hasattr(self.parent, "update_voice_options"):
                self.parent.update_voice_options()

    def _get_local_voices_list(self):
        # Listar voces de Piper con prefijo
        piper_v = [f"[Piper] {v}" for v in self.piper_engine.list_local_voices()]
        # Añadir Kokoro con prefijo Premium si está instalada
        if self.kokoro_engine.is_installed():
            piper_v.append("[Premium] Kokoro")
        return piper_v if piper_v else ["Ninguna descargada"]
