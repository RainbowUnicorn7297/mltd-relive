import logging
from configparser import ConfigParser
from datetime import timedelta, timezone

version = '0.1.0'
api_port = 7650
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
            self['default']['version'] = version
            self.write_config()

    @property
    def language(self):
        return self['default']['language']

    @language.setter
    def language(self, value):
        self['default']['language'] = value
        self.write_config()

    @property
    def timezone(self):
        return timezone(timedelta(hours=8 if self.language == 'zh' else 9))

    @property
    def log_level(self):
        return self.getint('default', 'log_level')

    @property
    def is_local(self):
        return self.getboolean('default', 'is_local')

    @is_local.setter
    def is_local(self, value):
        self['default']['is_local'] = str(value)
        self.write_config()

    def write_config(self):
        with open('config.ini', 'w') as config_file:
            self.write(config_file)


config = CustomConfigParser()

