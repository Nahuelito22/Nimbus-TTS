import asyncio
import edge_tts
import os

class TTSEngine:
    """
    Motor de sntesis de voz utilizando edge-tts.
    """
    def __init__(self, voice="es-ES-AlvaroNeural", rate="+0%"):
        self.voice = voice
        self.rate = rate

    async def generate_audio(self, text, output_path):
        """
        Genera un archivo de audio a partir de texto.
        """
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"Error al generar audio: {e}")
            return False

    def list_voices(self):
        """
        Retorna una lista de voces disponibles (puedes ampliar esto).
        """
        # Algunas voces recomendadas en espaol
        return [
            "es-ES-AlvaroNeural",
            "es-ES-ElviraNeural",
            "es-MX-DaliaNeural",
            "es-MX-JorgeNeural",
            "es-AR-ElenaNeural",
            "es-AR-TomasNeural"
        ]

# Helper para ejecutar asncronamente desde cdigo sncrono si fuera necesario
def run_tts(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%"):
    engine = TTSEngine(voice, rate)
    asyncio.run(engine.generate_audio(text, output_path))

if __name__ == "__main__":
    # Test
    # run_tts("Hola, esto es una prueba de Nimbus TTS", "test.mp3")
    pass
