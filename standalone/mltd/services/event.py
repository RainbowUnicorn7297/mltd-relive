from jsonrpc import dispatcher


@dispatcher.add_method(name='EventService.GetEventList')
def get_event_list(params):
    """Service for getting currently on-going events.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing event info (see implementation below).
    """
    return {
        'event_list': None,
        'today_event_schedule': {
            'mst_event_id': 0,
            'mst_event_schedule_id': 0,
            'event_schedule_type': 0,
            'is_finished': False,
            'begin_date': None,
            'end_date': None,
            'resource_id': ''
        }
    }

