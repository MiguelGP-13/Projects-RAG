# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['build.py'],
    pathex=[],
    binaries=[],
    datas=[('main.py', '.'), ('RAG.py', '.'), ('../secrets.env', '.'), ('../settings.env', '.'), ('../Frontend', 'frontend'), ('redis-server.exe', '.'), ('redis.conf.template', '.'), ('chats', 'chats'), ('documents', 'documents')],
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
    [],
    exclude_binaries=True,
    name='build',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='build',
)
