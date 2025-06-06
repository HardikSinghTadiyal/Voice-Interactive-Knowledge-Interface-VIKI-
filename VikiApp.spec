# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['viki_ui.py'],
    pathex=[],
    binaries=[],
    datas += [('jarvis', 'jarvis'), ('click.wav', '.')],
    hiddenimports=['PIL.Image', 'PIL.ImageTk', 'tkinter', 'tkinter.scrolledtext', 'tkinter.messagebox', 'tkinter.filedialog', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VikiApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\app_icon.ico'],
)
