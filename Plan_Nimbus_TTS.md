# Plan de Desarrollo: Nimbus-TTS 🎧📚

Este documento sirve para el seguimiento del desarrollo de Nimbus-TTS.

## Épica 1: Configuración Inicial y Base de Datos (Setup)
- [x] Tarea 1.1: Inicializar un entorno virtual de Python (`venv`).
- [x] Tarea 1.2: Instalar las dependencias core: `customtkinter`, `edge-tts`, `pygame`, `keyboard`, `PyMuPDF`.
- [x] Tarea 1.3: Crear el archivo `requirements.txt`.
- [x] Tarea 1.4: Crear la estructura de carpetas.

## Épica 2: Motor Lógico (Core) - Procesamiento y Audio
- [x] Tarea 2.1 - Parser PDF: Desarrollar `pdf_parser.py` (PyMuPDF).
- [x] Tarea 2.2 - Gestor de Texto: Desarrollar `text_manager.py`.
- [x] Tarea 2.3 - Motor TTS: Desarrollar `tts_engine.py` (edge-tts).
- [x] Tarea 2.4 - Reproductor: Desarrollar `audio_player.py` (pygame).

## Épica 3: Interfaz Gráfica (UI)
- [x] Tarea 3.1 - Ventana Base: Crear `app_window.py` (CustomTkinter).
- [x] Tarea 3.2 - Diseño Layout Principal: TextBox central.
- [x] Tarea 3.3 - Panel de Carga: Botón cargar PDF.
- [x] Tarea 3.4 - Controles de Reproducción: Botones Play, Pausa y Detener.
- [x] Tarea 3.5 - Configuración TTS: Menú desplegable para voz y slider de velocidad.

## Épica 4: Atajos Globales (Background Hotkeys)
- [x] Tarea 4.1 - Hotkeys Engine: Implementar `hotkeys.py` (keyboard).
- [x] Tarea 4.2 - Enlace de Lógica: Conectar el atajo capturado con la reproducción.

## Épica 5: Empaquetado y Distribución
- [ ] Tarea 5.1 - PyInstaller: Configurar y ejecutar PyInstaller (`nimbus.spec`).
- [ ] Tarea 5.2 - GitHub Actions: Crear workflow de CI/CD para release automático.

## Épica 6: Funcionalidades Premium y UX
- [x] Tarea 6.1 - Focus Mode: Resaltado visual del texto mientras se lee.
- [x] Tarea 6.2 - Drag & Drop: Soporte para arrastrar archivos PDF a la app.
- [x] Tarea 6.3 - Resúmenes con IA: Integración de IA para resumir textos largos.
- [x] Tarea 6.4 - System Tray: Minimizar la app a la bandeja del sistema.
- [ ] Tarea 6.5 - Historial: Lista de archivos PDF abiertos recientemente.
- [ ] Tarea 6.6 - Gestor de Voces (Hugging Face): Descarga y uso de modelos locales Piper.
