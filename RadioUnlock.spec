# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for RadioUnlock Windows Standalone.
Run:  pyinstaller --clean RadioUnlock.spec
"""

import sys
import os

# src path — works whether repo is checked out flat or in a subfolder
REPO_ROOT = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(SPEC))
SRC = os.path.join(REPO_ROOT, 'src')
sys.path.insert(0, REPO_ROOT)

block_cipher = None

datas = [
    (os.path.join(REPO_ROOT, 'src', 'radiocodes'), 'radiocodes'),
]
binaries = []
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'radiocodes.algorithms',
    'radiocodes.lookup_engine',
    'radiocodes.eeprom_analyzer',
    'radiocodes.serial_detector',
    'radiocodes.bluepill.analyzer',
    'radiocodes.algorithms.ford_m',
    'radiocodes.algorithms.ford_v',
    'radiocodes.algorithms.renault',
    'radiocodes.algorithms.vw_rcd',
    'radiocodes.algorithms.vauxhall',
    'radiocodes.algorithms.fiat',
    'radiocodes.algorithms.nissan',
    'radiocodes.algorithms.honda',
    'radiocodes.algorithms.kia',
    'radiocodes.algorithms.peugeot',
    'radiocodes.algorithms.alfa',
    'radiocodes.algorithms.chrysler',
    'radiocodes.algorithms.jaguar',
    'radiocodes.algorithms.toyota',
]

a = Analysis(
    ['windows_launcher.py'],
    pathex=[os.path.dirname(SPEC)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='RadioUnlock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RadioUnlock',
)
