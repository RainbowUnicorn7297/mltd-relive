import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Friend, MstCourse, MstGameSetting,
                                MstScoreThreshold, PendingSong, Profile,
                                RandomLive, RandomLiveIdol, User)
from mltd.models.schemas import GuestSchema, RandomLiveSchema
from mltd.servers.config import server_timezone
from mltd.services.user import update_vitality


@dispatcher.add_method(name='LiveService.GetRandomLive', context_arg='context')
def get_random_live(params, context):
    """Service for getting random live info for a user.

    Invoked when the game is transitioning to the song selection screen,
    either for the first time after the game boots up or after finishing
    any live performance.
    Args:
        params: A dict containing a single key named 'random_live_type',
                whose value is an int representing the requested random
                live type (1-2).
                1=Full Random (隨機公演)
                2=Song Random (隨機選曲)
                Normally this value is 2 only, because this method is 
                used by the game to check whether a random song has
                already been selected previously. For Full Random, after
                choosing the random song, it is immediately started.
    Returns:
        A dict containing a single key named 'random_live', whose value
        is a dict that represents previously generated random live info
        and contains the following keys.
            random_live_type: Random live type. See 'params' above.
            mst_song_id: If there was a previously selected random song
                         that has not been played, this is the master
                         song ID of that selected song. Otherwise, this
                         value is 0.
            mode: Solo or unit (1=Solo, 2=Unit).
            course: Course chosen by the user when selecting this random
                    live (1-6).
            live_ticket_count: For live tickets, this is the number of
                               live tickets that will be used. For
                               vitality, this value is 0.
            unit_song_type: 0.
            idol_list: null.
    """
    random_live_dict = {
        'random_live_type': params['random_live_type'],
        'mst_song_id': 0,
        'mode': 0,
        'course': 0,
        'live_ticket_count': 0,
        'unit_song_type': 0,
        'idol_list': None
    }

    with Session(engine) as session:
        random_live = session.scalar(
            select(RandomLive)
            .where(RandomLive.user_id == UUID(context['user_id']))
            .where(RandomLive.random_live_type == params['random_live_type'])
        )

        if random_live:
            random_live_schema = RandomLiveSchema()
            random_live_dict = random_live_schema.dump(random_live)

    return {'random_live': random_live_dict}


@dispatcher.add_method(name='LiveService.SetRandomLive', context_arg='context')
def set_random_live(params, context):
    """Service for setting random live info for a user.

    Invoked when the user confirms selecting random song, cards and
    costumes for Full Random, or selecting a random song for Song
    Random.
    The song, cards and costumes are randomly selected by the game
    client. This method is merely used to persist this info on the
    server. When the user has finished the random live performance, this
    info will be cleared.
    Args:
        params: A dict containing the following keys.
            random_live_type: Random live type (1-2).
                              1=Full Random (隨機公演)
                              2=Song Random (隨機選曲)
            mst_song_id: Master song ID.
            mode: Solo or unit (1=Solo, 2=Unit).
            course: Course (1-6).
            live_ticket_count: For live tickets, this is the number of
                               live tickets that will be used. For
                               vitality, this value is 0.
            use_song_unit: false.
            card_id_list: For Full Random, this is a list of 5 card IDs
                          representing the randomly chosen cards that
                          will be used for the live performance. The
                          order of this list is important. The first
                          card ID in this list is the center of this
                          unit. For Song Random, this is an empty list.
            mst_costume_id_list: For Full Random, this is a list of 5
                                 master costume IDs representing the
                                 randomly chosen costumes for each card
                                 in 'card_id_list' above. For Song
                                 Random, this is an empty list.
            unit_election: 0.
            skill_election: An int with encoded bit flags representing
                            the skill type(s) the user wants on the
                            randomly selected cards.
                            Meanings of bit flags:
                                3rd bit (0x04) = Healer
                                4th bit (0x08) = Life Guard
                                8th bit (0x80) = Multi Up
                            Meanings of int values:
                                0=No desired skills
                                4=Healer
                                8=Life Guard
                                12=Healer and Life Guard
                                128=Multi Up
                                132=Healer and Multi Up
                                136=Life Guard and Multi Up
                                140=Healer, Life Guard and Multi Up
            song_election: 0.
    Returns:
        A dict containing a single key named 'random_live', whose value
        is a dict that represents the random live info that will be
        persisted on the server and contains the following keys.
            random_live_type: See 'params' above.
            mst_song_id: See 'params' above.
            mode: See 'params' above.
            course: See 'params' above.
            live_ticket_count: See 'params' above.
            unit_song_type: 0.
            idol_list: For Song Random, this value is null. For Full
                       Random, this is a list of 5 dicts representing
                       the idols that will be performing in this random
                       live. Each dict contains the following keys.
                card_id: Card ID for this idol.
                mst_costume_id: Master costume ID of the costume for
                                this idol.
                mst_lesson_wear_id: 0.
                costume_is_random: false.
                costume_random_type: 0.
    """
    with Session(engine) as session:
        random_live = RandomLive(
            user_id=UUID(context['user_id']),
            random_live_type=params['random_live_type'],
            mst_song_id=params['mst_song_id'],
            mode=params['mode'],
            course=params['course'],
            live_ticket_count=params['live_ticket_count']
        )
        if random_live.random_live_type == 1:
            for i in range(5):
                random_live.random_live_idols.append(RandomLiveIdol(
                    position=i+1,
                    card_id=params['card_id_list'][i],
                    mst_costume_id=params['mst_costume_id_list'][i]
                ))
        session.add(random_live)

        session.commit()

        random_live_schema = RandomLiveSchema()
        random_live_dict = random_live_schema.dump(random_live)

    return {'random_live': random_live_dict}


