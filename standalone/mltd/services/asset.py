from jsonrpc import dispatcher

from mltd.servers.config import config


@dispatcher.add_method(name='AssetService.GetAssetVersion')
def get_asset_version(params):
    """Service for getting current asset version.

    Invoked after logging in.
    Args:
        params: A dict containing the following keys.
            os_name: Which OS the game is designed to run on
                     (Android/iOS).
            unity_version: Unity version of the game (2018v1).
            environment: 'production'
            token: A 40-character hex value representing the game
                   version. This value is the same as header value
                   'X-Version-Hash' for all requests sent from the same
                   game client version.
    Returns:
        A dict containing the following keys.
        asset_url: The URL from which assets are downloaded.
        asset_index_name: The name of the index/manifest file containing
                          file names and other info of all other assets.
        asset_version: Asset version (last version before EoS is
                       120000).
    """
    os_name = 'android' if params['os_name'] == 'Android' else 'ios'
    return {
        'asset_url': ('https://assets.rainbowunicorn7297.com/'
                      + f'{config.language}-{os_name}/'),
        'asset_index_name': (
            '85822153578df611a4f852d4e02660f6f34401e4.data'
            if config.language == 'zh'
            else '25c292462510f60200eecd8080f4680114b8c576.data'
        ),
        'asset_version': 120000
    }

