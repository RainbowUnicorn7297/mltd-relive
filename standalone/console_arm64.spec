# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['console.py'],
    pathex=['../env/python3.11/site-packages'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'mltd.services.asset',
        'mltd.services.auth',
        'mltd.services.banner',
        'mltd.services.birthday',
        'mltd.services.campaign',
        'mltd.services.card',
        'mltd.services.event',
        'mltd.services.friend',
        'mltd.services.game',
        'mltd.services.game_corner',
        'mltd.services.game_setting',
        'mltd.services.gasha',
        'mltd.services.gasha_medal',
        'mltd.services.greco',
        'mltd.services.guest_character',
        'mltd.services.idol',
        'mltd.services.inspect',
        'mltd.services.item',
        'mltd.services.jewel',
        'mltd.services.job',
        'mltd.services.last_update_date',
        'mltd.services.live',
        'mltd.services.login_bonus',
        'mltd.services.mission',
        'mltd.services.offer',
        'mltd.services.present',
        'mltd.services.song',
        'mltd.services.song_ranking',
        'mltd.services.story',
        'mltd.services.theater',
        'mltd.services.unit',
        'mltd.services.user'
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
