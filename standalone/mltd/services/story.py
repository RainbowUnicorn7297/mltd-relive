from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import MainStoryChapter, MstMainStoryContactStatus
from mltd.models.schemas import (MainStoryChapterSchema,
                                 MstMainStoryContactStatusSchema)


@dispatcher.add_method(name='StoryService.GetStoryList', context_arg='context')
def get_story_list(params, context):
    """Service for getting a list of main stories.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
            main_story_list: A list of dicts representing the main story
                             episodes and chapters. Each dict contains
                             the following keys.
                mst_main_story_id: Master main story ID.
                mst_idol_id_list: A list of 5 master idol IDs
                                  representing the idols in the song
                                  unit for this main story episode. If
                                  there are less than 5 idols, zeros are
                                  appended to this list.
                release_level: Required user level to unlock this
                               episode.
                release_song_id: Master song ID of the song that must be
                                 cleared at least once before this
                                 episode can be unlocked.
                released_date: Date when this episode is unlocked.
                reward_song_id: Master song ID of the song rewarded
                                after reading this episode.
                reward_song: A dict containing the reward song info. See
                             the return value 'mst_song' of the method
                             'SongService.GetSongList' for the dict
                             definition.
                reward_extend_song: A dict containing the extend song
                                    info for the reward song. See the
                                    return value 'extend_song_status' of
                                    the method 'SongService.GetSongList'
                                    for the dict definition.
                number: Main story episode number. Same as
                        'mst_main_story_id'.
                chapter: The chapter number for this episode (1-3).
                is_released: Whether this episode has been unlocked.
                is_read: Whether the user has read this chapter for this
                         episode.
                reward_item_list: A list of dicts representing the
                                  rewards for reading this episode. See
                                  the return value 'reward_item_list' of
                                  the method 'IdolService.GetIdolList'
                                  for the dict definition.
                intro_contact_mst_idol_id: Master idol ID of the main
                                           idol in the intro.
                blog_contact_mst_idol_id: Master idol ID of the idol who
                                          wrote the blog entry.
            main_story_contact_status_list: A list of dicts representing
                                            the theater contact info for
                                            each main story intro. Each
                                            dict contains the following
                                            keys.
                mst_main_story_id: Master main story ID.
                theater_room_status: A dict containing the following
                                     keys.
                    mst_room_id: In which room this theater contact
                                 takes place (1-4).
                    balloon: A dict containing the following keys.
                        theater_contact_category_type: 2.
                        room_idol_list: A list of dicts representing the
                                        idols for this theater contact.
                                        Each dict contains the following
                                        keys.
                            mst_idol_id: Master idol ID.
                            position_id: A string representing the room
                                         position where the idol is at.
                            motion_id: A string representing the idol
                                       motion.
                            reaction_id: An empty string.
                            reaction_id_2: An empty string.
                        resource_id: A string for getting resources
                                     related to this theater contact.
                        mst_theater_contact_schedule_id: 0.
                        mst_theater_contact_id: 0.
                        mst_theater_main_story_id: Master theater main
                                                   story ID for this
                                                   theater contact.
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

