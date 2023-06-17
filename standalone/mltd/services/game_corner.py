from jsonrpc import dispatcher


@dispatcher.add_method(name='GameCornerService.GetGameCornerList')
def get_event_list(params):
    """Service for getting game corners (meaning is unknown).

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key 'game_corner_list' with null
        value.
    """
    return {
        'game_corner_list': None
    }

