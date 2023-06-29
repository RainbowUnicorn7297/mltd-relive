from jsonrpc import dispatcher


@dispatcher.add_method(name='GuestCharacterService.GetGuestCharacterList')
def get_guest_character_list(params):
    """Service for getting a list of guest characters.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key 'guest_character_list' with null
        value.
    """
    return {'guest_character_list': None}

