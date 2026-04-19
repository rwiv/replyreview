# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['replyreview/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tests', 'pyarrow', 'fastparquet', 'sqlalchemy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='replyreview',
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
    icon='assets/icon.icns' if sys.platform == 'darwin' else 'assets/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['Qt6*', 'libQt6*', 'PySide6*', 'shiboken6*'],
    name='replyreview',
)
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='ReplyReview.app',
        icon='assets/icon.icns',
        bundle_identifier='com.rwiv.replyreview',
    )
