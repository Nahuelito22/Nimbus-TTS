import os
import sys

# Parche para PyInstaller y TkinterDnD2: Asegurar que las DLLs base sean encontradas por Tcl
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ.get('PATH', '')

from src.ui.app_window import NimbusApp

def main():
    print("Iniciando Nimbus-TTS...")
    app = NimbusApp()
    app.mainloop()

if __name__ == "__main__":
    main()
