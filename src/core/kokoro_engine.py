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
        self.model_name = "model.onnx"
        self.voices_name = "voices.bin"
        self.repo_id = "NeuML/kokoro-base-onnx"
        self._voice = None

    def is_installed(self):
        """Verifica si los archivos necesarios existen."""
        return (os.path.exists(os.path.join(self.models_dir, self.model_name)) and 
                os.path.exists(os.path.join(self.models_dir, self.voices_name)))

    def download_model(self, progress_callback=None):
        """Descarga el modelo y las voces binarias oficiales."""
        try:
            # 1. Descargar Modelo ONNX desde Hugging Face
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.model_name,
                local_dir=self.models_dir
            )
            
            # 2. Descargar Voces Binarias (.bin) desde el origen oficial
            # Este archivo es el que requiere la librería moderna
            voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
            response = requests.get(voices_url, stream=True)
            if response.status_code == 200:
                with open(os.path.join(self.models_dir, self.voices_name), 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
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
                import numpy as np
                # Parche: Guardar el valor original de np.load
                original_load = np.load
                # Crear una versión de np.load que siempre permita pickle
                def patched_load(*args, **kwargs):
                    kwargs['allow_pickle'] = True
                    return original_load(*args, **kwargs)
                
                # Aplicar el parche temporalmente
                np.load = patched_load
                try:
                    from kokoro_onnx import Kokoro
                    self._voice = Kokoro(model_path, voices_path)
                finally:
                    # Restaurar np.load original pase lo que pase
                    np.load = original_load
            
            samples, sample_rate = self._voice.create(text, voice=voice, speed=1.0, lang="en-us")
            sf.write(output_path, samples, sample_rate)
            return True
        except Exception as e:
            print(f"Error en síntesis con Kokoro: {e}")
            return False
