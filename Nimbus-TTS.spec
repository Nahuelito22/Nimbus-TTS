# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter
import tkinterdnd2

# Rutas de librerías críticas
ctk_path = os.path.dirname(customtkinter.__file__)
tkdnd_path = os.path.dirname(tkinterdnd2.__file__)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (ctk_path, 'customtkinter'),
        (tkdnd_path, 'tkinterdnd2'), # Incluimos TODA la carpeta de dnd2
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'tkinterdnd2',
        'PIL.ImageResampling',
        'pygame',
        'onnxruntime',
        'sounddevice',
        'soundfile',
        'librosa',
        'numpy',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Nimbus-TTS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\favicon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Nimbus-TTS',
)
