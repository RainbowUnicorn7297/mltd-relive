import random
from datetime import datetime, timedelta, timezone
from decimal import ROUND_DOWN, Decimal
from enum import Enum
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Card, Costume, Course, Friend, Item, LP,
                                MainStoryChapter, Memorial, Mission, MstCard,
                                MstCostume, MstCourse, MstCourseReward,
                                MstGameSetting, MstItem, MstMainStory,
                                MstMainStoryContactStatus, MstMemorial,
                                MstMission, MstRewardItem, MstScoreThreshold,
                                MstTheaterRoomStatus, PendingSong, Profile,
                                RandomLive, RandomLiveIdol, Song, SongUnit,
                                Unit, User)
from mltd.models.schemas import (CardSchema, GashaMedalSchema, GuestSchema,
                                 IdolSchema, ItemSchema, MemorialSchema,
                                 MissionSchema, MstRewardItemSchema,
                                 PendingSongSchema, RandomLiveSchema,
                                 SongSchema, SongUnitSchema, UnitSchema,
                                 UserSchema)
from mltd.servers.config import server_timezone
from mltd.servers.i18n import translation
from mltd.services.card import add_card
from mltd.services.game_setting import get_item_day_idol_type
from mltd.services.item import add_item
from mltd.services.mission import update_mission_progress

_ = translation.gettext


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
    server. When the user has finished or given up the random live
    performance, this info will be cleared.
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
        threshold_list_str = session.scalar(
            select(MstScoreThreshold.score_threshold_list)
            .where(MstScoreThreshold.level == level_subq)
        )
        threshold_list = [int(x) for x in threshold_list_str.split(',')]

        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        before_vitality = user.vitality
        after_vitality = before_vitality
        if not params['live_ticket']:
            cost = session.scalar(
                select(MstCourse.cost)
                .where(MstCourse.mst_song_id == params['mst_song_id'])
                .where(MstCourse.course_id == params['course'])
            )
            after_vitality -= cost
            if after_vitality < 0:
                raise RuntimeError('vitality cannot be negative')
            if after_vitality < user.max_vitality:
                user.full_recover_date = (
                    user.full_recover_date.replace(tzinfo=timezone.utc)
                    if before_vitality < user.max_vitality
                    else now
                ) + timedelta(seconds=cost * user.auto_recover_interval)
        else:
            user.live_ticket -= params['live_ticket']
            if user.live_ticket < 0:
                raise RuntimeError('live_ticket cannot be negative')
        full_recover_date = user.full_recover_date.replace(tzinfo=timezone.utc)
        user.vitality = after_vitality

        is_friend = False
        if params['guest_user_id']:
            friend_id = session.scalar(
                select(Friend.friend_id)
                .where(Friend.user_id == user.user_id)
                .where(Friend.friend_id == UUID(params['guest_user_id']))
            )
            is_friend = friend_id is not None

        user.pending_song = PendingSong(
            user_id=user.user_id,
            live_token=params['live_token'],
            unit_num=params['unit_num'],
            mst_song_id=params['mst_song_id'],
            mode=params['mode'],
            course=params['course'],
            guest_user_id=(None if not params['guest_user_id']
                           else UUID(params['guest_user_id'])),
            start_date=now,
            guest_idol_type=params['guest_idol_type'],
            use_song_unit=params['use_song_unit'],
            is_live_support=params['is_live_support'],
            life=params['life'],
            appeal=params['appeal'],
            use_full_random=params['use_full_random'],
            use_song_random=params['use_song_random'],
            seed=seed,
            is_valid=True,
            threshold_list=threshold_list_str,
            song_id=f'{user.user_id}_{params["mst_song_id"]}',
            is_friend=is_friend,
            live_ticket=params['live_ticket']
        )
        session.expire(user, ['pending_song'])

        song = user.pending_song.song
        if not song.is_played:
            song.is_played = True
        if song.is_new:
            song.is_new = False

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


@dispatcher.add_method(name='LiveService.RestartSong', context_arg='context')
def restart_song(params, context):
    """Service for resuming a pending song for a user.

    Invoked when the game was restarted during a song and the user
    chooses to continue.
    Args:
        params: A dict containing the following keys.
            live_token: A string representing the previous live token
                        generated by the game when starting the song.
            second: Number of seconds since the beginning of the song.
            is_two_d: Whether the user chooses to continue the song in
                      2D mode.
    Returns:
        A dict containing a single key named 'pending_song', whose value
        is a dict representing pending song info. See the return value
        'pending_song' of the method 'UserService.GetPendingData' for
        the dict definition.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        if params['live_token'] != user.pending_song.live_token:
            raise ValueError('Game and server live_tokens do not match')

        pending_song_schema = PendingSongSchema()
        pending_song = pending_song_schema.dump(user.pending_song)

    return {'pending_song': pending_song}


@dispatcher.add_method(name='LiveService.BreakSong', context_arg='context')
def break_song(params, context):
    """Service for giving up a song for a user.

    Invoked in the following situations.
    1. When life reaches zero or the game was paused or restarted during
       a song, and the user chooses to give up.
    2. When the pending song is expired.
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

        if user.pending_song.use_full_random:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 1)
            ).one()
            session.delete(random_live)
        elif user.pending_song.use_song_random:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 2)
            ).one()
            session.delete(random_live)
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


