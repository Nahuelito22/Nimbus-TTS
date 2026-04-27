import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_manager, hotkey_manager):
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        
        self.title("Configuracin de Nimbus-TTS")
        self.geometry("400x500")
        self.after(100, self.lift)  # Asegurar que est al frente en Windows
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.padx = 20
        self.pady = 10
        
        self.setup_ui()

    def setup_ui(self):
        # --- APARIENCIA ---
        ctk.CTkLabel(self, text="Apariencia", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=self.padx, pady=(20, 5), sticky="w")
        
        self.appearance_mode_option = ctk.CTkOptionMenu(self, values=["System", "Dark", "Light"], command=self.change_appearance_mode)
        self.appearance_mode_option.set(self.config_manager.get("appearance_mode"))
        self.appearance_mode_option.grid(row=1, column=0, padx=self.padx, pady=self.pady, sticky="ew")
        
        # --- ATAJOS DE TECLADO ---
        ctk.CTkLabel(self, text="Atajos de Teclado", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=self.padx, pady=(20, 5), sticky="w")
        
        # Play/Pause
        ctk.CTkLabel(self, text="Reproducir / Pausar:").grid(row=3, column=0, padx=self.padx, pady=(5, 0), sticky="w")
        self.pp_entry = ctk.CTkEntry(self)
        self.pp_entry.insert(0, self.config_manager.get("hotkey_play_pause"))
        self.pp_entry.grid(row=4, column=0, padx=self.padx, pady=self.pady, sticky="ew")
        
        # Stop
        ctk.CTkLabel(self, text="Detener:").grid(row=5, column=0, padx=self.padx, pady=(5, 0), sticky="w")
        self.stop_entry = ctk.CTkEntry(self)
        self.stop_entry.insert(0, self.config_manager.get("hotkey_stop"))
        self.stop_entry.grid(row=6, column=0, padx=self.padx, pady=self.pady, sticky="ew")
        
        # --- BOTN GUARDAR ---
        self.save_button = ctk.CTkButton(self, text="Guardar y Aplicar", command=self.save_and_close)
        self.save_button.grid(row=7, column=0, padx=self.padx, pady=30, sticky="ew")

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        self.config_manager.set("appearance_mode", new_appearance_mode)

    def save_and_close(self):
        pp_key = self.pp_entry.get().strip().lower()
        stop_key = self.stop_entry.get().strip().lower()
        
        if pp_key and stop_key:
            self.config_manager.set("hotkey_play_pause", pp_key)
            self.config_manager.set("hotkey_stop", stop_key)
            
            # Actualizar hotkeys en tiempo real
            self.hotkey_manager.update_hotkeys(pp_key, stop_key)
            
            self.destroy()
