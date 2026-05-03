import json
import os

class ConfigManager:
    """
    Gestiona la carga y guardado de la configuracin de la aplicacin.
    """
    def __init__(self, filename="config.json"):
        # Usar AppData para persistencia profesional
        app_data_root = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "Nimbus-TTS")
        os.makedirs(app_data_root, exist_ok=True)
        
        self.config_path = os.path.join(app_data_root, filename)
        models_path = os.path.join(app_data_root, "models")
        os.makedirs(models_path, exist_ok=True)

        self.default_config = {
            "voice": "es-ES-AlvaroNeural",
            "rate": "0%",
            "hotkey_play_pause": "ctrl+alt+p",
            "hotkey_stop": "ctrl+alt+s",
            "appearance_mode": "Dark",
            "use_offline_mode": False,
            "local_voice": "",
            "models_path": models_path,
            "gemini_api_key": "",
            "openai_api_key": "",
            "preferred_ai_provider": "Gemini",
            "recent_files": []
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return {**self.default_config, **json.load(f)}
            except Exception:
                return self.default_config
        return self.default_config

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error al guardar configuracin: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