@dispatcher.add_method(name='LiveService.FinishSong', context_arg='context')
def finish_song(params, context):
    """Service for finishing a song for a user.

    Invoked after clearing a song.
    Args:
        params: A dict containing the following keys.
            score: Score obtained for this song.
            score_rank: Score rank (0-5).
                        0=No rank
                        1=D rank
                        2=C rank
                        3=B rank
                        4=A rank
                        5=S rank
            combo: Highest combo obtained for this song.
            max_combo: Maximum possible combo (same as total number of
                       notes).
            count_list: A list of 6 ints representing the number of
                        PERFECT, GREAT, GOOD, SLOW, FAST and MISS notes.
            life: Current vitality of the user.
            seconds: Number of seconds since the beginning of the song.
            sp_appeal_success: Whether the special appeal note was
                               successfully pressed.
            live_token: A string representing the previous live token
                        generated by the game when starting the song.
            request: false.
            nonce: A 32-byte nonce in Base64 format.
            recovered_life: Life recovered during the song.
            damaged_life: Damage received during the song.
            skill_count_list: A list of 5 ints representing the total
                              number of skill activations for each card.
            support_card_id_list: A list of 10 card IDs representing the
                                  support cards.
    Returns:
        A dict containing the following keys.
        result_user: A dict representing the changes to user info after
                     playing this song. Contains the following keys.
            level_up: Whether the user levels up after this song.
            before_level: User level before this song.
            after_level: User level after this song.
            rank_up: Whether the producer rank increases after this
                     song.
            before_rank: Producer rank before this song.
            after_rank: Producer rank after this song.
            rank_reward: A dict representing the reward for increasing
                         the producer rank (empty info if producer rank
                         does not increase). See the return value
                         'reward_item_list' of the method
                         'IdolService.GetIdolList' for the dict
                         definition.
            before_vitality: User vitality before leveling up.
            after_vitality: User vitality after leveling up.
            before_max_vitality: Maximum possible vitality before
                                 leveling up.
            after_max_vitality: Maximum possible vitality after leveling
                                up.
            before_live_ticket: Number of live tickets.
            after_live_ticket: Same as 'before_live_ticket'.
            before_max_friend: Maximum possible number of friends before
                               leveling up.
            after_max_friend: Maximum possible number of friends after
                              leveling up.
            before_theater_fan: Total number of theater fans before this
                                song.
            after_theater_fan: Total number of theater fans after this
                               song.
            before_live_point: User LP before this song.
            after_live_point: User LP after this song.
            before_song_live_point: Song LP before this song.
            after_song_live_point: Song LP after this song.
            before_money: Amount of money before this song.
            after_money: Amount of money after this song.
            before_exp: Total user EXP before this song.
            after_exp: Total user EXP after this song.
            before_exp_gauge: How much the EXP gauge was filled up in %
                              (rounded down to the nearest integer)
                              before this song.
            after_exp_gauge: How much the EXP gauge is filled up in %
                             after this song. If the user levels up,
                             this value is greater than or equal to 100.
            exp: Current user EXP after this song.
            next_exp: Required user EXP for leveling up after this song.
            full_recover_date: Date when vitality will be fully
                               recovered after this song.
            map_level: A dict representing current map level of the user
                       after this song. See thes return value
                       'map_level' of the method 'AuthService.Login' for
                       the dict definition.
            release_all_live_course: Whether all live courses should be
                                     released as a result of leveling up
                                     to 50 after this song. This value
                                     is true only if the user was below
                                     level 50 before this song and at or
                                     above level 50 after this song.
            before_training_point: 0.
            after_training_point: 0.
            total_training_point: 0.
        result_idol_list: A list of 5 dicts representing the changes to
                          idol info after playing this song. Each dict
                          corresponds to the card and idol in the
                          selected unit. For a song unit with 13 cards
                          and idols, this list corresponds to the first
                          5 positions. The same idol can appear multiple
                          times in this list if multiple cards of this
                          idol were selected for the unit. For solo
                          songs, only the first card and idol (center)
                          will have their values increased. Each dict
                          contains the following keys.
            mst_idol_id: Master idol ID.
            before_awake_gauge: Awakening gauge value of the card before
                                this song.
            after_awake_gauge: Awakening gauge value of the card after
                               this song.
            max_awake_gauge: Maximum possible awakening gauge value of
                             the card.
            before_fan: Number of fans for this idol before this song.
                        If the same idol has appeared before in this
                        list, this value is the 'after_fan' value of the
                        last entry.
            after_fan: Number of fans for this idol after this song. If
                       the same idol has appeared before in this list,
                       this is the resulting value by adding the
                       additional fans gained at this position to
                       'before_fan'.
            before_affection: Affection value for this idol before this
                              song. If the same idol has appeared before
                              in this list, this value is the
                              'after_affection' value of the last entry.
            after_affection: Affection value for this idol after this
                             song. If the same idol has appeared before
                             in this list, this is the resulting value
                             by adding the additional affection gained
                             at this position to 'before_affection'.
            memorial_status: A dict representing the memorial unlocked
                             by obtaining the required affection value
                             after this song (empty memorial info if no
                             memorial is unlocked). See the return value
                             'memorial_list' of the method
                             'IdolService.GetIdolList' for the dict
                             definition.
            memorial_list: A list containing a single dict exactly the
                           same as 'memorial_status' above (null if no
                           memorial is unlocked).
        result_gasha_medal: A dict representing the changes to gasha
                            medal info after playing this song (empty
                            info if no changes). Contains the following
                            keys.
            before_gauge: Gasha medal point amount before this song.
            after_gauge: Gasha medal point amount to be added after this
                         song.
            get_point: Same as 'after_gauge'.
            count: If the total gasha medal point amount after this song
                   is greater than or equal to 100, this is the number
                   of gasha medals gained by converting every 100 point
                   amount into 1 medal. Otherwise, this value is 0.
            expire_date: Expiry date of the newly obtained gasha medals
                         ('0001-01-01T00:00:00+0000' if no gasha medal
                         was gained).
            is_over: Whether the total number of gasha medals the user
                     owns reaches the maximum possible number (10) after
                     this song.
        live_result_reward: A dict representing the changes to score/
                            combo/clear ranks and related rewards after
                            playing this song. Contains the following
                            keys.
            before_score_rank: Score rank before this song (0-4).
            after_score_rank: Score rank after this song (0-4).
            before_combo_rank: Combo rank before this song (0-4).
            after_combo_rank: Combo rank after this song (0-4).
            before_clear_rank: Clear rank before this song (0-4).
            after_clear_rank: Clear rank after this song (0-4).
            score_reward_item_list: null.
            combo_reward_item_list: null.
            clear_reward_item_list: null.
            course_reward: A dict containing the following keys.
                score_reward_item_list: A list of 4 dicts representing
                                        the reward items for obtaining
                                        score ranks 1-4. Each dict
                                        contains the following keys.
                    rank: Score/Combo/Clear rank (1-4).
                    reward: A dict representing the reward item for this
                            score/combo/clear rank. See the return value
                            'reward_item_list' of the method
                            'IdolService.GetIdolList' for the dict
                            definition.
                    threshold: Threshold for this score/combo/clear
                               rank.
                    status: An int representing the status of this
                            reward.
                            0=Not yet obtained
                            1=Already obtained previously
                            2=Just obtained after this song
                combo_reward_item_list: A list of 4 dicts representing
                                        the reward items for obtaining
                                        combo ranks 1-4. See
                                        'score_reward_item_list' above
                                        for the dict definition.
                clear_reward_item_list: A list of 4 dicts representing
                                        the reward items for obtaining
                                        clear ranks 1-4. See
                                        'score_reward_item_list' above
                                        for the dict definition.
        live_result_drop_reward: A dict representing the random drop
                                 rewards after playing this song.
                                 Contains the following key.
            drop_reward_box_list: A list of dicts (null if no drop
                                  rewards). Each dict contains the
                                  following key.
                drop_reward_item: A dict representing the drop reward
                                  item. See the return value
                                  'reward_item_list' of the method
                                  'IdolService.GetIdolList' for the dict
                                  definition.
                substitute_list: null.
                drop_reward_group_type: 1.
        song: A dict representing the new song info after playing this
              song. See the return value 'song_list' of the method
              'SongService.GetSongList' for the dict definition.
        live_result_rank: Score rank obtained (0-4).
                          0=D rank or below
                          1=C rank
                          2=B rank
                          3=A rank
                          4=S rank
        live_play_rank: Score rank obtained (0-5). Same as 'score_rank'
                        in 'params'.
        combo_rank: Combo rank obtained (0-4).
        count_list: Same as 'count_list' in 'params'.
        is_full_combo: Whether this is full combo.
        is_new_record: Whether this is a new record.
        guest: A dict representing the guest user. See the return value
               'guest_list' of the method
               'LiveService.GetRandomGuestList' for the dict definition.
        guest_idol_type: Idol type of the guest helper card.
        release_mst_main_story_id: Master main story ID of the unlocked
                                   main story as a result of playing
                                   this song (0 if no main story
                                   unlocked).
        mst_room_id: Master room ID for the intro contact of the
                     unlocked main story (0 if no main story unlocked).
        unit: A dict representing the selected unit for this song. See
              the return value 'unit_list' of the method
              'UnitService.GetUnitList' for the dict definition. For
              song unit and Full Random, unit_num is 0 and idol list
              contains 5 idols only.
        mission_process: A dict representing changes in mission states
                         after playing this song. Contains the following
                         keys.
            complete_mission_list: A list of dicts representing missions
                                   that have just been completed (empty
                                   if none). See the return value
                                   'mission_list' of the method
                                   'MissionService.GetMissionList' for
                                   the dict definition.
            open_mission_list: An empty list.
            training_point_diff: Unknown. Contains the following keys.
                before: 0.
                after: 0.
                total: 0.
        mission_list: A list of dicts representing missions with changed
                      states. This list is the same as
                      'complete_mission_list' above.
        over_capacity_info: A dict containing the following keys.
            money: Whether the amount of money exceeds the maximum
                   possible amount of money after this song.
            live_ticket: false.
        result_gasha_ticket: A dict containing the following keys.
            before_gauge: 0.
            after_gauge: 0.
            get_point: 0.
            count: 0.
            expire_date: null.
            is_over: false.
        awake_gauge_total: Total awakening gauge value gained after
                           playing this song.
        is_ticket: Whether live tickets were used to play this song.
        result_macaroon: Empty info. See implementation below.
        result_event_tour: Empty info. See implementation below.
        result_event_point: Empty info. See implementation below.
        result_daily_event_point: Empty info. See implementation below.
        release_mst_event_story_id: 0.
        mst_event_id: 0.
        event_type: 0.
        event_point_reward_list: null.
        daily_event_point_reward_list: null.
        is_event_tour: false.
        is_event_twin_stage: false.
        played_event_type: 0.
        card_list: A list of 5 or 6 dicts representing the final states
                   of the cards after playing this song. The first 5
                   dicts correspond to the selected cards in the first 5
                   positions of the selected unit. If the user has
                   previously obtained the 2nd anniversary card of the
                   idol in the first position (center) of the unit, it
                   will be appended to the end of this list. See the
                   return value 'card_list' of the method
                   'CardService.GetCardList' for the dict definition.
        updated_idol_list: A list of 10 dicts representing the final
                           states of the idols after playing this
                           song. The first 5 dicts contain empty idol
                           info. The last 5 dicts correspond to the
                           idols in the first 5 positions of the
                           selected unit. If multiple cards for the same
                           idol were selected in the unit, there will be
                           mulitple duplicated dicts for that idol in
                           this list. See the return value 'idol_list'
                           of the method 'IdolService.GetIdolList' for
                           the dict definition.
        updated_item_list: A list of dicts representing the final states
                           of user's items after playing this song. See
                           'item_list' of the method
                           'ItemService.GetItemList' for the dict
                           definition.
        lp_list: User LP list after playing this song. See the return
                 value 'lp_list' of the method 'AuthService.Login' for
                 the list definition.
        type_lp_list: User LP list by idol type after playing this song.
                      See the return value 'type_lp_list' of the method
                      'AuthService.Login' for the list definition.
        gasha_medal: User gasha medal info after playing this song. See
                     the return value 'gasha_medal' of the method
                     'GashaMedalService.GetGashaMedal' for the dict
                     definition.
        use_song_unit: Whether song unit was used.
        notes_match: true.
        token_verified: true.
        before_perfect_rate: Perfect rate for this course before playing
                             this song. Perfect rate is the percentage
                             of PERFECT notes to the total number of
                             notes.
        after_perfect_rate: Perfect rate for this course after playing
                            this song.
        perfect_rate: Perfect rate for this live performance. Calculated
                      using 'count_list' in 'params'.
        new_perfect_rate: Whether this is a new perfect rate. This is
                          true only if auto live pass was not used and
                          'perfect_rate' is higher than
                          'before_perfect_rate'.
        result_idol_event_point: Empty info. See implementation below.
        is_live_support: Whether auto live pass was used.
        use_full_random: Whether this is Full Random.
        use_song_random: Whether this is Song Random.
        release_mst_event_talk_story_id: 0.
        result_event_period_shop_point: Empty info. See implementation
                                        below.
        release_mst_event_talk_story_id_list: null.
        event_additional_status: Empty info. See implementation below.
        is_event_boosted: false.
        is_between_interval: false.
        event_tension_progress: Empty info. See implementation below.
        result_event_song_point: Empty info. See implementation below.
        result_event_encounter_status: Empty info. See implementation
                                       below.
        require_log_id: ''.
    """
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()
        if params['live_token'] != user.pending_song.live_token:
            raise ValueError('Game and server live_tokens do not match')

        course_id = user.pending_song.course
        is_ticket = user.pending_song.live_ticket > 0
        gained_exp = (0 if is_ticket
                      else [0, 150, 150, 260, 204, 260, 306][course_id])
        if user.level < 50:
            gained_exp *= 2
        gained_money = (0 if is_ticket
                        else [0, 630, 630, 1200, 900, 1200, 1350][course_id])
        gained_fan = [0, 60, 60, 100, 78, 97, 120][course_id]
        gained_affection = [0, 12, 12, 24, 18, 24, 30][course_id]
        gained_awakening_pt = [0, 15, 15, 28, 22, 28, 34][course_id]
        if is_ticket:
            gained_fan //= 2
            gained_affection //= 2
        if user.pending_song.use_song_random:
            if is_ticket:
                gained_fan = [0, 36, 36, 60, 48, 60, 72][course_id]
                gained_affection = [0, 7, 6, 14, 7, 12, 18][course_id]
            else:
                gained_fan = [0, 72, 72, 120, 96, 120, 144][course_id]
                gained_affection = [0, 14, 12, 28, 19, 25, 36][course_id]
            gained_awakening_pt = [0, 18, 18, 33, 26, 33, 40][course_id]
        if user.pending_song.use_full_random:
            if is_ticket:
                gained_fan = [0, 45, 43, 75, 60, 73, 90][course_id]
                gained_affection = [0, 9, 7, 18, 12, 18, 19][course_id]
            else:
                gained_fan = [0, 90, 90, 150, 120, 150, 180][course_id]
                gained_affection = [0, 18, 18, 36, 25, 36, 43][course_id]
            gained_awakening_pt = [0, 22, 22, 42, 33, 42, 51][course_id]

        #region Update user info.

        user_lv_base = session.scalar(
            select(MstGameSetting.user_lv_base)
        )
        new_level = user.level
        new_exp = user.exp + gained_exp
        new_next_exp = user.next_exp
        while new_exp >= new_next_exp:
            new_level += 1
            new_exp -= new_next_exp
            new_next_exp += user_lv_base
        new_rank = user.producer_rank
        rank_up_requirement = [0, 1_000, 10_000, 50_000, 100_000, 300_000,
                               500_000, 1_000_000]
        if (new_rank < 8
                and user.theater_fan + gained_fan
                >= rank_up_requirement[new_rank]):
            new_rank += 1
        rank_reward = session.scalar(
            select(MstRewardItem)
            .where(MstRewardItem.mst_item_id
                   == 0 if new_rank == user.producer_rank else 3)
            .where(MstRewardItem.amount
                   == (0 if new_rank == user.producer_rank
                       else 50 if new_rank <= 6
                       else 100 if new_rank == 7
                       else 150))
        )
        new_vitality = user.vitality
        new_max_vitality = user.max_vitality
        if new_level > user.level:
            for level in range(user.level+1, new_level+1):
                if (level <= 60 and level % 2 == 0
                    or 60 < level and level <= 150 and level % 3 == 0
                    or 150 < level and level <= 426 and level % 4 == 0
                    or 426 < level and level <= 586 and level % 5 == 1
                    or 586 < level and level <= 700 and level % 6 == 4):
                    new_max_vitality += 1
                new_vitality += new_max_vitality
        new_max_friend = user.max_friend
        if new_level > user.level:
            for level in range(user.level+1, new_level+1):
                if level <= 151 and level % 3 == 1:
                    new_max_friend += 1
        new_theater_fan = user.theater_fan + gained_fan
        user_schema = UserSchema()
        user_dict = user_schema.dump(user)
        song_idol_type = user.pending_song.song.mst_song.idol_type
        new_song_lp = user.pending_song.song.lp
        new_lp = user.lp
        is_live_support = user.pending_song.is_live_support
        if not is_live_support:
            if params['score'] // 10_000 > new_song_lp:
                new_song_lp = params['score'] // 10_000
                for type_lp in user_dict['type_lp_list']:
                    if type_lp['idol_type'] == song_idol_type:
                        if (not type_lp['lp_song_status_list']
                                or len(type_lp['lp_song_status_list']) < 10):
                            new_lp += new_song_lp
                        else:
                            min_lp = type_lp['lp_song_status_list'][-1]['lp']
                            if new_song_lp > min_lp:
                                new_lp += new_song_lp - min_lp
        new_money = min(user.money + gained_money, user.max_money)
        if new_theater_fan >= 1_000_000:
            new_map_level = 20
            new_recognition = 100
        else:
            # TODO: Verify map level when 95 <= recognition <= 99.999 on
            # JP server.
            new_map_level = new_theater_fan//50_000 + 1
            new_recognition = (
                Decimal(new_theater_fan) / Decimal(10_000)
            ).quantize(Decimal('.001'), rounding=ROUND_DOWN)
        release_all_live_course = user.level < 50 and new_level >= 50

        reward_item_schema = MstRewardItemSchema()
        result_user = {
            'level_up': new_level > user.level,
            'before_level': user.level,
            'after_level': new_level,
            'rank_up': new_rank > user.producer_rank,
            'before_rank': user.producer_rank,
            'after_rank': new_rank,
            'rank_reward': reward_item_schema.dump(rank_reward),
            'before_vitality': user.vitality,
            'after_vitality': new_vitality,
            'before_max_vitality': user.max_vitality,
            'after_max_vitality': new_max_vitality,
            'before_live_ticket': user.live_ticket,
            'after_live_ticket': user.live_ticket,
            'before_max_friend': user.max_friend,
            'after_max_friend': new_max_friend,
            'before_theater_fan': user.theater_fan,
            'after_theater_fan': new_theater_fan,
            'before_live_point': user.lp,
            'after_live_point': new_lp,
            'before_song_live_point': user.pending_song.song.lp,
            'after_song_live_point': new_song_lp,
            'before_money': user.money,
            'after_money': new_money,
            'before_exp': (user.level-1)*(user.level-1)*50 + user.exp,
            'after_exp': (new_level-1)*(new_level-1)*50 + new_exp,
            'before_exp_gauge': user.exp*100//user.next_exp,
            'after_exp_gauge': ((new_level-user.level)*100
                                + new_exp*100//new_next_exp),
            'exp': new_exp,
            'next_exp': new_next_exp,
            'full_recover_date': (now if new_vitality >= new_max_vitality
                                  else user.full_recover_date),
            'map_level': {
                'user_map_level': user.map_level.user_map_level,
                'user_recognition': new_recognition,
                'actual_map_level': new_map_level,
                'actual_recognition': new_recognition
            },
            'release_all_live_course': release_all_live_course,
            'before_training_point': 0,
            'after_training_point': 0,
            'total_training_point': 0
        }

        user.level = new_level
        user.producer_rank = new_rank
        # TODO: receive rank reward
        user.vitality = new_vitality
        user.max_vitality = new_max_vitality
        user.max_friend = new_max_friend
        user.theater_fan = new_theater_fan
        if not is_live_support:
            user.lp = new_lp
            lp = session.scalar(
                select(LP)
                .where(LP.user == user)
                .where(LP.mst_song_id == user.pending_song.mst_song_id)
            )
            if not lp:
                session.add(LP(
                    user_id=user.user_id,
                    mst_song_id=user.pending_song.mst_song_id,
                    course=user.pending_song.course,
                    lp=new_song_lp
                ))
                session.expire(user, ['lps'])
            elif new_song_lp > lp.lp:
                lp.course = user.pending_song.course
                lp.lp = new_song_lp
        user.money = new_money
        user.exp = new_exp
        user.next_exp = new_next_exp
        if new_vitality >= new_max_vitality:
            user.full_recover_date = now
        user.map_level.user_recognition = new_recognition
        user.map_level.actual_map_level = new_map_level
        user.map_level.actual_recognition = new_recognition

        #endregion

        #region Update song and course info and give score/combo/clear
        #       rank rewards to the user.

        song = user.pending_song.song
        course = song.courses[course_id-1]
        mode = user.pending_song.mode
        level = course.mst_course.level
        notes = course.mst_course.notes
        score_threshold_list = session.scalar(
            select(MstScoreThreshold.score_threshold_list)
            .where(MstScoreThreshold.level == level)
        )
        score_thresholds = [int(x) for x in score_threshold_list.split(',')][
            2:]
        combo_thresholds = [notes//4, notes*2//4, notes*3//4, notes]
        clear_thresholds = {
            1: [1, 3, 7, 10],
            2: [1, 3, 7, 10],
            3: [1, 15, 30, 50],
            4: [1, 5, 15, 20],
            5: [1, 15, 30, 50],
            6: [1, 30, 70, 100]
        }[course_id]
        score_reward_items = session.scalars(
            select(MstRewardItem)
            .join(MstCourseReward,
                  MstRewardItem.mst_reward_item_id
                  == MstCourseReward.score_reward_item_id)
            .where(MstCourseReward.course == course_id)
            .order_by(MstCourseReward.rank)
        ).all()
        combo_reward_items = session.scalars(
            select(MstRewardItem)
            .join(MstCourseReward,
                  MstRewardItem.mst_reward_item_id
                  == MstCourseReward.combo_reward_item_id)
            .where(MstCourseReward.course == course_id)
            .order_by(MstCourseReward.rank)
        ).all()
        clear_reward_items = session.scalars(
            select(MstRewardItem)
            .join(MstCourseReward,
                  MstRewardItem.mst_reward_item_id
                  == MstCourseReward.clear_reward_item_id)
            .where(MstCourseReward.course == course_id)
            .order_by(MstCourseReward.rank)
        ).all()
        live_result_reward = {
            'before_score_rank': course.score_rank,
            'after_score_rank': course.score_rank,
            'before_combo_rank': course.combo_rank,
            'after_combo_rank': course.combo_rank,
            'before_clear_rank': course.clear_rank,
            'after_clear_rank': course.clear_rank,
            'score_reward_item_list': None,
            'combo_reward_item_list': None,
            'clear_reward_item_list': None,
            'course_reward': {
                'score_reward_item_list': [
                    {
                        'rank': i+1,
                        'reward': reward_item_schema.dump(
                            score_reward_items[i]),
                        'threshold': score_thresholds[i],
                        'status': (1 if course.score_rank >= i+1 else 0)
                    } for i in range(4)
                ],
                'combo_reward_item_list': [
                    {
                        'rank': i+1,
                        'reward': reward_item_schema.dump(
                            combo_reward_items[i]),
                        'threshold': combo_thresholds[i],
                        'status': (1 if course.combo_rank >= i+1 else 0)
                    } for i in range(4)
                ],
                'clear_reward_item_list': [
                    {
                        'rank': i+1,
                        'reward': reward_item_schema.dump(
                            clear_reward_items[i]),
                        'threshold': clear_thresholds[i],
                        'status': (1 if course.clear_rank >= i+1 else 0)
                    } for i in range(4)
                ]
            }
        }
        before_perfect_rate = course.perfect_rate
        after_perfect_rate = course.perfect_rate
        perfect_rate = params['count_list'][0] / notes * 100
        new_perfect_rate = False
        is_new_record = False
        if mode == 1 and not song.is_released_vertical_mv:
            song.is_released_vertical_mv = True
        if mode == 2 and not song.is_released_horizontal_mv:
            song.is_released_horizontal_mv = True
        if not song.is_cleared:
            song.is_cleared = True
            song.first_cleared_date = now
        if not is_live_support:
            if new_song_lp > song.lp:
                song.lp = new_song_lp
            if params['score'] > course.score:
                course.score = params['score']
                course.score_update_date = now
                is_new_record = True
            if params['score_rank']-1 > course.score_rank:
                course.score_rank = params['score_rank']-1
                live_result_reward['after_score_rank'] = params['score_rank']-1
                score_reward_item_list = live_result_reward['course_reward'][
                    'score_reward_item_list']
                for i in range(live_result_reward['before_score_rank'],
                               live_result_reward['after_score_rank']):
                    score_reward_item_list[i]['status'] = 2
                    # TODO: receive score rank reward
            if params['combo'] > course.combo:
                course.combo = params['combo']
            combo_rank = 0
            while (combo_rank < 4
                   and course.combo >= combo_thresholds[combo_rank]):
                combo_rank += 1
            if combo_rank > course.combo_rank:
                course.combo_rank = combo_rank
                live_result_reward['after_combo_rank'] = combo_rank
                combo_reward_item_list = live_result_reward['course_reward'][
                    'combo_reward_item_list']
                for i in range(live_result_reward['before_combo_rank'],
                               live_result_reward['after_combo_rank']):
                    combo_reward_item_list[i]['status'] = 2
                    # TODO: receive combo rank reward
            if perfect_rate > course.perfect_rate:
                course.perfect_rate = perfect_rate
                after_perfect_rate = perfect_rate
                new_perfect_rate = True
        course.clear += 1
        clear_rank = 0
        while clear_rank < 4 and course.clear >= clear_thresholds[clear_rank]:
            clear_rank += 1
        if clear_rank > course.clear_rank:
            course.clear_rank = clear_rank
            live_result_reward['after_clear_rank'] = clear_rank
            clear_reward_item_list = live_result_reward['course_reward'][
                'clear_reward_item_list']
            for i in range(live_result_reward['before_clear_rank'],
                            live_result_reward['after_clear_rank']):
                clear_reward_item_list[i]['status'] = 2
                # TODO: receive clear rank reward
        if course_id in [1, 2, 4, 5] and not song.courses[2].is_released:
            song.courses[2].is_released = True
        if course_id == 5 and not song.courses[5].is_released:
            song.courses[5].is_released = True
        if release_all_live_course:
            session.execute(
                update(Course)
                .where(Course.user == user)
                .values(is_released=True)
            )
        song_schema = SongSchema()
        song_dict = song_schema.dump(song)

        #endregion

        #region Update card and idol info.

        def _distribute_gain_per_card(total_gain, max_gain_per_card):
            """Calculate the gained fan/affection/awakening pt per card.

            Args:
                total_gain: Total fan/affection/awakening pt to be
                            distributed across the five cards/idols.
                max_gain_per_card: A list of 5 ints representing the
                                   maximum allowed gain per card/idol.
            Returns:
                A list of 5 ints representing the distributed gain per
                card/idol.
            """
            gain_per_card = [0, 0, 0, 0, 0]
            while total_gain > 0 and [x for x in max_gain_per_card if x > 0]:
                if total_gain >= 2 and max_gain_per_card[0] >= 2:
                    gain_per_card[0] += 2
                    total_gain -= 2
                    max_gain_per_card[0] -= 2
                elif total_gain >= 1 and max_gain_per_card[0] >= 1:
                    gain_per_card[0] += 1
                    total_gain -= 1
                    max_gain_per_card[0] -= 1
                for i in range(1, 5):
                    if total_gain >= 1 and max_gain_per_card[i] >= 1:
                        gain_per_card[i] += 1
                        total_gain -= 1
                        max_gain_per_card[i] -= 1
            return gain_per_card

        unit_dict = {
            'unit_num': 0,
            'name': _('Unit{unit_num}').format(unit_num=0),
            'idol_list': []
        }
        use_song_unit = user.pending_song.use_song_unit
        if use_song_unit:
            song_unit = session.scalars(
                select(SongUnit)
                .where(SongUnit.user == user)
                .where(SongUnit.mst_song_id == song.mst_song_id)
            ).one()
            song_unit_schema = SongUnitSchema()
            song_unit_dict = song_unit_schema.dump(song_unit)
            unit_dict['idol_list'] = song_unit_dict['idol_list'][:5]
            cards = [x.card for x in song_unit.song_unit_idols][:5]
        elif user.pending_song.use_full_random:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 1)
            ).one()
            random_live_schema = RandomLiveSchema()
            random_live_dict = random_live_schema.dump(random_live)
            unit_dict['idol_list'] = random_live_dict['idol_list']
            cards = [x.card for x in random_live.random_live_idols]
        else:
            unit = session.scalars(
                select(Unit)
                .where(Unit.user == user)
                .where(Unit.unit_num == user.pending_song.unit_num)
            ).one()
            unit_schema = UnitSchema()
            unit_dict = unit_schema.dump(unit)
            cards = [x.card for x in unit.unit_idols]
        idols = [x.idol for x in cards]

        gained_fan_per_idol = [0, 0, 0, 0, 0]
        gained_affection_per_idol = [0, 0, 0, 0, 0]
        gained_awakening_pt_per_card = [0, 0, 0, 0, 0]
        if mode == 1:
            gained_fan_per_idol[0] = gained_fan
            gained_affection_per_idol[0] = gained_affection
            gained_awakening_pt_per_card[0] = min(
                gained_awakening_pt,
                cards[0].mst_card.awakening_gauge_max
                - cards[0].awakening_gauge)
        else:
            gained_fan_per_idol = _distribute_gain_per_card(
                gained_fan, [gained_fan] * 5)
            gained_affection_per_idol = _distribute_gain_per_card(
                gained_affection, [gained_affection] * 5)
            gained_awakening_pt_per_card = _distribute_gain_per_card(
                gained_awakening_pt,
                [card.mst_card.awakening_gauge_max - card.awakening_gauge
                 for card in cards])

        result_idol_list = []
        memorial_schema = MemorialSchema()
        for i in range(5):
            before_fan = idols[i].fan
            before_affection = idols[i].affection
            for j in range(i):
                if result_idol_list[j]['mst_idol_id'] == idols[i].mst_idol_id:
                    before_fan = result_idol_list[j]['after_fan']
                    before_affection = result_idol_list[j]['after_affection']
            after_affection = before_affection + gained_affection_per_idol[i]
            result_idol_list.append({
                'mst_idol_id': idols[i].mst_idol_id,
                'before_awake_gauge': cards[i].awakening_gauge,
                'after_awake_gauge': (cards[i].awakening_gauge
                                      + gained_awakening_pt_per_card[i]),
                'max_awake_gauge': cards[i].mst_card.awakening_gauge_max,
                'before_fan': before_fan,
                'after_fan': before_fan + gained_fan_per_idol[i],
                'before_affection': before_affection,
                'after_affection': after_affection,
                'memorial_status': {
                    'mst_memorial_id': 0,
                    'scenario_id': '',
                    'mst_idol_id': 0,
                    'release_affection': 0,
                    'number': 0,
                    'is_released': False,
                    'is_read': False,
                    'released_date': None,
                    'reward_item_list': None,
                    'is_available': False,
                    'begin_date': None
                },
                'memorial_list': None
            })
            memorial_id = session.scalar(
                select(MstMemorial.mst_memorial_id)
                .where(MstMemorial.mst_idol_id == idols[i].mst_idol_id)
                .where(before_affection < MstMemorial.release_affection)
                .where(MstMemorial.release_affection <= after_affection)
            )
            if memorial_id:
                memorial = session.scalars(
                    select(Memorial)
                    .where(Memorial.user == user)
                    .where(Memorial.mst_memorial_id == memorial_id)
                ).one()
                memorial_dict = memorial_schema.dump(memorial)
                result_idol_list[i]['memorial_status'] = memorial_dict
                result_idol_list[i]['memorial_list'] = [memorial_dict]

            cards[i].awakening_gauge = result_idol_list[i]['after_awake_gauge']
            idols[i].fan = result_idol_list[i]['after_fan']
            idols[i].affection = result_idol_list[i]['after_affection']
            if memorial_id:
                memorial.is_released = True

        card_schema = CardSchema()
        card_list = card_schema.dump(cards, many=True)
        center_2nd_anniversary_card = session.scalar(
            select(Card)
            .join(MstCard)
            .where(Card.user == user)
            .where(MstCard.mst_idol_id == idols[0].mst_idol_id)
            .where(MstCard.ex_type == 7)
        )
        if center_2nd_anniversary_card:
            card_list.append(card_schema.dump(center_2nd_anniversary_card))
        idol_schema = IdolSchema()
        updated_idol_list = [{
            'idol_id': '',
            'mst_idol_id': 0,
            'resource_id': '',
            'idol_type': 0,
            'fan': 0,
            'affection': 0,
            'tension': 0,
            'is_best_condition': False,
            'area': 0,
            'offer_type': 0,
            'mst_costume_id': 0,
            'having_costume_list': None,
            'costume_list': None,
            'favorite_costume_list': None,
            'voice_category_list': None,
            'has_another_appeal': False,
            'can_perform': False,
            'lesson_wear_list': None,
            'mst_agency_id_list': None,
            'default_costume': {
                'mst_costume_id': 0,
                'mst_idol_id': 0,
                'resource_id': '',
                'mst_costume_group_id': 0,
                'costume_name': '',
                'costume_number': 0,
                'exclude_album': False,
                'exclude_random': False,
                'collabo_number': 0,
                'replace_group_id': 0,
                'sort_id': 0,
                'release_date': None,
                'gorgeous_appeal_type': 0
            },
            'birthday_live': 0
        }] * 5
        updated_idol_list.extend(idol_schema.dump(idols, many=True))

        #endregion

        #region Pick random drop rewards and give them to the user.

        # The drop rates are an approximation based on the following
        # 1309 items dropped across 245 songs.
        # Stage dress           105 ( 73 on non-item days)
        # Mini crown            116 ( 84 on non-item days)
        # Lipstick              187 (107 on non-item days)
        # Perfume               229 (150 on non-item days)
        # Mirror                112 ( 64 on non-item days)
        # Gasha medal 10pt       66
        # Gasha medal 15pt       79
        # Gasha medal 20pt       66
        # Lesson ticket N        74
        # Lesson ticket R        65
        # Throat lozenges         4
        # Tapioca drink           9
        # High cocoa chocolate    9
        # Roll cake               6
        # Fan letter              9
        # Single flower          10
        # Hand cream             10
        # Bath additive           5
        # Auto live pass         10
        # N cards               113
        # R cards                17
        # Costumes                8
        class DropType(Enum):
            AWAKENING_ITEM = 55.0
            GASHA_MEDAL_PT = 15.5
            LESSON_TICKET = 10.0
            CARD = 9.5
            AUTO_LIVE_PASS = 5.0
            GIFT = 4.5
            COSTUME = 0.5

        class AwakeningDropType(Enum):
            STAGE_DRESS = (4, 100, 15.7)
            MINI_CROWN = (4, 101, 17.7)
            PRINCESS_LIPSTICK = (1, 110, 7.4)
            PRINCESS_PERFUME = (1, 111, 10.4)
            PRINCESS_MIRROR = (1, 112, 4.4)
            FAIRY_LIPSTICK = (2, 120, 7.4)
            FAIRY_PERFUME = (2, 121, 10.4)
            FAIRY_MIRROR = (2, 122, 4.4)
            ANGEL_LIPSTICK = (3, 130, 7.4)
            ANGEL_PERFUME = (3, 131, 10.4)
            ANGEL_MIRROR = (3, 132, 4.4)
            def __init__(self, idol_type, mst_item_id, weight):
                self.idol_type = idol_type
                self.mst_item_id = mst_item_id
                self.weight = weight

        gained_gasha_medal_pt = 0
        gasha_medal_point_amount = user.gasha_medal.point_amount
        drop_reward_box_list = None
        updated_item_ids = []
        if not user.pending_song.live_ticket:
            drop_reward_box_list = []
            is_item_day = song_idol_type == get_item_day_idol_type()
            n_card_id_stmt = (
                select(MstCard.mst_card_id)
                .where(MstCard.rarity == 1)
            )
            r_card_id_stmt = (
                select(MstCard.mst_card_id)
                .where(MstCard.rarity == 2)
            )
            if is_item_day and song_idol_type != 4:
                n_card_id_stmt = n_card_id_stmt.where(
                    MstCard.idol_type == song_idol_type)
                r_card_id_stmt = r_card_id_stmt.where(
                    MstCard.idol_type == song_idol_type)
            n_card_ids = session.scalars(n_card_id_stmt).all()
            r_card_ids = session.scalars(r_card_id_stmt).all()
            unlocked_costume_subq = (
                select(Costume.mst_costume_id)
                .where(Costume.user == user)
                .where(Costume.mst_costume_id == MstCostume.mst_costume_id)
            ).exists()
            locked_costume_ids = session.scalars(
                select(MstCostume.mst_costume_id)
                .where(MstCostume.costume_name == 'ex')
                .where(MstCostume.costume_number.in_([2, 3, 5, 6]))
                .where(~unlocked_costume_subq)
            ).all()
            auto_live_pass_remaining = session.scalar(
                select(MstItem.max_amount - Item.amount)
                .select_from(Item)
                .join(MstItem)
                .where(Item.user == user)
                .where(Item.mst_item_id == 50)
                .where(Item.amount < MstItem.max_amount)
            )
            allowed_drops = [
                DropType.AWAKENING_ITEM,
                DropType.GASHA_MEDAL_PT,
                DropType.LESSON_TICKET,
                DropType.CARD,
                DropType.GIFT
            ]
            if auto_live_pass_remaining:
                allowed_drops.append(DropType.AUTO_LIVE_PASS)
            if locked_costume_ids:
                allowed_drops.append(DropType.COSTUME)
            drop_count = [
                2, 2, 4, 3, 4, random.randint(4, 5)][course_id-1]
            if params['score_rank'] == 5:
                drop_count = [
                    random.randint(2, 3),
                    random.randint(2, 3),
                    random.randint(4, 5),
                    random.randint(3, 4),
                    random.randint(4, 5),
                    random.randint(5, 6)
                ][course_id-1]

            selected_drops = random.choices(
                allowed_drops, [x.value for x in allowed_drops], k=drop_count)
            for drop_type in selected_drops:
                if (drop_type is DropType.AUTO_LIVE_PASS
                        and not auto_live_pass_remaining):
                    if DropType.AUTO_LIVE_PASS in allowed_drops:
                        allowed_drops.remove(DropType.AUTO_LIVE_PASS)
                    drop_type = random.choices(
                        allowed_drops, [x.value for x in allowed_drops], k=1
                    )[0]
                if drop_type is DropType.COSTUME and not locked_costume_ids:
                    if DropType.COSTUME in allowed_drops:
                        allowed_drops.remove(DropType.COSTUME)
                    drop_type = random.choices(
                        allowed_drops, [x.value for x in allowed_drops], k=1
                    )[0]

                if drop_type is DropType.AWAKENING_ITEM:
                    allowed_awakening_drops = [
                        AwakeningDropType.STAGE_DRESS,
                        AwakeningDropType.MINI_CROWN,
                        AwakeningDropType.PRINCESS_LIPSTICK,
                        AwakeningDropType.PRINCESS_PERFUME,
                        AwakeningDropType.PRINCESS_MIRROR,
                        AwakeningDropType.FAIRY_LIPSTICK,
                        AwakeningDropType.FAIRY_PERFUME,
                        AwakeningDropType.FAIRY_MIRROR,
                        AwakeningDropType.ANGEL_LIPSTICK,
                        AwakeningDropType.ANGEL_PERFUME,
                        AwakeningDropType.ANGEL_MIRROR
                    ]
                    if is_item_day:
                        allowed_awakening_drops = [
                            x for x in allowed_awakening_drops
                            if x.idol_type == song_idol_type]
                    selected_awakening_drop = random.choices(
                        allowed_awakening_drops,
                        [x.weight for x in allowed_awakening_drops], k=1)[0]
                    drop_reward_item = MstRewardItem(
                        reward_type=4,
                        mst_item_id=selected_awakening_drop.mst_item_id,
                        item_type=7,
                        amount=1
                    )
                elif drop_type is DropType.GASHA_MEDAL_PT:
                    selected_item_id = random.choice([502, 503, 504])
                    gained_gasha_medal_pt += (
                        10 if selected_item_id == 502
                        else 15 if selected_item_id == 503
                        else 20)
                    drop_reward_item = MstRewardItem(
                        reward_type=4,
                        mst_item_id=selected_item_id,
                        item_type=4,
                        amount=1
                    )
                elif drop_type is DropType.LESSON_TICKET:
                    selected_item_id = random.choice([200, 201])
                    drop_reward_item = MstRewardItem(
                        reward_type=4,
                        mst_item_id=selected_item_id,
                        item_type=8,
                        amount=1
                    )
                elif drop_type is DropType.GIFT:
                    selected_item_id = random.choices(
                        [70, 71, 72, 73, 80, 81, 82, 83],
                        [1, 2, 2, 1, 2, 2, 2, 1], k=1)[0]
                    drop_reward_item = MstRewardItem(
                        reward_type=4,
                        mst_item_id=selected_item_id,
                        item_type=25 if selected_item_id < 80 else 26,
                        amount=1
                    )
                elif drop_type is DropType.AUTO_LIVE_PASS:
                    auto_live_pass_remaining -= 1
                    drop_reward_item = MstRewardItem(
                        reward_type=4,
                        mst_item_id=50,
                        item_type=23,
                        amount=1
                    )
                elif drop_type is DropType.CARD:
                    selected_card_type = random.choices(
                        ['N', 'R'], [9, 1], k=1)[0]
                    if selected_card_type == 'N':
                        selected_card_id = random.choice(n_card_ids)
                    else:
                        selected_card_id = random.choice(r_card_ids)
                    drop_reward_item = MstRewardItem(
                        reward_type=6,
                        mst_card_id=selected_card_id,
                        amount=1
                    )
                elif drop_type is DropType.COSTUME:
                    selected_costume_id = random.choice(locked_costume_ids)
                    locked_costume_ids.remove(selected_costume_id)
                    drop_reward_item = MstRewardItem(
                        reward_type=8,
                        mst_costume_id=selected_costume_id,
                        amount=1
                    )

                drop_reward_box_list.append({
                    'drop_reward_item': reward_item_schema.dump(
                        drop_reward_item),
                    'substitute_list': None,
                    'drop_reward_group_type': 1
                })
                if drop_reward_item.mst_item_id:
                    add_item(
                        session=session,
                        user_id=user.user_id,
                        mst_item_id=drop_reward_item.mst_item_id,
                        item_type=drop_reward_item.item_type)
                    if drop_type is not DropType.GASHA_MEDAL_PT:
                        updated_item_ids.append(drop_reward_item.mst_item_id)
                elif drop_reward_item.mst_card_id:
                    rarity = session.scalar(
                        select(MstCard.rarity)
                        .select_from(Card)
                        .join(MstCard)
                        .where(Card.user == user)
                        .where(Card.mst_card_id
                               == drop_reward_item.mst_card_id)
                    )
                    if rarity:
                        lesson_ticket_item_id = 200 if rarity == 1 else 201
                        add_item(
                            session=session,
                            user_id=user.user_id,
                            mst_item_id=lesson_ticket_item_id,
                            item_type=8,
                            amount=2
                        )
                        updated_item_ids.append(lesson_ticket_item_id)
                        master_piece_item_id = 300 if rarity == 1 else 301
                        add_item(
                            session=session,
                            user_id=user.user_id,
                            mst_item_id=master_piece_item_id,
                            item_type=9,
                            amount=1
                        )
                        updated_item_ids.append(master_piece_item_id)
                    else:
                        add_card(
                            session=session,
                            user=user,
                            mst_card_id=drop_reward_item.mst_card_id
                        )
                elif drop_reward_item.mst_costume_id:
                    mst_costume_id = drop_reward_item.mst_costume_id
                    user.costumes.append(Costume(
                        costume_id=(f'{user.user_id}_{mst_costume_id}'),
                        mst_costume_id=mst_costume_id
                    ))

        result_gasha_medal = {
            'before_gauge': 0,
            'after_gauge': 0,
            'get_point': 0,
            'count': 0,
            'expire_date': None,
            'is_over': False
        }
        if gained_gasha_medal_pt:
            # TODO: What are the correct values when is_over is true?
            result_gasha_medal['before_gauge'] = gasha_medal_point_amount
            result_gasha_medal['after_gauge'] = gained_gasha_medal_pt
            result_gasha_medal['get_point'] = gained_gasha_medal_pt
            new_gasha_medal_point_amount = (gasha_medal_point_amount
                                            + gained_gasha_medal_pt)
            if new_gasha_medal_point_amount >= 100:
                while new_gasha_medal_point_amount >= 100:
                    result_gasha_medal['count'] += 1
                    new_gasha_medal_point_amount -= 100
                result_gasha_medal['expire_date'] = now + timedelta(days=7)
            else:
                result_gasha_medal['expire_date'] = datetime(1, 1, 1)
            result_gasha_medal['is_over'] = len(
                user.gasha_medal.gasha_medal_expire_dates) >= 10
        live_result_drop_reward = {
            'drop_reward_box_list': drop_reward_box_list
        }
        updated_items = session.scalars(
            select(Item)
            .where(Item.user == user)
            .where(Item.mst_item_id.in_(updated_item_ids))
        ).all()
        updated_item_list = []
        if updated_items:
            item_schema = ItemSchema()
            updated_item_list = item_schema.dump(updated_items, many=True)
        gasha_medal_schema = GashaMedalSchema()
        gasha_medal = gasha_medal_schema.dump(user.gasha_medal)

        #endregion

        #region Unlock main story episode (if any).

        release_mst_main_story_id = 0
        mst_room_id = 0
        min_locked_main_story_id = session.scalar(
            select(func.min(MainStoryChapter.mst_main_story_id))
            .where(MainStoryChapter.user == user)
            .where(MainStoryChapter.is_released == False)
        )
        if min_locked_main_story_id:
            release_song_id, release_level, room_id = session.execute(
                select(MstMainStory.release_song_id,
                       MstMainStory.release_level,
                       MstTheaterRoomStatus.mst_room_id)
                .join(MstMainStoryContactStatus)
                .join(MstTheaterRoomStatus)
                .where(MstMainStory.mst_main_story_id
                       == min_locked_main_story_id)
            ).one()
            release_song_is_cleared = session.scalar(
                select(Song.is_cleared)
                .where(Song.user == user)
                .where(Song.mst_song_id == release_song_id)
            )
            if new_level >= release_level and release_song_is_cleared:
                release_mst_main_story_id = min_locked_main_story_id
                mst_room_id = room_id
                session.execute(
                    update(MainStoryChapter)
                    .where(MainStoryChapter.user == user)
                    .where(MainStoryChapter.mst_main_story_id
                           == release_mst_main_story_id)
                    .where(MainStoryChapter.chapter == 1)
                    .values(is_released=True)
                )
                #TODO: add theater_room

        #endregion

        #region Update mission info and give mission rewards to the
        #       user.

        mission_list = []
        mission_schema = MissionSchema()

        # Update daily mission progress.
        daily_song_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 72)
            .where(Mission.mission_state == 1)
        )
        if (daily_song_mission
                and user.challenge_song.daily_challenge_mst_song_id
                == song.mst_song_id):
            update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=daily_song_mission,
                progress=1
            )
            mission_list.append(mission_schema.dump(daily_song_mission))

            daily_total_mission = session.scalar(
                select(Mission)
                .where(Mission.user == user)
                .where(Mission.mst_mission_id == 75)
                .where(Mission.mission_state == 1)
            )
            if daily_total_mission:
                is_complete = update_mission_progress(
                    session=session,
                    user_id=user.user_id,
                    mission=daily_total_mission,
                    progress=daily_total_mission.progress + 1
                )
                if is_complete:
                    mission_list.append(
                        mission_schema.dump(daily_total_mission))

        # Update weekly mission progress.
        weekly_fan_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 70)
            .where(Mission.mission_state == 1)
        )
        if weekly_fan_mission:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=weekly_fan_mission,
                progress=weekly_fan_mission.progress + gained_fan
            )
            if is_complete:
                mission_list.append(mission_schema.dump(weekly_fan_mission))

        # Update normal mission progress.
        live_clear_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 1)
            .where(Mission.mission_state.in_([0, 1]))
            # Process missions in the order they are unlocked.
            .order_by(MstMission.sort_id)
        ).all()
        for mission in live_clear_missions:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                # Side note: Total live clear count at any given time
                # can be calculated from the clear count of all courses.
                progress=mission.progress + 1
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        if not is_live_support:
            if combo_rank == 4:
                full_combo_missions = session.scalars(
                    select(Mission)
                    .join(MstMission)
                    .where(Mission.user == user)
                    .where(MstMission.mst_mission_class_id == 2)
                    .where(or_(Mission.mission_state.in_([0, 1]),
                               # Use the first mission to keep track of
                               # total full combo count even when all
                               # missions are completed.
                               Mission.mst_mission_id == 7))
                    .order_by(MstMission.sort_id)
                ).all()
                for mission in full_combo_missions:
                    is_complete = update_mission_progress(
                        session=session,
                        user_id=user.user_id,
                        mission=mission,
                        progress=mission.progress + 1
                    )
                    if is_complete:
                        mission_list.append(mission_schema.dump(mission))

            score_missions = session.scalars(
                select(Mission)
                .join(MstMission)
                .where(Mission.user == user)
                .where(MstMission.mst_mission_class_id == 3)
                .where(Mission.mission_state.in_([0, 1]))
                .order_by(MstMission.sort_id)
            ).all()
            for mission in score_missions:
                is_complete = update_mission_progress(
                    session=session,
                    user_id=user.user_id,
                    mission=mission,
                    progress=params['score']
                )
                if is_complete:
                    mission_list.append(mission_schema.dump(mission))

            song_level_missions = session.scalars(
                select(Mission)
                .join(MstMission)
                .where(Mission.user == user)
                .where(MstMission.mst_mission_class_id == 4)
                .where(Mission.mission_state.in_([0, 1]))
                .order_by(MstMission.sort_id)
            ).all()
            for mission in song_level_missions:
                is_complete = update_mission_progress(
                    session=session,
                    user_id=user.user_id,
                    mission=mission,
                    progress=course.mst_course.level
                )
                if is_complete:
                    mission_list.append(mission_schema.dump(mission))

        card_count = len(user.cards)
        card_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 5)
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in card_missions:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=card_count
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        affection_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 6)
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in affection_missions:
            progress = mission.progress
            for result_idol in result_idol_list:
                if (result_idol['before_affection']
                        < int(mission.mst_mission.option)
                        and int(mission.mst_mission.option)
                        <= result_idol['after_affection']):
                    progress += 1
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=progress
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        if result_user['rank_up']:
            user_level_missions = session.scalars(
                select(Mission)
                .join(MstMission)
                .where(Mission.user == user)
                .where(MstMission.mst_mission_class_id == 7)
                .where(Mission.mission_state.in_([0, 1]))
                .order_by(MstMission.sort_id)
            ).all()
            for mission in user_level_missions:
                is_complete = update_mission_progress(
                    session=session,
                    user_id=user.user_id,
                    mission=mission,
                    progress=user.level
                )
                if is_complete:
                    mission_list.append(mission_schema.dump(mission))

        cleared_song_count = session.scalar(
            select(func.count(Song.mst_song_id))
            .where(Song.user == user)
            .where(Song.is_cleared == True)
        )
        song_clear_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 8)
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in song_clear_missions:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=cleared_song_count
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        costume_count = len(user.costumes)
        costume_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 9)
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in costume_missions:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=costume_count
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        user_lp_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 37)
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in user_lp_missions:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=new_lp
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        costume_set_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 47)
            .where(Mission.mission_state == 1)
        ).all()
        for mission in costume_set_missions:
            costume_count = len([
                costume for costume in user.costumes
                if costume.mst_costume.mst_costume_group_id
                == int(mission.mst_mission.option)
            ])
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=costume_count
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        shika_unit_center_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 120)
            .where(Mission.mission_state == 1)
        )
        if (shika_unit_center_mission
                and idols[0].mst_idol_id
                == int(shika_unit_center_mission.mst_mission.option)
                and song.mst_song_id
                == int(shika_unit_center_mission.mst_mission.option2)
                and mode == 2):
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=shika_unit_center_mission,
                progress=shika_unit_center_mission.progress + 1
            )
            if is_complete:
                mission_list.append(
                    mission_schema.dump(shika_unit_center_mission))

        shika_solo_center_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 121)
            .where(Mission.mission_state == 1)
        )
        if (shika_solo_center_mission
                and idols[0].mst_idol_id
                == int(shika_solo_center_mission.mst_mission.option)
                and song.mst_song_id
                == int(shika_solo_center_mission.mst_mission.option2)
                and mode == 1):
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=shika_solo_center_mission,
                progress=shika_solo_center_mission.progress + 1
            )
            if is_complete:
                mission_list.append(
                    mission_schema.dump(shika_solo_center_mission))

        shika_live_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 122)
            .where(Mission.mission_state == 1)
        )
        if (shika_live_mission
                and [idol for idol in idols
                     if idol.mst_idol_id
                     == int(shika_live_mission.mst_mission.option)]
                and song.mst_song_id
                == int(shika_live_mission.mst_mission.option2)):
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=shika_live_mission,
                progress=shika_live_mission.progress + 1
            )
            if is_complete:
                mission_list.append(mission_schema.dump(shika_live_mission))

        shika_center_mission = session.scalar(
            select(Mission)
            .where(Mission.user == user)
            .where(Mission.mst_mission_id == 123)
            .where(Mission.mission_state == 1)
        )
        if (shika_center_mission
                and idols[0].mst_idol_id
                == int(shika_center_mission.mst_mission.option)):
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=shika_center_mission,
                progress=shika_center_mission.progress + 1
            )
            if is_complete:
                mission_list.append(mission_schema.dump(shika_center_mission))

        user_dict = user_schema.dump(user)
        for type_lp in user_dict['type_lp_list']:
            if type_lp['idol_type'] == song_idol_type:
                idol_type_lp = type_lp['lp']
        idol_type_lp_mission = session.scalar(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == song_idol_type+69)
            .where(Mission.mission_state == 1)
        )
        if idol_type_lp_mission:
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=idol_type_lp_mission,
                progress=idol_type_lp
            )
            if is_complete:
                mission_list.append(mission_schema.dump(idol_type_lp_mission))

        # Update idol mission progress.
        idol_missions = session.scalars(
            select(Mission)
            .join(MstMission)
            .where(Mission.user == user)
            .where(MstMission.mst_mission_class_id == 36)
            .where(MstMission.option.in_(
                [f'{idol.mst_idol_id}' for idol in idols]))
            .where(Mission.mission_state.in_([0, 1]))
            .order_by(MstMission.sort_id)
        ).all()
        for mission in idol_missions:
            progress = mission.progress
            for result_idol in result_idol_list:
                if (result_idol['mst_idol_id']
                        == int(mission.mst_mission.option)
                        and result_idol['after_affection'] > progress):
                    progress = result_idol['after_affection']
            is_complete = update_mission_progress(
                session=session,
                user_id=user.user_id,
                mission=mission,
                progress=progress
            )
            if is_complete:
                mission_list.append(mission_schema.dump(mission))

        # TODO: time-limited missions

        #endregion

        if user.pending_song.use_full_random:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 1)
            ).one()
            session.delete(random_live)
        elif user.pending_song.use_song_random:
            random_live = session.scalars(
                select(RandomLive)
                .where(RandomLive.user_id == user.user_id)
                .where(RandomLive.random_live_type == 2)
            ).one()
            session.delete(random_live)

        pending_song_schema = PendingSongSchema()
        pending_song = pending_song_schema.dump(user.pending_song)
        user.pending_song = None

        # TODO: Verify song ranking works

        session.commit()

    return {
        'result_user': result_user,
        'result_idol_list': result_idol_list,
        'result_gasha_medal': result_gasha_medal,
        'live_result_reward': live_result_reward,
        'live_result_drop_reward': live_result_drop_reward,
        'song': song_dict,
        'live_result_rank': max(params['score_rank']-1, 0),
        'live_play_rank': params['score_rank'],
        'combo_rank': combo_rank,
        'count_list': params['count_list'],
        'is_full_combo': combo_rank == 4,
        'is_new_record': is_new_record,
        'guest': pending_song['user_summary'],
        'guest_idol_type': pending_song['guest_idol_type'],
        'release_mst_main_story_id': release_mst_main_story_id,
        'mst_room_id': mst_room_id,
        'unit': unit_dict,
        'mission_process': {
            'complete_mission_list': mission_list,
            'open_mission_list': [],
            'training_point_diff': {
                'before': 0,
                'after': 0,
                'total': 0
            }
        },
        'mission_list': mission_list,
        'over_capacity_info': {
            'money': (result_user['before_money'] + gained_money
                      > user_dict['max_money']),
            'live_ticket': False
        },
        'result_gasha_ticket': {
            'before_gauge': 0,
            'after_gauge': 0,
            'get_point': 0,
            'count': 0,
            'expire_date': None,
            'is_over': False
        },
        'awake_gauge_total': gained_awakening_pt,
        'is_ticket': is_ticket,
        'result_macaroon': {
            'mst_event_id': 0,
            'before_macaroon': 0,
            'after_macaroon': 0
        },
        'result_event_tour': {
            'mst_event_id': 0,
            'before_playable_count': 0,
            'after_playable_count': 0,
            'playable_count_required_step': 0,
            'playable_count_step': 0,
            'before_playable_count_step': 0,
            'after_playable_count_step': 0,
            'required_fixed_step': 0,
            'fixed_step': 0,
            'is_keep_point_scale': False,
            'fixed_step_twin': 0,
            'is_keep_point_scale_twin': False
        },
        'result_event_point': {
            'mst_event_id': 0,
            'before_event_point': 0,
            'after_event_point': 0
        },
        'result_daily_event_point': {
            'mst_event_id': 0,
            'before_event_point': 0,
            'after_event_point': 0
        },
        'result_event_carnival_mission': {
            'mst_event_id': 0,
            'mst_event_schedule_id': 0,
            'before_carnival_mission_value': 0,
            'after_carnival_mission_value': 0,
            'before_comprehensive_carnival_mission_value': 0,
            'after_comprehensive_carnival_mission_value': 0
        },
        'release_mst_event_story_id': 0,
        'mst_event_id': 0,
        'event_type': 0,
        'event_point_reward_list': None,
        'daily_event_point_reward_list': None,
        'is_event_tour': False,
        'is_event_twin_stage': False,
        'played_event_type': 0,
        'card_list': card_list,
        'updated_idol_list': updated_idol_list,
        'updated_item_list': updated_item_list,
        'lp_list': user_dict['lp_list'],
        'type_lp_list': user_dict['type_lp_list'],
        'gasha_medal': gasha_medal,
        'use_song_unit': use_song_unit,
        'notes_match': True,
        'token_verified': True,
        'before_perfect_rate': before_perfect_rate,
        'after_perfect_rate': after_perfect_rate,
        'perfect_rate': perfect_rate,
        'new_perfect_rate': new_perfect_rate,
        'result_idol_event_point': {
            'mst_event_id': 0,
            'mst_idol_id': 0,
            'before_event_point': 0,
            'after_event_point': 0
        },
        'is_live_support': is_live_support,
        'use_full_random': pending_song['use_full_random'],
        'use_song_random': pending_song['use_song_random'],
        'release_mst_event_talk_story_id': 0,
        'result_event_period_shop_point': {
            'mst_event_id': 0,
            'mst_event_period_shop_id': 0,
            'before_point': 0,
            'after_point': 0
        },
        'release_mst_event_talk_story_id_list': None,
        'event_additional_status': {
            'boost_start_date': None,
            'boost_lifetime': 0,
            'interval_start_date': None,
            'interval_lifetime': 0,
            'boost_amount': 0,
            'max_boost_amount': 0
        },
        'is_event_boosted': False,
        'is_between_interval': False,
        'event_tension_progress': {
            'gain_fever_count': 0,
            'before_event_tension': {
                'mst_event_tension_id': 0,
                'mst_event_id': 0,
                'mst_song_id': 0,
                'fever_amount': 0,
                'buff_amount': 0,
                'total_event_tension_lv': 0,
                'vocal_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'dance_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'visual_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'total_event_tension_lv_reward_list': None
            },
            'after_event_tension': {
                'mst_event_tension_id': 0,
                'mst_event_id': 0,
                'mst_song_id': 0,
                'fever_amount': 0,
                'buff_amount': 0,
                'total_event_tension_lv': 0,
                'vocal_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'dance_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'visual_event_tension_lv_exp': {
                    'exp': 0,
                    'lv': 0,
                    'remaining_exp': 0,
                    'next_exp': 0
                },
                'total_event_tension_lv_reward_list': None
            },
            'exp_range_table': None,
            'tension_buff_text': {
                'mst_song_id': 0,
                'mst_song_id_use_fever': 0,
                'mst_song_id_gain_buff': 0,
                'mst_idol_id': 0,
                'text': ''
            }
        },
        'result_event_song_point': {
            'before_point': 0,
            'after_point': 0,
            'event_song_point_reward_list': None,
            'event_reward_card_list': None
        },
        'result_event_encounter_status': {
            'mst_event_encounter_id': 0,
            'mst_idol_id': 0,
            'status': 0,
            'clear_count': 0,
            'total_text_num': 0,
            'message': {
                'mst_event_encounter_message_id': 0,
                'lv': 0
            },
            'sort_id': 0,
            'bonus_rate': 0
        },
        'require_log_id': ''
    }

