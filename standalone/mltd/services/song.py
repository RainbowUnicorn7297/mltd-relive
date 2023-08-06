from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Course, MstCourseReward, MstRewardItem,
                                MstScoreThreshold, Song)
from mltd.models.schemas import CourseSchema, MstRewardItemSchema, SongSchema
from mltd.servers.i18n import translation

_ = translation.gettext


def localize_song_name(mst_song_id):
    """Get the localized name for a song.

    Args:
        mst_song_id: Master song ID.
    Returns:
        A str representing the localized name of the song.
    """
    return [
        '',
        'Thank You!',
        'HOME, SWEET FRIENDSHIP',
        'Blue Symphony',
        _('Kokoro ga Kaeru Basho'),
        _('Toumei na Prologue'),
        _('Happy☆Lucky☆Jet Machine'),
        'Precious Grain',
        'Sentimental Venus',
        _('Suteki na Kiseki'),
        _('Tokimeki no Onpu ni Natte'),
        _('Marionette wa Nemuranai'),
        'THE IDOLM@STER',
        'Happy Darling',
        _('After School Party Time'),
        _('Smile Ichiban'),
        'IMPRESSION→LOCOMOTION!',
        _('Koi no Lesson Shokyuuhen'),
        _('Jireru Heart ni Hi o Tsukete'),
        _('Liar Rouge'),
        _('Original Koe ni Natte'),
        'dear...',
        _('Festa Illumination'),
        _('Chou↑Genki Show☆Idol ch@ng!'),
        _('Ano ne, Kiite Hoshii Koto ga Arunda'),
        _('Kokoro☆Exercise'),
        'Shooting Stars',
        'PRETTY DREAMER',
        'Growing Storm!',
        _('...In The Name Of。 ...LOVE?'),
        _('Happy～ Effect!'),
        _('Heart♡・Days・Night☆'),
        'vivid color',
        'WHY?',
        'Brand New Theater!',
        _('Ruriiro Kingyo to Hanashoubu'),
        _('Hummingbird'),
        'Good-Sleep, Baby♡',
        _('Jibun REST@RT'),
        _('FairyTale ja Irarenai'),
        'STANDING ALIVE',
        'Angelic Parade♪',
        _('DREAM TRAVELER'),
        'Princess Be Ambitious!!',
        'Welcome!!',
        'READY!!',
        _('Kuraki Hoshi, Tooi Tsuki'),
        _('Aikotoba wa Start Up!'),
        _('Nijiiro letters'),
        _('Unison☆Beat'),
        _('Hoshikuzu no Symphonia'),
        _('ZETTAI × BREAK!! Twinkle Rhythm'),
        _('Machiuke Prince'),
        '',
        'Melty Fantasia',
        'Birth of Color',
        _('Hanazakari Weekend✿'),
        '',
        '',
        'Eternal Harmony',
        _('Saku wa Ukiyo no Kimi Hanabi'),
        'Dreaming!',
        'UNION!!',
        _('Fantasista Carnival'),
        'Blooming Star',
        'ToP!!!!!!!!!!!!!',
        _("BigBang's Volleyball!!!!!"),
        _('Sun Rhythm Orchestra♪'),
        'brave HARMONY',
        _('Ordinary Clover'),
        'Starry Melody',
        _('Last Actress'),
        'FIND YOUR WIND!',
        _('Koigokoro Masquerade'),
        _('Jungle☆Party'),
        _('Harmonics'),
        _('Merry'),
        _('Harumachi Joshi'),
        _('THE IDOLM@STER Hatsuboshi-mix'),
        _('Animal☆Station!'),
        'Raise the FLAG',
        _('Datte Anata wa Princess'),
        'BOUNCING♪ SMILE!',
        _('Rolling△Sankaku'),
        _('SeichouChu→LOVER!!'),
        _('Asayake no Crescendo'),
        _('Getsuyoubi no Cream Soda'),
        'Maria Trap',
        'Bonnes! Bonnes!! Vacances!!!',
        _('PicoPico IIKO! Invader'),
        'WE ARE ONE!!',
        _('OVERMASTER'),
        _('Invincible Justice'),
        'Justice OR Voice',
        _("Beginner's☆Strike"),
        'Episode. Tiara',
        _('Oshiete last note…'),
        _('Primula'),
        _('Hana Shirabe'),
        'LEADER!!',
        _('Ryuuseigun'),
        'fruity love',
        _('Orange no Sora no Shita'),
        'White Vows',
        'Rebellion',
        'MUSIC♪',
        'Flyers!!!',
        'MUSIC JOURNEY',
        "dans l'obscurité",
        _('Marionette no Kokoro'),
        _('Running High'),
        _('Sakashima no Kotoba'),
        _('Rabbit Fur'),
        'Just be myself!!',
        _('Akai Sekai ga Kieru Koro'),
        _('Mirai Hikou'),
        'Girl meets Wonder',
        _('Kyun! Vampire Girl'),
        _('Kiramekirari')
    ][mst_song_id]


