"""Internationalization module for localized translations.

Uses Python's gettext module.
To create the human-readable message catalog template file
'mltd/locales/mltd.pot', use the pygettext.py tool:

cd <Path to repository>/standalone
python -X utf8 <Path to Python installation>/Tools/i18n/pygettext.py -d mltd -p <Path to repository>/standalone/mltd/locales .

Copy the content of the resulting mltd.pot file to
'mltd/locales/<Language>/LC_MESSAGES/mltd.po' and add translations for
Traditional Chinese and Korean.
To create the machine-readable binary catalog files
'mltd/locales/<Language>/LC_MESSAGES/mltd.mo', use the msgfmt.py tool:

python <Path to Python installation>/Tools/i18n/msgfmt.py <Path to repository>/standalone/mltd/locales/zh/LC_MESSAGES/mltd.po
python <Path to Python installation>/Tools/i18n/msgfmt.py <Path to repository>/standalone/mltd/locales/ko/LC_MESSAGES/mltd.po
"""
import gettext
import sys
from os import path

from mltd.servers.config import server_language


def _locales_path():
    base_path = getattr(sys, '_MEIPASS', path.abspath('./mltd'))
    return path.join(base_path, 'locales')


translation = gettext.translation('mltd', _locales_path(), [server_language])
