from jsonrpc import dispatcher


@dispatcher.add_method(name='InspectService.CheckNGWord')
def check_ng_word(params):
    """Check whether there are any NG words in a string.

    Invoked when the user has entered a string.
    Args:
        params: A dict containing a single key named 'text', whose value
                is the string entered by the user.
    Returns:
        A dict containing a single key named 'has_ng_word', whose value
        is a bool indicating whether there are any NG words.
    """
    # Always return false for local server.
    return {'has_ng_word': False}

