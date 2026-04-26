import pygame
import os

class AudioPlayer:
    """
    Controlador de reproduccin de audio basado en pygame.
    """
    def __init__(self):
        pygame.mixer.init()
        self.current_file = None

    def load(self, file_path):
        """
        Carga un archivo de audio para su reproduccin.
        """
        if not os.path.exists(file_path):
            print(f"Error: Archivo no encontrado {file_path}")
            return False
        
        try:
            pygame.mixer.music.load(file_path)
            self.current_file = file_path
            return True
        except Exception as e:
            print(f"Error al cargar audio: {e}")
            return False

    def play(self):
        """Inicia la reproduccin."""
        pygame.mixer.music.play()

    def pause(self):
        """Pausa la reproduccin."""
        pygame.mixer.music.pause()

    def unpause(self):
        """Reanuda la reproduccin."""
        pygame.mixer.music.unpause()

    def stop(self):
        """Detiene la reproduccin."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Libera el archivo para que pueda ser sobrescrito

    def is_playing(self):
        """Retorna True si hay audio reproducindose."""
        return pygame.mixer.music.get_busy()

    def set_volume(self, volume):
        """Ajusta el volumen (0.0 a 1.0)."""
        pygame.mixer.music.set_volume(volume)

    def __del__(self):
        pygame.mixer.quit()

if __name__ == "__main__":
    # Test
    # player = AudioPlayer()
    # if player.load("test.mp3"):
    #     player.play()
    pass