@dispatcher.add_method(name='SongService.GetSongList', context_arg='context')
def get_song_list(params, context):
    """Service for getting a list of all songs.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: A dict containing the following key.
            is_all: true.
    Returns:
        A dict containing a single key named 'song_list', whose value is
        a list of dicts. Each of the dict represents a single song and
        contains the following keys.
            song_id: Unique song ID per user per song (user_id +
                     mst_song_id).
            mst_song_id: Master song ID.
            mst_song: A dict with abridged master song info. Contains
                      the following keys.
                mst_song_id: Master song ID.
                sort_id: Sort ID.
                resource_id: A string for getting song-related
                             resources.
                idol_type: Song idol type (1-4).
                song_type: Song type (1=Normal, 2=Special).
                kind: Unknown (0-16).
                stage_id: Unknown (1-48).
                stage_ts_id: Unknown (1-6).
                bpm: 234.
            song_type: Song type (1=Normal, 2=Special).
            sort_id: Sort ID.
            released_course_list: A list of course IDs representing the
                                  unlocked courses for this user (1-6).
            course_list: A list of 6 dicts representing the course info
                         for this song. Each dict contains the following
                         keys.
                course_id: Course ID (1-6).
                cost: Vitality cost for this course.
                level: Song level.
                appeal: Target appeal value for this course.
                score: Highest score obtained by the user.
                combo: Highest combo obtained by the user.
                clear: Number of times the user has cleared this course.
                score_rank: Best score rank obtained by the user (0-4).
                combo_rank: Best combo rank obtained by the user (0-4).
                clear_rank: Best clear rank obtained by the user (0-4).
                notes: Number of notes for this course.
            is_released_mv: true.
            is_released_horizontal_mv: Whether the unit MV has been
                                       unlocked by the user (by clearing
                                       any of the unit courses at least
                                       once).
            is_released_vertical_mv: Whether the solo MV has been
                                     unlocked by the user (by clearing
                                     any of the solo courses at least
                                     once).
            resource_id: A string for getting song-related resources.
            idol_type: Song idol type (1-4).
            kind: Unknown (0-16).
            stage_id: Unknown (1-48).
            stage_ts_id: Unknown (1-6).
            bpm: 234.
            is_cleared: Whether the user has cleared this song.
            first_cleared_date: Date when the user first cleared this
                                song.
            is_played: Whether the user has played this song.
            lp: Song LP.
            is_visible: true.
            apple_song_url: An empty string.
            google_song_url: An empty string.
            is_disable: Whether to disable this song because the user
                        has not unlocked it.
            song_open_type: Song unlock type (0 if unlocked by default).
                            1 = From panel missions (THE IDOLM@STER)
                            2 = From main stories
                            3 = From shop
                            4 = From obtaining Shika's card (Blooming
                                Star)
            song_open_type_value: For songs with song_open_type=2, this
                                  is the corresponding main story
                                  episode (1-49). For other songs, this
                                  value is 0.
            song_open_level: For songs with song_open_type=2, this is
                             the required user level to unlock this song
                             (1-50). For other songs, this value is 0.
            song_unit_idol_id_list: A list of at least 5 master idol IDs
                                    representing the idols in the
                                    default song unit. If the song unit
                                    has less than 5 idols, zeros are
                                    appended to this list.
            mst_song_unit_id: Master song unit ID.
            idol_count: Number of idols performing in this song (1-5,
                        13).
            icon_type: Icon type.
                       0=no icon
                       1=separate vocals (分唱對應)
                       2=partially separate vocals (部分分唱對應)
            extend_song_status: A nullable dict representing extend song
                                info (if any). Contains the following
                                keys.
                resource_id: A string for getting song-related
                             resources.
                kind: Unknown (7-16).
                stage_id: Unknown (5-44).
                stage_ts_id: Unknown (1-2).
                mst_song_unit_id: Master song unit ID.
                song_unit_idol_id_list: A list of master idol IDs
                                        representing the idols in the
                                        default song unit.
                unit_selection_type: Unknown (1-3).
                unit_song_type: Unit song type (1=normal, 2=13 idols).
                icon_type: Icon type.
                           3=13 live (13人演唱會)
                           4=13 live (13人演唱會) & separate vocals
                             (分唱對應)
                           5=duo live (雙人組演唱會)
                           10=sound source selection (音源選擇) &
                              partially separate vocals (部分分唱對應)
                idol_count: Number of idols performing in this song
                            (2-3, 13).
                extend_type: Unknown (0-1).
                filter_type: Filter type (0=normal, 1=duo live, 2=13
                             live).
                song_open_type: 0.
                song_open_type_value: 0.
                song_open_level: 0.
            unit_selection_type: Unknown (1-3).
            only_default_unit: True for Blooming Star. False for
                               everything else.
            only_extend: True for THE IDOLM@STER 初星-mix. False for
                         everything else.
            is_off_vocal_available: Whether instrumental version is
                                    available.
            off_vocal_status: A dict representing instrumental version
                              info. Contains the following keys.
                is_released: Whether the instrumental version has been
                             unlocked by the user (false if no off
                             vocal).
                off_vocal_cue_sheet: Off vocal cue sheet (an empty
                                     string if no off vocal).
                off_vocal_cue_name: Off vocal cue name (an empty string
                                    if no off vocal).
            song_permit_control: True for Blooming Star. False for
                                 everything else.
            permitted_mst_idol_id_list: null.
            permitted_mst_agency_id_list: null.
            extend_song_playable_status: An int representing the
                                         playable status of the extend
                                         song.
                                         0 = No extend song
                                         2 = Playable
            is_new: Whether this song is new to the user.
            live_start_voice_mst_idol_id_list: null.
            is_enable_random: Whether this song can appear in random
                              selection. False for Blooming Star and
                              THE IDOLM@STER 初星-mix. True for
                              everything else.
            part_permitted_mst_idol_id_list: A list containing a single
                                             int 201 for White Vows.
                                             Null for everything else.
            is_recommend: false.
            song_parts_type: 1 for songs with partially separate vocals.
                             0 for everything else.
    """
    with Session(engine) as session:
        songs = session.scalars(
            select(Song)
            .where(Song.user_id == UUID(context['user_id']))
        ).all()

        song_schema = SongSchema()
        song_list = song_schema.dump(songs, many=True)

    return {'song_list': song_list}


