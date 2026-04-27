import keyboard
import threading

class HotkeyManager:
    """
    Gestiona los atajos de teclado globales para controlar la aplicacin en segundo plano.
    """
    def __init__(self, play_pause_callback=None, stop_callback=None):
        self.play_pause_callback = play_pause_callback
        self.stop_callback = stop_callback

    def start(self):
        """
        Registra los atajos e inicia el escucha.
        """
        self.update_hotkeys('ctrl+alt+p', 'ctrl+alt+s')

    def update_hotkeys(self, play_pause_key, stop_key):
        """
        Actualiza los hotkeys registrados.
        """
        try:
            keyboard.unhook_all()
            if self.play_pause_callback:
                keyboard.add_hotkey(play_pause_key, self.play_pause_callback)
            if self.stop_callback:
                keyboard.add_hotkey(stop_key, self.stop_callback)
        except Exception as e:
            print(f"Error al actualizar hotkeys: {e}")

    def stop_listening(self):
        """
        Elimina todos los hotkeys registrados.
        """
        keyboard.unhook_all()

if __name__ == "__main__":
    # Test bsico
    def test_pp(): print("Play/Pause pulsado")
    def test_s(): print("Stop pulsado")
    
    hm = HotkeyManager(test_pp, test_s)
    hm.start()
    print("Escuchando hotkeys (Ctrl+Alt+P y Ctrl+Alt+S)... Presiona Esc para salir.")
    keyboard.wait('esc')
