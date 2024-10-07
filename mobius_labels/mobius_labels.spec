# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mobius_labels.py'],
    pathex=[],
    binaries=[('Release-24.07.0-0', 'Release-24.07.0-0')],
    datas=[('images', 'images'), ('texts', 'texts')],
    hiddenimports=[],
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
    name='mobius_labels',
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
    icon='images\mobius-label-icon.ico',
)
