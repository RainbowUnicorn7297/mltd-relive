from jsonrpc import dispatcher


@dispatcher.add_method(name='FriendService.GetFlowerStandCount')
def get_flower_stand_count(params):
    """Service for getting flower stand counts for a user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: A dict with empty flower stand count info. See
                'flower_stand_count' below for the dict definition.
    Returns:
        A dict containing a single key 'flower_stand_count', whose value
        is a dict that represents flower stand count info and contains
        the following keys.
            send_count: Number of flower stands sent by the user on the
                        previous day.
            recv_count: Number of flower stands received by the user on
                        the previous day.
            all_recv_count: 0.
    """
    # Return static flower stand count info.
    return {
        'send_count': 5,
        'recv_count': 5,
        'all_recv_count': 0
    }