@dispatcher.add_method(name='SongService.GetCourse', context_arg='context')
def get_course(params, context):
    """Service for getting course info for a user.

    Invoked in the following situations.
    1. When the user has finished a song and one or more
       score/combo/clear rank rewards were obtained.
    2. When the user presses Rewards button on song selection screen.
    Args:
        params: A dict containing the following keys.
            mst_song_id: Master song ID.
            course: Course.
    Returns:
        A dict containing the following keys.
            course: A dict representing the course info. See the return
                    value 'course_list' of the method
                    'SongService.GetSongList' for the dict definition.
            course_reward: A dict representing course reward info. See
                           the return value 'course_reward' of the
                           method 'LiveService.FinishSong' for the dict
                           definition. All mission statuses are either
                           0 or 1.
    """
    with Session(engine) as session:
        course_id = params['course']
        course = session.scalars(
            select(Course)
            .where(Course.user_id == UUID(context['user_id']))
            .where(Course.mst_song_id == params['mst_song_id'])
            .where(Course.course_id == course_id)
        ).one()
        course_schema = CourseSchema()
        course_dict = course_schema.dump(course)

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
        reward_item_schema = MstRewardItemSchema()
        course_reward = {
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

    return {
        'course': course_dict,
        'course_reward': course_reward
    }

