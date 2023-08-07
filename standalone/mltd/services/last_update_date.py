from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import LastUpdateDate
from mltd.models.schemas import LastUpdateDateSchema


@dispatcher.add_method(name='LastUpdateDateService.GetLastUpdateDateList',
                       context_arg='context')
def get_last_update_date_list(params, context):
    """Service for getting a list of last update dates for a user.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the game is transitioning to the theater screen.
    It is unclear what the last update dates mean or what they are used
    for. My current guess is the game client uses these dates to
    determine whether any of its previously cached game data needs to be
    refreshed. If this is the case, it is important to set the dates
    correctly.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        last_update_date_list: A list of 17 dicts containing last update
                               date info. Each dict contains the
                               following keys.
            last_update_date_type: Last update date type (1-17).
                                   1=Present?
                                   2=?
                                   3=?
                                   4=?
                                   5=?
                                   8=Announcement?
            last_update_date: Last update date
                              ('0001-01-01T00:00:00+0000' if none).
        announce_pop_up_status: A dict representing a pop-up
                                announcement. Contains the following
                                keys.
            announce_web_view_link: A URL to the announcement web view.
            announcement_type: Announcement type.
            last_update_date: Last update date.
        mobile_unread_status: A dict containing mobile unread status
                              info. Contains the following keys.
            is_new_mail: Whether there is any new mail.
            is_new_blog: Whether there is any new blog.
    """
    with Session(engine) as session:
        last_update_dates = session.scalars(
            select(LastUpdateDate)
            .where(LastUpdateDate.user_id == UUID(context['user_id']))
        ).all()

        last_update_date_schema = LastUpdateDateSchema()
        last_update_date_list = last_update_date_schema.dump(last_update_dates,
                                                             many=True)

        # TODO: Check mobile unread status
        is_new_mail = False
        is_new_blog = False

    return {
        'last_update_date_list': last_update_date_list,
        'announce_pop_up_status': {
            'announce_web_view_link': 'https://webview-dot-theaterdays-zh'
                + '.appspot.com/info/google#/update'
                + '/d26235aa-7f22-4588-8c64-d6bd6fbc211f',
            'announce_type': 3,
            'last_update_date': '2022-01-27T04:00:00+0000'
        },
        'mobile_unread_status': {
            'is_new_mail': is_new_mail,
            'is_new_blog': is_new_blog
        }
    }

