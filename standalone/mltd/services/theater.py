from jsonrpc import dispatcher


@dispatcher.add_method(name='TheaterService.GetTheater')
def get_theater(params):
    """Service for getting theater info.

    Invoked after logging in.
    Args:
        params: A empty dict.
    Returns:
        A dict containing the following keys.
        theater_opening:
    """
    # TODO: Returning empty theater info for now. Replace this with
    # actual implementation.
    return {
        'theater_opening': {
            'mst_theater_opening_id': 0,
            'opening_type': 0,
            'resource_id': '',
            'jump_type': '',
            'cue_sheet': '',
            'cue_name': '',
            'mv_status': {
                'mst_song_id': 0,
                'mv_unit_idol_list': None
            }
        },
        'theater_opening_list': None,
        'theater': {
            'room_list': [],
            'idol_booking_list': [],
            'theater_display_room': {
                'mst_room_id': 0,
                'balloon': {
                    'theater_contact_category_type': 0,
                    'room_idol_list': None,
                    'resource_id': '',
                    'mst_theater_contact_schedule_id': 0,
                    'mst_theater_contact_id': 0,
                    'mst_theater_main_story_id': 0,
                    'mst_theater_guest_main_story_id': 0,
                    'guest_main_story_has_intro': False,
                    'mst_guest_main_story_id': 0,
                    'mst_theater_blog_id': 0,
                    'mst_theater_costume_blog_id': 0,
                    'mst_costume_id': 0,
                    'mst_theater_event_story_id': 0,
                    'mst_event_story_id': 0,
                    'mst_event_id': 0
                }
            },
            'prior_lot_rate_table_list': []
        }
    }

