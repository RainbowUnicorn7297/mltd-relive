from msgpack import unpackb

_manifest_name = {'zh': '85822153578df611a4f852d4e02660f6f34401e4.data',
                  'ko': '25c292462510f60200eecd8080f4680114b8c576.data'}
_lookup = {'zh': {}, 'ko': {}}


def load_manifest(lang, platform):
    global _manifest_name, _lookup
    path = '../assets-' + lang + '-' + platform + '/' + _manifest_name[lang]
    with open(path, 'rb') as f:
        manifest = unpackb(f.read())
        _lookup[lang][platform] = {v[1]: k for k, v in manifest[0].items()}


def asset(lang, platform, hashed_name):
    global _manifest_name, _lookup
    if platform not in _lookup[lang].keys():
        load_manifest(lang, platform)
    path = '../assets-' + lang + '-' + platform + '/'
    if hashed_name == _manifest_name[lang]:
        path += hashed_name
    else:
        path += '120000/' + _lookup[lang][platform][hashed_name]
    ret = b''
    with open(path, 'rb') as f:
        ret = f.read()
    return ret

