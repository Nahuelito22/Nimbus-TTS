# Plan de Desarrollo: Nimbus-TTS 🎧📚

Este documento sirve para el seguimiento del desarrollo de Nimbus-TTS.

## Épica 1: Configuración Inicial y Base de Datos (Setup)
- [x] Tarea 1.1: Inicializar un entorno virtual de Python (`venv`).
- [x] Tarea 1.2: Instalar las dependencias core: `customtkinter`, `edge-tts`, `pygame`, `keyboard`, `PyMuPDF`.
- [x] Tarea 1.3: Crear el archivo `requirements.txt`.
- [x] Tarea 1.4: Crear la estructura de carpetas.

## Épica 2: Motor Lógico (Core) - Procesamiento y Audio
- [ ] Tarea 2.1 - Parser PDF: Desarrollar `pdf_parser.py` (PyMuPDF).
- [ ] Tarea 2.2 - Gestor de Texto: Desarrollar `text_manager.py`.
- [ ] Tarea 2.3 - Motor TTS: Desarrollar `tts_engine.py` (edge-tts).
- [ ] Tarea 2.4 - Reproductor: Desarrollar `audio_player.py` (pygame).

## Épica 3: Interfaz Gráfica (UI)
- [ ] Tarea 3.1 - Ventana Base: Crear `app_window.py` (CustomTkinter).
- [ ] Tarea 3.2 - Diseño Layout Principal: TextBox central.
- [ ] Tarea 3.3 - Panel de Carga: Botón cargar PDF.
- [ ] Tarea 3.4 - Controles de Reproducción: Botones Play, Pausa y Detener.
- [ ] Tarea 3.5 - Configuración TTS: Menú desplegable para voz y slider de velocidad.

## Épica 4: Atajos Globales (Background Hotkeys)
- [ ] Tarea 4.1 - Hotkeys Engine: Implementar `hotkeys.py` (keyboard).
- [ ] Tarea 4.2 - Enlace de Lógica: Conectar el atajo capturado con la reproducción.

## Épica 5: Empaquetado y Distribución
- [ ] Tarea 5.1 - PyInstaller: Configurar y ejecutar PyInstaller (`nimbus.spec`).
- [ ] Tarea 5.2 - GitHub Actions: Crear workflow de CI/CD para release automático.
