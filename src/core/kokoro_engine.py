import os
import requests
import threading
from huggingface_hub import hf_hub_download

class KokoroEngine:
    """
    Motor para la voz Premium Kokoro-82M (ONNX).
    """
    def __init__(self, models_dir=None):
        if models_dir is None:
            self.models_dir = os.path.join(os.getcwd(), "models", "kokoro")
        else:
            self.models_dir = os.path.join(models_dir, "kokoro")
            
        os.makedirs(self.models_dir, exist_ok=True)
        self.model_name = "kokoro-v0_19.onnx"
        self.voices_name = "voices.json"
        self.repo_id = "hexgrad/Kokoro-82M"
        self._voice = None

    def is_installed(self):
        """Verifica si los archivos necesarios existen."""
        return (os.path.exists(os.path.join(self.models_dir, self.model_name)) and 
                os.path.exists(os.path.join(self.models_dir, self.voices_name)))

    def download_model(self, progress_callback=None):
        """Descarga el modelo Kokoro desde Hugging Face."""
        try:
            # Descargar ONNX
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.model_name,
                local_dir=self.models_dir,
                local_dir_use_symlinks=False
            )
            # Descargar Voices
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.voices_name,
                local_dir=self.models_dir,
                local_dir_use_symlinks=False
            )
            return True
        except Exception as e:
            print(f"Error descargando Kokoro: {e}")
            return False

    def generate_audio(self, text, output_path, voice="af_heart"):
        """
        Genera audio de alta calidad usando Kokoro.
        voice: ej 'af_heart' (femenina), 'am_adam' (masculina)
        """
        try:
            from kokoro_onnx import Kokoro
            import soundfile as sf
            
            model_path = os.path.join(self.models_dir, self.model_name)
            voices_path = os.path.join(self.models_dir, self.voices_name)
            
            if not self._voice:
                self._voice = Kokoro(model_path, voices_path)
            
            samples, sample_rate = self._voice.create(text, voice=voice, speed=1.0, lang="en-us")
            sf.write(output_path, samples, sample_rate)
            return True
        except Exception as e:
            print(f"Error en síntesis con Kokoro: {e}")
            return False