@dispatcher.add_method(name='LiveService.GetRandomGuestList',
                       context_arg='context')
def get_random_guest_list(params, context):
    """Service for getting a list of random guests for a user.

    Invoked after the user has selected a song and is transitioning to
    the guest selection screen.
    Usually a total of 20 guests will be randomly selected. Sometimes it
    is slightly less, presumably due to certain users being selected
    more than once. This method will first attempt to select as many as
    15 friends, then select the remainder from all users.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'guest_list', whose value
        is a list of dicts, each representing a single guest. Each dict
        contains the following keys.
            user_id: User ID of the guest.
            name: Display name of the guest.
            mst_achievement_id: Master achievement ID of the main
                                achievement displayed in guest's
                                profile.
            mst_achievement_id_list: A list of maximum 52 master
                                     achievement IDs representing the
                                     achievements displayed in guest's
                                     profile.
            comment: Guest comment.
            level: Guest level.
            lp: Guest LP.
            helper_card_list: See the return value 'helper_card_list' of
                              the method 'UserService.GetSelfProfile'.
            favorite_card: A dict representing guest's favorite card.
                           See the return value 'card_list' of the
                           method 'CardService.GetCardList' for the dict
                           definition.
            favorite_card_before_awake: Whether the displayed favorite
                                        card should use before awakened
                                        artwork or not.
            producer_rank: Guest's producer rank (1-8).
            is_friend: Whether the guest is a friend of this user.
            lounge_id: Guest's lounge ID.
            lounge_user_state: An int representing the guest state for
                               lounge.
                               0 = Not in any lounge.
                               3 = Joined a lounge as a member.
            lounge_name: Displayed lounge name chosen by the lounge
                         owner.
            create_date: The date when the guest first registered.
            last_login_date: Last login date of the guest.
    """
    with Session(engine) as session:
        friends = session.scalars(
            select(Profile)
            .join(Friend, Friend.friend_id == Profile.id_)
            .where(Friend.user_id == UUID(context['user_id']))
            .order_by(func.random())
            .limit(15)
        ).all()
        friend_ids = [friend.id_ for friend in friends]
        other_guests = session.scalars(
            select(Profile)
            .where(Profile.id_ != UUID(context['user_id']))
            .where(~Profile.id_.in_(friend_ids))
            .order_by(func.random())
            .limit(20 - len(friends))
        ).all()

        guest_schema = GuestSchema()
        guest_list = guest_schema.dump(friends, many=True)
        guest_list.extend(guest_schema.dump(other_guests, many=True))
        for guest in guest_list:
            guest['is_friend'] = UUID(guest['user_id']) in friend_ids

    return {'guest_list': guest_list}


