from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Profile, RecordTime, User
from mltd.models.schemas import ProfileSchema, RecordTimeSchema, UserSchema


@dispatcher.add_method(name='UserService.GetSelf', context_arg='context')
def get_self(params, context):
    """Service for getting self user info.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing user info. See the return value 'user' of
        AuthService.Login method for the definition.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()

        user_schema = UserSchema()
        user_dict = user_schema.dump(user)

    return user_dict


@dispatcher.add_method(name='UserService.GetSelfProfile',
                       context_arg='context')
def get_self_profile(params, context):
    """Service for getting self profile.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: Either an empty dict or a dict with empty profile info.
                See the return value below for the dict definition.
    Returns:
        A dict containing profile info. Contains the following keys.
        id: User ID in UUID format.
        name: Display name chosen by the user.
        birthday: A string representing user birthday in 'MMDD' format.
        is_birthday_public: Whether user birthday is publicly visible.
        comment: User comment.
        favorite_card_id: Card ID of user's favorite card.
        favorite_card_before_awake: Whether the displayed favorite card
                                    should use before awakened artwork
                                    or not.
        helper_card_id_list: A list of 4 dicts representing the helper
                             card IDs chosen by the user for each idol
                             type. Each dict contains the following
                             keys.
            idol_type: Idol type (1-4).
            card_id: Card ID of the chosen helper card for this idol
                     type.
        mst_achievement_id: Master achievement ID of the main
                            achievement chosen by the user to be
                            displayed on their profile.
        mst_achievement_id_list: A list of maximum 52 ints representing
                                 the master achievement IDs of the
                                 achievements chosen by the user to be
                                 displayed on their profile.
        helper_card_list: A list of 4 dicts representing the helper
                          cards chosen by the user for each idol type.
                          Each dict contains the following keys.
            idol_type: Idol type (1-4).
            card: A dict representing the chosen helper card for this
                  idol type. See the return value 'card_list' of the
                  method 'CardService.GetCardList' for the dict
                  definition.
        favorite_card: A dict representing user's favorite card. See the
                       return value 'card_list' of the method
                       'CardService.GetCardList' for the dict
                       definition.
        lp: User LP.
        album_count: Number of unlocked cards in user's card album.
        story_count: How many story episodes the user has read.
        clear_song_count_list: A list of 6 dicts representing the number
                               of cleared songs for each course. Each
                               dict contains the following keys.
            live_course: Course ID (1-6).
            count: Number of songs cleared for this course.
        full_combo_song_count_list: A list of 6 dicts representing the
                                    number of full-comboed songs for
                                    each course. Each dict contains the
                                    following keys.
            live_course: Course ID (1-6).
            count: Number of songs full comboed for this course.
    """
    with Session(engine) as session:
        profile = session.scalars(
            select(Profile)
            .where(Profile.id_ == UUID(context['user_id']))
        ).one()

        profile_schema = ProfileSchema()
        profile_dict = profile_schema.dump(profile)

    return profile_dict


@dispatcher.add_method(name='UserService.GetRecordTimeList',
                       context_arg='context')
def get_record_time_list(params, context):
    """Service for getting a list of recorded times for user actions.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'record_time_list', whose
        value is a list of dicts representing the recorded time for
        each action previously performed by the user (such as finished
        reading a tutorial). Each dict contains the following keys.
            kind: A string representing the kind of action performed.
            time: The time when the user performed this action.
    """
    with Session(engine) as session:
        record_times = session.scalars(
            select(RecordTime)
            .where(RecordTime.user_id == UUID(context['user_id']))
        ).all()

        record_time_schema = RecordTimeSchema()
        record_time_list = record_time_schema.dump(record_times, many=True)
        if not record_times:
            record_time_list = None

    return {'record_time_list': record_time_list}


@dispatcher.add_method(name='UserService.GetDirectMessage')
def get_direct_messages(params):
    """Service for getting a list of direct messages sent to the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'message_list' with null
        value.
    """
    return {'message_list': None}

