import random
from datetime import datetime, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Item, Mission, MstMission, MstSong, Offer,
                                Song, User)
from mltd.models.schemas import UserSchema
from mltd.servers.config import server_timezone


@dispatcher.add_method(name='AuthService.TransferPassword')
def transfer_password(params):
    """Service for transferring an existing account using a password.

    Invoked after doing a clean installation and entering user ID and
    password.
    Args:
        params: A dict containing the following keys.
            user_id: Entered user ID. Corresponds to search_id of the
                     existing user (8 characters).
            password: Entered password. This must match the password
                      previously entered for the transfer to be
                      successful.
            platform: Platform of the mobile device (google/apple).
            platform_user_id: A 16-character hex value. Seems to be
                              device-specific. This value is the same as
                              the header value 'X-Platform-User-Id' for
                              all requests sent from the device.
            device_name: Name of the mobile device the game is running
                         on.
    Returns:
        A dict containing the following keys.
        success: A boolean flag indicating whether the transfer was
                 successful.
        user_id: The user ID in UUID format (if successful).
        secret: The user secret (if successful).
    """
    # Return a static user_id for now.
    return {
        'success': True,
        'user_id': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
        'secret': 'abcdefghijklmnopqrstuvwxyz012345'
    }


@dispatcher.add_method(name='AuthService.Login')
def login(params):
    """Service for user login.

    Invoked right after title screen for an existing user.
    Args:
        params: A dict containing the following keys.
            user_id: Unique user id in UUID format.
            secret: User secret obtained at user registration or
                    account transfer.
            device_name: Name of the mobile device the game is running
                         on.
            os_name: OS of the mobile device (android/ios).
            os_version: OS version of the mobile device.
            ad_id: Empty.
            space: Available space of the mobile device in bytes.
    Returns:
        If the user is successfully authenticated (which is normally the
        case), returns a dict containing the following keys.
        token: A new JWT valid for 24 hours.
        is_pending_song: Whether the user ended the last session while
                         playing a song.
        is_pending_job: Whether the user ended the last session while
                        doing a job.
        is_join_lounge: Whether the user has joined a lounge.
        user: A dict containing the following keys.
            user_id: User id in UUID format. Same value as the one in
                     args.
            search_id: 8 uppercase letters/numbers uniquely identifying
                       each user. Shown on title screen.
            name: Display name chosen by the user.
            money: Amount of money the user owns.
            max_money: Maximum possible amount of money (9999999).
            vitality: Current vitality the user has.
            max_vitality: Maximum possible vitality (based on user
                          level).
            live_ticket: Number of live tickets the user owns.
            max_live_ticket: Maximum possible number of live tickets
                             (500).
            exp: Current user experience.
            next_exp: Required user experience for leveling up.
            level: Current user level.
            max_level: Maximum possible user level (999).
            lp: User LP. Calculated from user's 40 best song LPs, 10
                from each idol type.
            lp_list: A nullable list of at most 10 dicts representing
                     user's highest song LPs (independent of idol type),
                     sorted in descending LP. Each dict contains the
                     following keys.
                mst_song_id: Song ID.
                course: An int (1 to 6) representing the mode (solo
                        2M/2M+, unit 2M/4M/6M/MM) the user played on
                        when they got the LP.
                level: Song difficulty.
                lp: Song LP.
                is_playable: True.
                idol_type: An int (1 to 4) representing the song's idol
                           type (Princess/Fairy/Angel/All).
                resource_id: A string for getting song-related
                             resources.
                sort_id: Sort ID.
            type_lp_list: A list of 4 dicts representing user's all song
                          LPs grouped by each idol type. Each dict
                          contains the following keys.
                idol_type: Song idol type.
                lp_song_status_list: A nullable list of dicts
                                     representing user's all song LPs
                                     specific to this idol type, sorted
                                     in descending LP. See 'lp_list'
                                     above for the dict definition.
                lp: User LP for this idol type. Calculated from user's
                    10 best song LPs for this idol type.
            theater_fan: Current number of fans for the user.
            last_login_date: Last login date. Same as current server
                             time because the user is logging in.
            is_tutorial_finished: Whether the user has completed the
                                  tutorial.
            lounge_id: User's lounge ID in UUID format (empty if the
                       user hasn't joined a lounge).
            lounge_name: Displayed lounge name chosen by the lounge
                         owner (empty if the user hasn't joined a
                         lounge).
            lounge_user_state: An int representing the user state for
                               lounge.
                               0 = Not in any lounge.
                               3 = Joined a lounge as a member.
            producer_rank: Producer rank (1 to 8).
            full_recover_date: If vitality is not full, this represents
                               the time when vitality will be fully
                               recovered. This date is in the past if
                               vitality is full.
            auto_recover_interval: Number of seconds to automatically
                                   recover 1 vitality (300).
            first_time_date: The date when the user first registered.
            produce_gauge: Current produce gauge.
            max_friend: Maximum possible number of friends (based on
                        user level).
            challenge_song: A dict representing the daily challenge song
                            for the user. Contains the following keys.
                daily_challenge_mst_song_id: Song ID.
                update_date: The date when this daily challenge song was
                             chosen by the server. Should always be on
                             the same day as the server because
                             otherwise it would have automatically
                             chosen a new daily challenge song.
            mission_summary: A dict representing the state of beginner's
                             panel missions for the user. Contains the
                             following keys.
                current_mst_panel_mission_sheet_id: Current panel
                                                    mission sheet the
                                                    user is on (1 to 3).
                current_panel_mission_sheet_state: Current state of the
                                                   panel mission sheet.
                                                   1 = In progress.
                                                   3 = Completed.
            is_connected_bnid: Whether the user account is bound with a
                               BANDAI NAMCO ID.
            is_connected_facebook: False.
            user_recognition: User recognition (0.005 to 100). Related
                              to producer rank and map level.
            default_live_quality: 0.
            default_theater_quality: 0.
            default_mv_quality: 0.
            mv_quality_limit: 0.
            tutorial_live_quality: 0.
            asset_tag: Empty string.
            map_level: A dict representing current map level of the
                       user. Related to producer rank. Contains the
                       following keys.
                user_map_level: Current map level (1 to 20).
                user_recognition: Current user recognition (0.005 to
                                  100).
                actual_map_level: Same as user_level.
                actual_recognition: Same as user_recognition.
            user_id_hash: A base64 string encoding the user_id
                          concatenated with 32 bytes of unknown data.
                          The 32 bytes are the same for all users and
                          remain static across all sessions.
            un_lock_song_status: Meaning unknown. A dict containing the
                                 following keys.
                count: 0.
                max_count: 3.
            disabled_massive_live: false.
            disabled_massive_mv: false.
            button_disabled: false.
            training_point: 0.
            total_training_point: 0.
    """
    result = {
        # Skip authentication for local server. Return a static token.
        'token': (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJFeHBpcmVkIjoiMjAyMi0wMS0y'
            + 'M1QxNToyNToxMC44ODk5MTAyODZaIiwiTW9kZSI6ImxvZ2luIiwiVHJhbnNmZXI'
            + 'iOjIsIlVzZXJJRCI6ImQ1Nzc3YzVhLTM1MmUtNGZlNC05NDc4LTI5ZGFmMDFmZD'
            + 'k5NyJ9.wTcuKRK371C0X_eLeAewUj8PFzvepbLzkV3o0_ldFu4'
        ),
    }

    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(params['user_id']))
        ).one()
        result['is_pending_song'] = user.pending_song is not None
        result['is_pending_job'] = user.pending_job is not None
        result['is_join_lounge'] = True if user.lounge_id else False

        now = datetime.now(timezone.utc)
        last_login_date = user.last_login_date.replace(tzinfo=timezone.utc)
        user.last_login_date = now
        # Perform daily reset.
        if (last_login_date.astimezone(server_timezone).date()
                < now.astimezone(server_timezone).date()):
            # Update challenge_song based on user's unplayed and
            # unlocked songs, idols' birthdays and server date.
            unlocked_stmt = (
                select(Song.mst_song_id)
                .where(Song.user == user)
                .where(Song.is_disable == False)
            )
            unlocked_song_ids = session.scalars(unlocked_stmt).all()
            unplayed_stmt = unlocked_stmt.where(Song.is_played == False)
            unplayed_song_ids = session.scalars(unplayed_stmt).all()
            server_month = now.astimezone(server_timezone).month
            server_day = now.astimezone(server_timezone).day
            # TODO: check idols' birthdays
            if (server_month == 2 and server_day == 27
                and 1 in unlocked_song_ids):
                user.challenge_song.daily_challenge_mst_song_id = 1
            else:
                song_ids = unlocked_song_ids
                if unplayed_song_ids:
                    song_ids = random.choice([unplayed_song_ids,
                                              unlocked_song_ids])
                user.challenge_song.daily_challenge_mst_song_id = (
                    random.choice(song_ids))
            user.challenge_song.update_date = now

            # Remove expired items.
            session.execute(
                update(Item)
                .where(Item.user == user)
                .where(Item.mst_item_id.in_([
                    32,     # One-day spark drink 30
                    33      # One-day spark drink MAX
                ]))
                .values(amount=0)
            )

            # Reset daily missions.
            session.execute(
                update(Mission)
                .where(Mission.user == user)
                .where(Mission.mst_mission.has(MstMission.mission_type == 1))
                .values(
                    create_date=now,
                    update_date=now,
                    finish_date=datetime(1, 1, 1),
                    progress=0,
                    mission_state=1
                )
            )
            song_idol_type_subq = (
                select(MstSong.idol_type)
                .where(MstSong.mst_song_id
                       == user.challenge_song.daily_challenge_mst_song_id)
                .scalar_subquery()
            )
            session.execute(
                update(Mission)
                .where(Mission.user == user)
                .where(Mission.mst_mission_id == 72)
                .values(song_idol_type=song_idol_type_subq)
            )

            # Reset weekly missions.
            if (last_login_date.astimezone(server_timezone).year
                    != now.astimezone(server_timezone).year
                    or last_login_date.astimezone(
                        server_timezone).isocalendar()[1]
                    != now.astimezone(server_timezone).isocalendar()[1]):
                session.execute(
                    update(Mission)
                    .where(Mission.user == user)
                    .where(Mission.mst_mission.has(
                        MstMission.mission_type == 2))
                    .values(
                        create_date=now,
                        update_date=now,
                        finish_date=datetime(1, 1, 1),
                        progress=0,
                        mission_state=1
                    )
                )

            # Clear offer list.
            session.execute(
                delete(Offer)
                .where(Offer.user_id == user.user_id)
                .where(Offer.slot == 0)
            )

            # Reset daily free draws.
            for gasha in user.gashas:
                if gasha.mst_gasha_id == 99002:
                    gasha.draw1_free_count = 1
                    gasha.balloon = 1

        user_schema = UserSchema()
        result['user'] = user_schema.dump(user)

        session.commit()

    return result

