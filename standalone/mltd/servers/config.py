import logging
from configparser import ConfigParser
from datetime import timedelta, timezone

version = '0.1.0'
# 'zh' for Traditional Chinese, 'ko' for Korean
_language = 'zh'
_log_level = logging.INFO
_is_local = False


def version_tuple(v):
    return tuple(map(int, v.split('.')))


class CustomConfigParser(ConfigParser):

    def __init__(self):
        super().__init__()
        self.read_dict({
            'default': {
                'version': version,
                'language': _language,
                'log_level': _log_level,
                'is_local': _is_local
            }
        })
        if not self.read('config.ini'):
            self.write_config()
        if version_tuple(self['default']['version']) < version_tuple(version):
            self.set_config('version', version)

    def write_config(self):
        with open('config.ini', 'w') as config_file:
            self.write(config_file)

    def set_config(self, key, value):
        self['default'][key] = str(value)
        self.write_config()


config = CustomConfigParser()

server_language = config['default']['language']
server_timezone = timezone(timedelta(
    hours=8 if server_language == 'zh' else 9))
log_level = config.getint('default', 'log_level')
is_local = config.getboolean('default', 'is_local')
api_port = 7650 if is_local else 8443

