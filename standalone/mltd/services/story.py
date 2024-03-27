from datetime import timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (MainStoryChapter, MstMainStoryContactStatus,
                                MstTopics, MstWhiteBoard, SpecialStory)
from mltd.models.schemas import (MainStoryChapterSchema,
                                 MstMainStoryContactStatusSchema,
                                 MstTopicsSchema, MstWhiteBoardSchema,
                                 SpecialStorySchema)
from mltd.servers.config import config
from mltd.servers.utilities import format_datetime


@dispatcher.add_method(name='StoryService.GetStoryList', context_arg='context')
def get_story_list(params, context):
    """Get a list of main stories.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        main_story_list: A list of dicts representing the main story
                            episodes and chapters. Each dict contains
                            the following keys.
            mst_main_story_id: Master main story ID.
            mst_idol_id_list: A list of 5 master idol IDs representing
                              the idols in the song unit for this main
                              story episode. If there are less than 5
                              idols, zeros are appended to this list.
            release_level: Required user level to unlock this episode.
            release_song_id: Master song ID of the song that must be
                             cleared at least once before this episode
                             can be unlocked.
            released_date: Date when this episode is unlocked.
            reward_song_id: Master song ID of the song rewarded after
                            reading this episode.
            reward_song: A dict containing the reward song info. See the
                         return value 'mst_song' of the method
                         'SongService.GetSongList' for the dict
                         definition.
            reward_extend_song: A dict containing the extend song info
                                for the reward song. See the return
                                value 'extend_song_status' of the method
                                'SongService.GetSongList' for the dict
                                definition.
            number: Main story episode number. Same as
                    'mst_main_story_id'.
            chapter: The chapter number for this episode (1-3).
            is_released: Whether this episode has been unlocked.
            is_read: Whether the user has read this chapter for this
                     episode.
            reward_item_list: A list of dicts representing the rewards
                              for reading this episode. See the return
                              value 'reward_item_list' of the method
                              'IdolService.GetIdolList' for the dict
                              definition.
            intro_contact_mst_idol_id: Master idol ID of the main idol
                                       in the intro.
            blog_contact_mst_idol_id: Master idol ID of the idol who
                                      wrote the blog entry.
        main_story_contact_status_list: A list of dicts representing the
                                        theater contact info for each
                                        main story intro. Each dict
                                        contains the following keys.
            mst_main_story_id: Master main story ID.
            theater_room_status: A dict containing the following keys.
                mst_room_id: In which room this theater contact takes
                             place (1-4).
                balloon: A dict containing the following keys.
                    theater_contact_category_type: 2.
                    room_idol_list: A list of dicts representing the
                                    idols for this theater contact. Each
                                    dict contains the following keys.
                        mst_idol_id: Master idol ID.
                        position_id: A string representing the room
                                     position where the idol is at.
                        motion_id: A string representing the idol
                                   motion.
                        reaction_id: An empty string.
                        reaction_id_2: An empty string.
                    resource_id: A string for getting resources related
                                 to this theater contact.
                    mst_theater_contact_schedule_id: 0.
                    mst_theater_contact_id: 0.
                    mst_theater_main_story_id: Master theater main story
                                               ID for this theater
                                               contact.
                    mst_theater_guest_main_story_id: 0.
                    guest_main_story_has_intro: false.
                    mst_guest_main_story_id: 0.
                    mst_theater_blog_id: 0.
                    mst_theater_costume_blog_id: 0.
                    mst_costume_id: 0.
                    mst_theater_event_story_id: 0.
                    mst_event_story_id: 0.
                    mst_event_id: 0.
            duration: Duration of this theater contact.
    """
    with Session(engine) as session:
        main_story_chapters = session.scalars(
            select(MainStoryChapter)
            .where(MainStoryChapter.user_id == UUID(context['user_id']))
        ).all()

        main_story_chapter_schema = MainStoryChapterSchema()
        main_story_list = main_story_chapter_schema.dump(main_story_chapters,
                                                         many=True)

        mst_main_story_contact_statuses = session.scalars(
            select(MstMainStoryContactStatus)
        ).all()

        main_story_contact_status_schema = MstMainStoryContactStatusSchema()
        main_story_contact_status_list = main_story_contact_status_schema.dump(
            mst_main_story_contact_statuses, many=True)

    return {
        'main_story_list': main_story_list,
        'main_story_contact_status_list': main_story_contact_status_list
    }


