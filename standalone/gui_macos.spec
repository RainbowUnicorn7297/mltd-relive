# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['gui.pyw'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a.datas += Tree('../key', prefix='key', excludes=['*.cmd'])
a.datas += Tree('mltd/locales', prefix='locales', excludes=['*.cmd'])
a.datas += Tree('mltd/models/mst_data', prefix='mst_data')
a.datas += Tree('mltd/models/mst_data/zh', prefix='zh')
a.datas += Tree('mltd/models/mst_data/ko', prefix='ko')
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mltd-relive-standalone',
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
    icon=['../app_icon.icns'],
)
app = BUNDLE(
    exe,
    name='mltd-relive-standalone.app',
    icon='../app_icon.icns',
    bundle_identifier=None,
)
