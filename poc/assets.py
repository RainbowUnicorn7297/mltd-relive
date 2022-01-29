# temp hack for Windows Shortcut
import sys
import win32com.client
##
from msgpack import unpackb

lookup = {'zh': {}, 'ko': {}}

def load_manifest(lang, platform):
    global lookup
    manifest_name = {'zh': '85822153578df611a4f852d4e02660f6f34401e4.data',
                     'ko': '25c292462510f60200eecd8080f4680114b8c576.data'}
    path = 'assets-' + lang + '-' + platform + '/' + manifest_name[lang]
    # temp hack for Windows Shortcut
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut('assets-' + lang + '-' + platform + '.lnk')
    path = shortcut.Targetpath + '/' + manifest_name[lang]
    ##
    with open(path, 'rb') as f:
        manifest = unpackb(f.read())
        lookup[lang][platform] = {v[1]: k for k, v in manifest[0].items()}

def asset(lang, hashed_name):
    global lookup
    if not lookup[lang][platform]:
        load_manifest(lang, platform)
    path = 'assets-' + lang + '-' + platform + '/120000/' + \
           lookup[lang][platform][hashed_name]
    # temp hack for Windows Shortcut
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut('assets-' + lang + '-' + platform + '.lnk')
    path = shortcut.Targetpath + '/120000' + lookup[lang][platform][hashed_name]
    ##
    ret = b''
    with open(path, 'rb') as f:
        ret = f.read()
    return ret
