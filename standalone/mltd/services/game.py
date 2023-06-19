from datetime import datetime

from jsonrpc import dispatcher

from mltd.servers.config import server_language, server_timezone
from mltd.servers.utilities import format_datetime


@dispatcher.add_method(name='GameService.GetVersion')
def get_version(params):
    """Service for static game version info.
    
    Invoked at title screen, either at app boot or server daily reset.
    Args:
        params: An empty dict.
    Returns:
        A dict containing supported client version and other info (see
        below).
    """
    return {
        'support_client_version': '2.1.000',
        'game_url': f'https://theaterdays-{server_language}.appspot.com/',
        'webview_url': (f'https://webview-dot-theaterdays-{server_language}'
                        + '.appspot.com/'),
        'store_url': ('https://play.google.com/store/apps/details?id='
                      + 'com.bandainamcoent.imas_millionlive_theaterdays_'
                      + 'ch' if server_language == 'zh' else 'kr'),
        'policy_last_update_date': format_datetime(
            datetime(2017, 9, 6, 18, 0, 0, tzinfo=server_timezone)),
        'terms_url': 'https://legal.bandainamcoent.co.jp/terms/',
        'policy_url': 'https://legal.bandainamcoent.co.jp/privacy/',
        'title_image_url': '',
        'title_cue_name': '',
        'title_call_cue_name': 'title_call_001har',
        'hide_title_logo': False,
        'enable_button': False,
        'enable_special_event_button': False,
        'title_button': {
            'image_url': '',
            'url': '',
            'text': '',
            'pos_x': 0,
            'pos_y': 0,
            'position': {
                'x': 0,
                'y': 0
            },
            'anchor': {
                'x': 0,
                'y': 0
            }
        },
        'title_button_list': None,
        'enable_special_title_logo': False,
        'special_event_button': {
            'image_url': '',
            'url': '',
            'text': '',
            'pos_x': 0,
            'pos_y': 0,
            'position': {
                'x': 0,
                'y': 0
            },
            'anchor': {
                'x': 0,
                'y': 0
            }
        },
        'dialog': {
            'title': '',
            'message': '',
            'connection_title_jump': False,
            'connection_retry_count': 0,
            'connection_ignore_override_error': False
        }
    }

