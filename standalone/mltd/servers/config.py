import configparser
import logging
from datetime import timedelta, timezone

version = '0.1.0'
# 'zh' for Traditional Chinese, 'ko' for Korean
_language = 'zh'
_log_level = str(logging.INFO)


def version_tuple(v):
    return tuple(map(int, v.split('.')))


class Config:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.read_config()

    def read_config(self):
        self.config.read('config.ini')
        if 'default' not in self.config:
            self.config['default'] = {}
            default = self.config['default']
            default['version'] = version
            default['language'] = _language
            default['log_level'] = _log_level
            self.write_config()
        elif (version_tuple(self.get_config('version'))
              < version_tuple(version)):
            self.set_config('version', version)

    def write_config(self):
        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)

    def get_config(self, key):
        return self.config['default'][key]

    def set_config(self, key, value):
        self.config['default'][key] = value
        self.write_config()


config = Config()

server_language = config.get_config('language')
server_timezone = timezone(timedelta(
    hours=8 if server_language == 'zh' else 9))
log_level = int(config.get_config('log_level'))

