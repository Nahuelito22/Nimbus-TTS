import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

def show_splash():
    """Muestra una pantalla de bienvenida mientras carga la app."""
    try:
        splash = tk.Tk()
        splash.title("Iniciando Nimbus-TTS...")
        
        # Quitar bordes de la ventana
        splash.overrideredirect(True)
        splash.attributes("-topmost", True) # Asegurar que esté al frente
        
        # Cargar Logo Original
        def get_path(rel):
            base = getattr(sys, '_MEIPASS', os.path.abspath("."))
            return os.path.join(base, rel)
            
        logo_path = get_path("assets/Logo_Original.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            # Reescalar si es muy grande para el splash
            img.thumbnail((600, 400))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(splash, image=photo, bg='#1a1a1a')
            label.image = photo # Mantener referencia
            label.pack()
            splash.config(bg='#1a1a1a')
        else:
            label = tk.Label(splash, text="Nimbus-TTS\nIniciando...", font=("Arial", 28, "bold"), fg="#2a5a8a", bg="#1a1a1a")
            label.pack(padx=60, pady=60)

        # Centrar Splash
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f'{width}x{height}+{x}+{y}')
        
        return splash
    except:
        return None

def main():
    splash = show_splash()
    if splash:
        splash.update()
    
    print("Iniciando Nimbus-TTS...")
    # Importación tardía para que el splash aparezca rápido
    from src.ui.app_window import NimbusApp
    
    app = NimbusApp()
    
    # Cerrar splash y mostrar app
    if splash:
        splash.destroy()
    
    print("Nimbus-TTS iniciado correctamente.")
    app.mainloop()

if __name__ == "__main__":
    main()
