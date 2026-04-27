# Nimbus-TTS

Una aplicación de escritorio moderna y ligera desarrollada en Python para transformar textos de estudio en audio utilizando voces neuronales de alta fidelidad. 

Este proyecto nace de la necesidad de mejorar la experiencia de estudio: evita las voces robóticas tradicionales de los sistemas operativos y soluciona el problema de la pérdida de foco al permitir pausar y reanudar la lectura desde cualquier pantalla mediante atajos de teclado globales.

## Características Principales (Fase de Desarrollo)

- **Voces Neuronales:** Integración con `edge-tts` para una lectura natural, fluida y agradable al oído.
- **Interfaz Moderna:** UI limpia y responsiva construida con `CustomTkinter`.
- **Control Global:** Atajos de teclado que funcionan en segundo plano (ideal para pausar la lectura mientras tomas apuntes en otra ventana).
- **Lectura por Bloques:** Diseñado para manejar textos largos como módulos universitarios o documentación técnica.

## Stack Tecnológico

- **Lenguaje:** Python 3.x
- **Frontend / UI:** CustomTkinter
- **Motor de Audio:** Edge-TTS + Pygame / Pydub
- **Control de Periféricos:** Keyboard (para global hotkeys)

## Próximos Pasos (Roadmap)

- [x] Fase 1: Implementación del motor de audio (TTS) y reproducción sin bloqueos.
- [x] Fase 2: Construcción de la interfaz gráfica (UI).
- [x] Fase 3: Integración de atajos de teclado globales.
- [ ] Fase 4: (Opcional) Integración de IA local para generar resúmenes automáticos del texto leído.

## Autor

Desarrollado por Nahuel Ghilardi