@dispatcher.add_method(name='LiveService.StartSong', context_arg='context')
def start_song(params, context):
    """Service for starting a song for a user.

    Invoked when the user presses Start Live button.
    Args:
        params: A dict containing the following keys.
            unit_num: Unit number of the chosen unit (1-18).
            use_song_unit: Whether the song unit should be used.
            mst_song_id: Master song ID.
            mode: Solo or unit (1=Solo, 2=Unit).
            course: Course (1-6).
            live_ticket: For live tickets, this is the number of live
                         tickets that will be used. For vitality, this
                         value is 0.
            live_ticket_count: For live tickets, this is the chosen
                               multiplier (how many times of the minimum
                               live tickets required to play the
                               course). For vitality, this value is 0.
            macaroon_count: 0.
            tour_count: 0.
            guest_user_id: User ID of the guest.
            appeal: Total appeal value.
            unit_appeal: Appeal value from the chosen unit.
            support_appeal: Appeal value from support.
            speed: Related to game setting.
            timing: Related to game setting.
            note_design: Related to game setting.
            is_line_support: Related to game setting.
            user_live_view: Related to game setting.
            user_live_quality: Related to game setting.
            user_mv_quality: Related to game setting.
            guest_idol_type: Idol type of the guest helper card.
            is_event_tour: false.
            is_live_support: Whether this is an auto live.
            life: Total life (calculated from the 5 cards in the unit
                  and the guest card).
            use_boost: false.
            use_full_random: Whether this song was started using Full
                             Random.
            use_song_random: Whether this song was started using Song
                             Random.
            speed_by_course: An int representing speed by course in game
                             setting.
            live_token: A unique string representing the token for this
                        live.
            visual_mode: Related to game setting.
            solo_live_camera: Related to game setting.
            back_ground_filter3_d: Related to game setting.
            back_ground_filter2_d: Related to game setting.
            auto_darken_back_ground_in_auto_live: Related to game
                                                  setting.
            back_ground_image2_d: Related to game setting.
            increase_note_size: Related to game setting.
            note_target_with_unit: Related to game setting.
            note_target_with_solo: Related to game setting.
            note_target_interval: Related to game setting.
    Returns:
        A dict containing the following keys.
        mst_song_id: Master song ID.
        live_mode: Solo or unit (1=Solo, 2=Unit).
        course_id: Course (1-6).
        start_date: Date when this song was started. Same as current
                    server time because the song is starting.
        guest_user_id: User ID of the guest.
        unit_num: Unit number of the chosen unit (1-18).
        threshold: Threshold for S score rank.
        threshold_list: A list of 6 ints representing the thresholds for
                        each score rank. The first int is 0, followed by
                        the thresholds for D, C, B, A and S score ranks.
        result_vitality: A dict representing the resulting vitality for
                         the user. Contains the following keys.
            before_vitality: Vitality of the user before starting this
                             song.
            after_vitality: Vitality of the user after starting this
                            song. If live tickets were used, this value
                            is the same as 'before_vitality'.
            full_recover_date: The time when vitality will be fully
                               recovered after starting this song.
        seed: A random 32-bit signed int.
        current_event: A dict containing the following keys.
            mst_event_id: 0.
            event_type: 0.
            begin_date: null.
            end_date: null.
    """
    now = datetime.now(timezone.utc)
    seed = random.randint(-2_147_483_648, 2_147_483_647)
    with Session(engine) as session:
        level_subq = (
            select(MstCourse.level)
            .where(MstCourse.mst_song_id == params['mst_song_id'])
            .where(MstCourse.course_id == params['course'])
            .scalar_subquery()
        )
        threshold_list = session.scalar(
            select(MstScoreThreshold.score_threshold_list)
            .where(MstScoreThreshold.level == level_subq)
        )
        threshold_list = [int(x) for x in threshold_list.split(',')]

        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        update_vitality(user)
        before_vitality = user.vitality
        if not params['live_ticket']:
            cost = session.scalar(
                select(MstCourse.cost)
                .where(MstCourse.mst_song_id == params['mst_song_id'])
                .where(MstCourse.course_id == params['course'])
            )
            user.vitality -= cost
            if user.vitality < 0:
                raise RuntimeError('vitality cannot be negative')
            user.full_recover_date = (
                user.full_recover_date.replace(tzinfo=timezone.utc)
                if before_vitality < user.max_vitality
                else now) + timedelta(seconds=cost*user.auto_recover_interval)
        else:
            user.live_ticket -= params['live_ticket']
            if user.live_ticket < 0:
                raise RuntimeError('live_ticket cannot be negative')
        after_vitality = user.vitality
        full_recover_date = user.full_recover_date.replace(tzinfo=timezone.utc)

        if params['use_full_random']:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 1)
            ).one()
            session.delete(random_live)
        elif params['use_song_random']:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 2)
            ).one()
            session.delete(random_live)

        session.add(PendingSong(
            user_id=user.user_id,
            live_token=params['live_token'],
            unit_num=params['unit_num'],
            mst_song_id=params['mst_song_id'],
            mode=params['mode'],
            course=params['course'],
            guest_user_id=UUID(params['guest_user_id']),
            start_date=now,
            guest_idol_type=params['guest_idol_type'],
            use_song_unit=params['use_song_unit'],
            is_live_support=params['is_live_support'],
            life=params['life'],
            appeal=params['appeal'],
            use_full_random=params['use_full_random'],
            use_song_random=params['use_song_random'],
            seed=seed,
            is_valid=True
        ))

        session.commit()

    return {
        'mst_song_id': params['mst_song_id'],
        'live_mode': params['mode'],
        'course_id': params['course'],
        'start_date': now.astimezone(server_timezone),
        'guest_user_id': params['guest_user_id'],
        'unit_num': params['unit_num'],
        'threshold': threshold_list[-1],
        'threshold_list': threshold_list,
        'result_vitality': {
            'before_vitality': before_vitality,
            'after_vitality': after_vitality,
            'full_recover_date': full_recover_date
        },
        'seed': seed,
        'current_event': {
            'mst_event_id': 0,
            'event_type': 0,
            'begin_date': None,
            'end_date': None
        }
    }


