from datetime import datetime, timedelta, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Profile, RecordTime, User
from mltd.models.schemas import (PendingJobSchema, PendingSongSchema,
                                 ProfileSchema, RecordTimeSchema, UserSchema)


@dispatcher.add_method(name='UserService.GetSelf', context_arg='context')
def get_self(params, context):
    """Service for getting self user info.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the user gives up a song or rehearsal.
    3. When the user starts or finishes a rehearsal.
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

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the game is transitioning to the theater screen.
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


@dispatcher.add_method(name='UserService.RecordTime',
                       context_arg='context')
def record_time(params, context):
    """Service for recording current time after performing an action.

    Invoked when the user has just performed an action that needs
    keeping track of (such as finished reading a tutorial).
    Args:
        params: A dict containing a single key 'kind', whose value is a
                string representing the kind of action performed.
    Returns:
        A dict containing a single key 'record_time', whose value is a
        dict representing the recorded time (same as current time) for
        the action. See the return value 'record_time_list' of the
        method 'UserService.GetRecordTimeList' for the dict definition.
    """
    with Session(engine) as session:
        record_time = RecordTime(
            user_id=UUID(context['user_id']),
            kind=params['kind'],
            time=datetime.now(timezone.utc)
        )
        session.add(record_time)

        record_time_schema = RecordTimeSchema()
        record_time_dict = record_time_schema.dump(record_time)

        session.commit()

    return {'record_time': record_time_dict}


@dispatcher.add_method(name='UserService.GetDirectMessage')
def get_direct_messages(params):
    """Service for getting a list of direct messages sent to the user.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the game is transitioning to the theater screen.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'message_list' with null
        value.
    """
    return {'message_list': None}


@dispatcher.add_method(name='UserService.GetPendingData',
                       context_arg='context')
def get_pending_data(params, context):
    """Service for getting pending song or job for a user.

    Invoked after logging in if there is a pending song or job.
    Args:
        params: A dict containing the following keys.
            live_token: A string representing the previous live token
                        generated by the game when starting the song
                        (an empty string for pending job).
            job_token: A string representing the previous job token
                       generated by the game when starting the job (an
                       empty string for pending song).
    Returns:
        A dict containing the following keys.
        pending_song: A dict representing the pending song (empty info
                      for pending job). Contains the following keys.
            unit_num: Unit number of the chosen unit (1-18).
            mst_song_id: Master song ID.
            mode: Solo or unit (1=Solo, 2=Unit).
            course: Course (1-6).
            guest_user_id: User ID of the guest.
            user_summary: A dict representing the guest user. See the
                          return value 'guest_list' of the method
                          'LiveService.GetRandomGuestList' for the dict
                          definition.
            start_date: Date when this song was started.
            is_available: true.
            is_expired: Whether this pending song is expired. This
                        happens when more than 24 hours has passed since
                        this song was started.
            is_rehearsal: Whether this pending song is a rehearsal.
            is_event_tour: false.
            guest_idol_type: Idol type of the guest helper card.
            use_song_unit: Whether the song unit should be used.
            is_live_support: Whether this is an auto live.
            life: Total life (calculated from the 5 cards in the unit
                  and the guest card).
            appeal: Total appeal value.
            threshold_list: A list of 6 ints representing the thresholds
                            for each score rank. The first int is 0,
                            followed by the thresholds for D, C, B, A
                            and S score ranks.
            song: A dict containing the pending song info. See the
                  return value 'song_list' of the method
                  'SongService.GetSongList' for the dict definition.
            use_full_random: Whether this song was started using Full
                             Random.
            use_song_random: Whether this song was started using Song
                             Random.
            seed: A random 32-bit signed int.
            is_valid: true.
            retry_count: The total number of retries for this song.
        pending_job: A dict representing the pending job (empty info
                     for pending song). Contains the following keys.
            token: A string representing the token generated by the
                   server for this pending job.
            is_chance: Whether there is a chance or challenge event for
                       this job.
            mst_job_id: Master job ID.
            mst_idol_id: Master idol ID of the idol for this job.
            text_scenario_id: A string for getting resources related to
                              text scenario.
            adv_scenario_id: A string for getting resources related to
                             chance or challenge event scenario (an
                             empty string if no chance or challenge
                             event).
            answer_list: A list of dicts representing the available
                         answers for the chance or challenge event
                         (null if no chance or challenge event of if the
                         chance event has no answers).
                         Each dict contains the following keys.
                scenario_id: Same as 'adv_scenario_id'.
                answer_key: A string for getting resources related to
                            this answer (for chance event with multiple
                            answers only).
                count: Number of times this answer has been chosen by
                       all users.
            text_background_id: A string for getting resources related
                                to text background.
            is_collab_available: false.
            is_adv_collab_available: false.
            adv_background_id: ''.
            is_challenge: Whether there is a challenge event for this
                          job.
            is_challenge_good: Whether the result of the challenge event
                               is good.
            is_valid: true.
    """
    result = {
        'pending_song': {
            'unit_num': 0,
            'mst_song_id': 0,
            'mode': 0,
            'course': 0,
            'guest_user_id': '',
            'user_summary': {
                'user_id': '',
                'name': '',
                'mst_achievement_id': 0,
                'mst_achievement_id_list': None,
                'comment': '',
                'level': 0,
                'lp': 0,
                'helper_card_list': None,
                'favorite_card': {
                    'card_id': '',
                    'mst_card_id': 0,
                    'mst_idol_id': 0,
                    'mst_costume_id': 0,
                    'bonus_costume_id': 0,
                    'rank5_costume_id': 0,
                    'resource_id': '',
                    'rarity': 0,
                    'idol_type': 0,
                    'exp': 0,
                    'level': 0,
                    'level_max': 0,
                    'life': 0,
                    'vocal': 0,
                    'vocal_base': 0,
                    'vocal_diff': 0,
                    'vocal_max': 0,
                    'vocal_master_bonus': 0,
                    'dance': 0,
                    'dance_base': 0,
                    'dance_diff': 0,
                    'dance_max': 0,
                    'dance_master_bonus': 0,
                    'visual': 0,
                    'visual_base': 0,
                    'visual_diff': 0,
                    'visual_max': 0,
                    'visual_master_bonus': 0,
                    'before_awakened_params': {
                        'life': 0,
                        'vocal': 0,
                        'dance': 0,
                        'visual': 0
                    },
                    'after_awakened_params': {
                        'life': 0,
                        'vocal': 0,
                        'dance': 0,
                        'visual': 0
                    },
                    'skill_level': 0,
                    'skill_level_max': 10,
                    'is_awakened': False,
                    'awakening_gauge': 0,
                    'awakening_gauge_max': 0,
                    'master_rank': 0,
                    'master_rank_max': 4,
                    'cheer_point': 0,
                    'center_effect': {
                        'mst_center_effect_id': 0,
                        'effect_id': 0,
                        'idol_type': 0,
                        'specific_idol_type': 0,
                        'attribute': 0,
                        'value': 0,
                        'song_idol_type': 0,
                        'attribute2': 0,
                        'value2': 0
                    },
                    'card_skill_list': None,
                    'ex_type': 0,
                    'create_date': '0001-01-01T00:00:00+0000',
                    'variation': 0,
                    'master_lesson_begin_date': '0001-01-01T00:00:00+0000',
                    'training_item_list': None,
                    'begin_date': '0001-01-01T00:00:00+0000',
                    'sort_id': 0,
                    'is_new': False,
                    'costume_list': None,
                    'card_category': 0,
                    'extend_card_params': {
                        'level_max': 0,
                        'life': 0,
                        'vocal_max': 0,
                        'vocal_master_bonus': 0,
                        'dance_max': 0,
                        'dance_master_bonus': 0,
                        'visual_max': 0,
                        'visual_master_bonus': 0
                    },
                    'is_master_lesson_five_available': False,
                    'barrier_mission_list': [],
                    'training_point': 0,
                    'sign_type': 0,
                    'sign_type2': 0
                },
                'favorite_card_before_awake': False,
                'producer_rank': 0,
                'is_friend': False,
                'lounge_id': '',
                'lounge_user_state': 0,
                'lounge_name': '',
                'create_date': '0001-01-01T00:00:00+0000',
                'last_login_date': '0001-01-01T00:00:00+0000'
            },
            'start_date': None,
            'is_available': False,
            'is_expired': False,
            'is_rehearsal': False,
            'is_event_tour': False,
            'guest_idol_type': 0,
            'use_song_unit': False,
            'is_live_support': False,
            'life': 0,
            'appeal': 0,
            'threshold_list': None,
            'song': {
                'song_id': '',
                'mst_song_id': 0,
                'mst_song': {
                    'mst_song_id': 0,
                    'sort_id': 0,
                    'resource_id': '',
                    'idol_type': 0,
                    'song_type': 0,
                    'kind': 0,
                    'stage_id': 0,
                    'stage_ts_id': 0,
                    'bpm': 0
                },
                'song_type': 0,
                'sort_id': 0,
                'released_course_list': None,
                'course_list': None,
                'is_released_mv': False,
                'is_released_horizontal_mv': False,
                'is_released_vertical_mv': False,
                'resource_id': '',
                'idol_type': 0,
                'kind': 0,
                'stage_id': 0,
                'stage_ts_id': 0,
                'bpm': 0,
                'is_cleared': False,
                'first_cleared_date': None,
                'is_played': False,
                'lp': 0,
                'is_visible': False,
                'apple_song_url': '',
                'google_song_url': '',
                'is_disable': False,
                'song_open_type': 0,
                'song_open_type_value': 0,
                'song_open_level': 0,
                'song_unit_idol_id_list': None,
                'mst_song_unit_id': 0,
                'idol_count': 0,
                'icon_type': 0,
                'extend_song_status': None,
                'unit_selection_type': 0,
                'only_default_unit': False,
                'only_extend': False,
                'is_off_vocal_available': False,
                'off_vocal_status': {
                    'is_released': False,
                    'cue_sheet': '',
                    'cue_name': ''
                },
                'song_permit_control': False,
                'permitted_mst_idol_id_list': None,
                'permitted_mst_agency_id_list': None,
                'extend_song_playable_status': 0,
                'is_new': False,
                'live_start_voice_mst_idol_id_list': None,
                'is_enable_random': False,
                'part_permitted_mst_idol_id_list': None,
                'is_recommend': False,
                'song_parts_type': 0
            },
            'use_full_random': False,
            'use_song_random': False,
            'seed': 0,
            'is_valid': False,
            'retry_count': 0
        },
        'pending_job': {
            'token': '',
            'is_chance': False,
            'mst_job_id': 0,
            'mst_idol_id': 0,
            'text_scenario_id': '',
            'adv_scenario_id': '',
            'answer_list': None,
            'text_background_id': '',
            'is_collab_available': False,
            'is_adv_collab_available': False,
            'adv_background_id': '',
            'is_challenge': False,
            'is_challenge_good': False,
            'is_valid': False
        }
    }

    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        if params['live_token']:
            if params['live_token'] != user.pending_song.live_token:
                raise ValueError('Game and server live_tokens do not match')
            start_date = user.pending_song.start_date.replace(
                tzinfo=timezone.utc)
            if start_date + timedelta(days=1) <= datetime.now(timezone.utc):
                user.pending_song.is_expired = True

            pending_song_schema = PendingSongSchema()
            result['pending_song'] = pending_song_schema.dump(
                user.pending_song)
        elif params['job_token']:
            if params['job_token'] != user.pending_job.job_token:
                raise ValueError('Game and server job_tokens do not match')

            pending_job_schema = PendingJobSchema()
            result['pending_job'] = pending_job_schema.dump(user.pending_job)

        session.commit()

    return result