@dispatcher.add_method(name='StoryService.GetTopicsList')
def get_topics_list(params):
    """Get a list of (loading screen) topics.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        recent_release_date: The most recent release date from the list.
        topics_status_list: A list of dicts representing available
                            topics (tidbits that appear during loading
                            screen). Each dict contains the following
                            keys.
            mst_topics_id: Master topic ID.
            topics_category: Topic category.
                             1 = Secrets (小秘密)
                             2 = Candid shots (休閒照)
                             3 = General tips?
            topics_type: Topic type.
                         1 = Idol topics
                         2 = Secretary (事務員) topics
                         3 = Theater topics
            mst_topics_icon_id: Master topic icon ID (1-52, 101-102,
                                903-908).
            number: A unique number (not necessary sequential) per idol/
                    secretary/theater per category.
            release_date: Release date of this topic.
    """
    with Session(engine) as session:
        recent_release_date = session.scalar(
            select(func.max(MstTopics.release_date))
        )
        recent_release_date = recent_release_date.replace(
            tzinfo=timezone.utc).astimezone(config.timezone)

        mst_topics = session.scalars(
            select(MstTopics)
        ).all()

        mst_topics_schema = MstTopicsSchema()
        topics_status_list = mst_topics_schema.dump(mst_topics, many=True)

    return {
        'recent_release_date': format_datetime(recent_release_date),
        'topics_status_list': topics_status_list
    }


@dispatcher.add_method(name='StoryService.GetWhiteBoardList')
def get_white_board_list(params):
    """Get a list of whiteboard drawings.

    Invoked in the following situations.
    1. 
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        recent_begin_date: The most recent begin date from the list.
        white_board_status_list: A list of dicts representing all
                                 whiteboard drawings. Each dict contains
                                 the following keys.
            mst_white_board_id: Master whiteboard ID.
            mst_topics_icon_id: Master topic icon ID (1-52, 101-102,
                                908).
            number: A mostly sequential number (possibly repeated) per
                    idol/secretary/theater.
            sort_id: Sort ID.
            display_date: Date when this whiteboard drawing was
                          displayed.
            begin_date: Same as 'display_date'.
            end_date: '2099-12-31T23:59:59+0800'.
    """
    with Session(engine) as session:
        recent_begin_date = session.scalar(
            select(func.max(MstWhiteBoard.begin_date))
        )
        recent_begin_date = recent_begin_date.replace(
            tzinfo=timezone.utc).astimezone(config.timezone)

        mst_white_board = session.scalars(
            select(MstWhiteBoard)
        ).all()

        mst_white_board_schema = MstWhiteBoardSchema()
        white_board_status_list = mst_white_board_schema.dump(mst_white_board,
                                                              many=True)

    return {
        'recent_begin_date': format_datetime(recent_begin_date),
        'white_board_status_list': white_board_status_list
    }


@dispatcher.add_method(name='StoryService.GetSpecialStoryList',
                       context_arg='context')
def get_special_story_list(params, context):
    """Get a list of special stories.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named
        'special_story_status_list', whose value is a list of dicts
        representing special story info. Each dict contains the
        following keys.
            mst_special_story_id: Master special story ID.
            mst_special_id: Master special ID.
            mst_idol_id_list: A list of 5 master idol IDs representing
                              the idols in this special story (null if
                              mst_special_stoy_id=0). If there are less
                              than 5 idols in this story, zeros are
                              appended to the list.
            cue_name: Cue name.
            scenario_id: Scenario ID.
            number: A sequential number representing the special story
                    episode number, starting from number 1 (0 if
                    mst_special_story_id=0).
            is_released: Whether the user has unlocked this special
                         story.
            is_read: Whether the user has read this special story.
            reward_item_list: A list of dicts representing the rewards
                              for reading this special story (null if
                              no rewards). See the return value
                              'reward_item_list' of the method
                              'IdolService.GetIdolList' for the dict
                              definition.
            story_type: Story type (1-5).
            card_status: Unknown (Shika's EX card if
                         mst_special_story_id=0, null card for
                         everything else). See the return value
                         'card_list' of the method
                         'CardService.GetCardList' for the dict
                         definition.
            special_mv_status: A dict representing the MV info for this
                               special story. Contains the following
                               keys.
                mst_special_id: 0.
                mst_special_mv_id: 0.
                mst_song_id: Master song ID of the song performed during
                             this special story (0 if none).
                mv_unit_idol_list: A list of dicts representing the
                                   idols performing in the MV (null if
                                   none). Each dict contains the
                                   following keys.
                    mst_idol_id: Master idol ID.
                    costume_status: A dict representing the costume of
                                    this idol. See the return value
                                    'costume_list' of the method
                                    'CardService.GetCardList' for the
                                    dict definition.
            category: Category (2, 3 or 5).
            begin_date: Date when this special story becomes available.
            end_date: Date when this special story becomes unavailable.
    """
    with Session(engine) as session:
        special_stories = session.scalars(
            select(SpecialStory)
            .where(SpecialStory.user_id == UUID(context['user_id']))
        ).all()

        special_story_schema = SpecialStorySchema()
        special_story_status_list = special_story_schema.dump(special_stories,
                                                              many=True)

    return {'special_story_status_list': special_story_status_list}


@dispatcher.add_method(name='StoryService.GetOfferStoryList')
def get_offer_story_list(params):
    """Get a list of offer stories.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key 'offer_story_list' with null
        value.
    """
    return {'offer_story_list': None}