@dispatcher.add_method(name='LiveService.ContinueSong', context_arg='context')
def continue_song(params, context):
    """Service for continuing a song for a user.

    Invoked when life reaches zero during live and the user chooses to
    continue by spending jewels.
    Args:
        params: A dict containing a single key named 'retry_count',
                whose value is the total number of retries for this
                song.
    Returns:
        A dict containing a single key named 'retry_count', whose value
        is the same as 'retry_count' above.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        user.pending_song.retry_count = params['retry_count']

        continue_jewel_amount = session.scalar(
            select(MstGameSetting.continue_jewel_amount)
        )
        user.jewel.free_jewel_amount -= continue_jewel_amount
        if user.jewel.free_jewel_amount < 0:
            raise RuntimeError('free_jewel_amount cannot be negative')

        session.commit()

    return {'retry_count': params['retry_count']}


@dispatcher.add_method(name='LiveService.BreakSong', context_arg='context')
def break_song(params, context):
    """Service for giving up a song for a user.

    Invoked when life reaches zero or the game was paused or restarted
    during a song, and the user chooses to give up.
    Args:
        params: A dict containing the following keys.
            score: 0.
            score_rank: 0.
            combo: 0.
            combo_rank: 0.
            count_list: [].
            life: 0.
            seconds: Number of seconds since the beginning of the song.
    Returns:
        See the implementation below.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        user.pending_song = None

        session.commit()

    return {
        'is_event_tour': False,
        'is_event_twin_stage': False,
        'event_additional_status': {
            'boost_start_date': None,
            'boost_lifetime': 0,
            'interval_start_date': None,
            'interval_lifetime': 0,
            'boost_amount': 0,
            'max_boost_amount': 0
        },
        'played_event_type': 0
    }

