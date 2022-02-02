from msgpack import unpackb

manifest_name = {'zh': '85822153578df611a4f852d4e02660f6f34401e4.data',
                 'ko': '25c292462510f60200eecd8080f4680114b8c576.data'}
lookup = {'zh': {}, 'ko': {}}

def load_manifest(lang, platform):
    global manifest_name, lookup
    path = '../assets-' + lang + '-' + platform + '/' + manifest_name[lang]
    with open(path, 'rb') as f:
        manifest = unpackb(f.read())
        lookup[lang][platform] = {v[1]: k for k, v in manifest[0].items()}

def asset(lang, platform, hashed_name):
    global manifest_name, lookup
    print(lang+' '+platform+' '+hashed_name)
    if platform not in lookup[lang].keys():
        load_manifest(lang, platform)
    path = '../assets-' + lang + '-' + platform + '/'
    if hashed_name == manifest_name[lang]:
        path += hashed_name
    else:
        path += '120000/' + lookup[lang][platform][hashed_name]
    ret = b''
    with open(path, 'rb') as f:
        ret = f.read()
    return ret
