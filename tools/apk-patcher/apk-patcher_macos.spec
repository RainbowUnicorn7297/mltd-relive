# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


datas = [
    ('OverrideActivity_device_max_refresh_rate.smali', '.'),
    ('mltd.jks', '.')
]


a = Analysis(
    ['apk-patcher.pyw'],
    pathex=[],
    binaries=[],
    datas=datas,
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
a.datas += Tree('../fonts', prefix='fonts')
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mltd-relive-apk-patcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='mltd-relive-apk-patcher.app',
    bundle_identifier=None,
)