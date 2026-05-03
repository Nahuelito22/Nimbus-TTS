import os
import requests
import json
from huggingface_hub import hf_hub_download
import threading

class PiperEngine:
    """
    Gestiona la sntesis de voz local usando Piper y la descarga de modelos desde Hugging Face.
    """
    def __init__(self, models_dir=None):
        if models_dir is None:
            self.models_dir = os.path.join(os.getcwd(), "models")
        else:
            self.models_dir = models_dir
            
        os.makedirs(self.models_dir, exist_ok=True)
        # Repositorio oficial de voces de Piper en Hugging Face
        self.repo_id = "rhasspy/piper-voices"
        self._voices_metadata = {}

    def update_models_dir(self, new_dir):
        """Actualiza la ruta de los modelos y asegura que exista."""
        self.models_dir = new_dir
        os.makedirs(self.models_dir, exist_ok=True)

    def get_cached_voices_if_any(self):
        """Busca voces en memoria o disco SIN tocar internet. Ideal para la UI."""
        cache_path = os.path.join(self.models_dir, "voices_cache.json")
        if self._voices_metadata:
            return self._format_voices(self._voices_metadata)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self._voices_metadata = json.load(f)
                    return self._format_voices(self._voices_metadata)
            except:
                pass
        return None

    def get_available_spanish_voices(self):
        """Descarga el catálogo (o usa la caché local) y devuelve info legible."""
        try:
            # Primero intentar lo rápido
            cached = self.get_cached_voices_if_any()
            if cached: return cached
            
            # Si no hay nada, descargar (esto debe ir en un hilo)
            url = "https://huggingface.co/rhasspy/piper-voices/raw/main/voices.json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self._voices_metadata = response.json()
                cache_path = os.path.join(self.models_dir, "voices_cache.json")
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(self._voices_metadata, f)
                    
            return self._format_voices(self._voices_metadata)
        except Exception as e:
            print(f"Error obteniendo catálogo de voces: {e}")
            return []

    def _format_voices(self, metadata):
        """Helper para formatear las voces del json."""
        es_voices = []
        for voice_id, info in metadata.items():
            lang = info.get("language", {})
            if lang.get("family") == "es":
                country = lang.get("region", "ES")
                name = info.get("name", voice_id)
                quality = info.get("quality", "unknown")
                label = f"[Piper] [{country}] {name.capitalize()} ({quality.capitalize()})"
                es_voices.append({"id": voice_id, "label": label})
        return sorted(es_voices, key=lambda x: x["label"])

    def list_local_voices(self):
        """Lista las voces descargadas en la carpeta models."""
        return [f.replace(".onnx", "") for f in os.listdir(self.models_dir) if f.endswith(".onnx")]

    def download_voice(self, voice_name, progress_callback=None):
        """
        Descarga un modelo de voz desde Hugging Face.
        voice_name ej: 'es_ES-alvaro-medium'
        """
        try:
            if not self._voices_metadata:
                self.get_available_spanish_voices()
                
            voice_data = self._voices_metadata.get(voice_name)
            if not voice_data:
                print(f"La voz {voice_name} no existe en el catlogo.")
                return False
                
            # Extraer las rutas correctas desde el json
            files = voice_data.get("files", {})
            onnx_file_path = None
            json_file_path = None
            
            for f in files.keys():
                if f.endswith(".onnx"):
                    onnx_file_path = f
                elif f.endswith(".onnx.json"):
                    json_file_path = f
                    
            if not onnx_file_path or not json_file_path:
                return False
            
            # Descargar ONNX
            hf_hub_download(
                repo_id=self.repo_id,
                filename=onnx_file_path,
                local_dir=self.models_dir,
                local_dir_use_symlinks=False
            )
            
            # Descargar JSON de config
            hf_hub_download(
                repo_id=self.repo_id,
                filename=json_file_path,
                local_dir=self.models_dir,
                local_dir_use_symlinks=False
            )
            
            # Mover los archivos a la raz de 'models' para evitar subcarpetas
            import shutil
            import glob
            
            # La descarga de hf_hub crea la estructura de carpetas de github localmente.
            # Vamos a buscar los archivos donde sea que se hayan descargado y moverlos a self.models_dir
            for f in glob.glob(os.path.join(self.models_dir, '**', f"{voice_name}.onnx*"), recursive=True):
                filename = os.path.basename(f)
                dest = os.path.join(self.models_dir, filename)
                if f != dest:
                    shutil.move(f, dest)
            
            return True
        except Exception as e:
            print(f"Error descargando voz {voice_name}: {e}")
            return False

    def generate_audio(self, text, output_path, voice_name):
        """
        Genera audio usando piper executable o librera.
        Como la librera piper-tts puede ser caprichosa con las dependencias de C++,
        una forma robusta es usar subprocess si el binario est disponible, 
        o la librera si carg bien.
        """
        try:
            import wave
            from piper import PiperVoice
            model_path = os.path.join(self.models_dir, f"{voice_name}.onnx")
            config_path = os.path.join(self.models_dir, f"{voice_name}.onnx.json")
            
            if not os.path.exists(model_path):
                return False
                
            voice = PiperVoice.load(model_path, config_path)
            with wave.open(output_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            return True
        except Exception as e:
            print(f"Error en síntesis local (Piper): {e}")
            return False
