from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (EventMemory, EventStory, EventTalkStory,
                                MstEventTalkCallText)
from mltd.models.schemas import (EventMemorySchema, EventStorySchema,
                                 EventTalkStorySchema, MstEventSchema,
                                 MstEventTalkCallTextSchema,
                                 MstEventTalkControlSchema)


@dispatcher.add_method(name='EventService.GetEventList')
def get_event_list(params):
    """Service for getting currently on-going events.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing event info (see implementation below).
    """
    return {
        'event_list': None,
        'today_event_schedule': {
            'mst_event_id': 0,
            'mst_event_schedule_id': 0,
            'event_schedule_type': 0,
            'is_finished': False,
            'begin_date': None,
            'end_date': None,
            'resource_id': ''
        }
    }


@dispatcher.add_method(name='EventService.GetEventTalkArchiveList',
                       context_arg='context')
def get_event_talk_archive_list(params, context):
    """Service for getting a list of MILLION LIVE WORKING story info.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'event_talk_archive_list',
        whose value is a list of dicts, each representing a MILLION LIVE
        WORKING event. Each dict contains the following keys.
            event_talk_list: A list of dicts. Each dict represents a
                             single day for the event and contains the
                             following keys.
                mst_event_talk_control_id: Master event talk control ID.
                                           This is a unique ID for each
                                           day of each event.
                mst_event_id: Master event ID.
                event_day: Which day of the event this is, starting from
                           day 1.
                mst_event_schedule_id: Master event schedule ID.
                release_event_point: Required event points to unlock
                                     each story for this day (400).
                release_item_id: Master item ID of the required item
                                 (memory piece) to unlock all stories
                                 for this day after the event period
                                 (3001).
                release_item_amount: Number of items required to unlock
                                     all stories for this day after the
                                     event period (1).
                reward_item_list: A list containing a single dict
                                  representing the rewards for reading
                                  the stories for this day. See the
                                  return value 'reward_item_list' of the
                                  method 'IdolService.GetIdolList' for
                                  the dict definition.
                event_talk_story_status_list: A list of dicts
                                              representing the stories
                                              for this day. Each dict
                                              contains the following
                                              keys.
                    mst_event_talk_story_id: Master event talk story ID.
                                             This is a unique ID for
                                             each story episode of each
                                             event.
                    episode: Story episode number for this event.
                    release_event_point: Required event points to unlock
                                         this story for this day.
                    mst_event_talk_speaker_id: A list of ints
                                               representing the idols
                                               in this story.
                    bg_id: Background ID.
                    thumbnail_id: Thumbnail ID.
                    begin_date: Date when this story becomes available.
                    released_date: Date when this story was unlocked by
                                   the user.
                    is_released: Whether the user has unlocked this
                                 story.
                    is_read: Whether the user has read this story.
                event_talk_call_text: A list of 52 dicts representing
                                      all idols. Each dict contains the
                                      the following keys.
                    mst_event_talk_call_text_id: Same as master idol ID.
                    speaker_id: Same as master idol ID.
            event_data: A dict representing event info. Contains the
                        following keys.
                mst_event_id: Master event ID.
                begin_date: Date when the event begins.
                end_date: Date when the event ends.
                page_begin_date: Date when the event page becomes
                                 available.
                page_end_date: Date when the event page becomes
                               unavailable.
                boost_begin_date: '0001-01-01T00:00:00+0000'.
                boost_end_date: '0001-01-01T00:00:00+0000'.
                event_type: Event type (6).
                cue_sheet: ''.
                cue_name: ''.
                cue_sheet2: ''.
                cue_name2: ''.
                ending_cue_sheet: ''.
                ending_cue_name: ''.
                appeal_type: 0.
                is_board_open: false.
    """
    with Session(engine) as session:
        mst_event_talk_call_texts = session.scalars(
            select(MstEventTalkCallText)
        ).all()
        event_talk_stories = session.scalars(
            select(EventTalkStory)
            .where(EventTalkStory.user_id == UUID(context['user_id']))
        ).all()

        event_schema = MstEventSchema()
        event_talk_control_schema = MstEventTalkControlSchema()
        event_talk_story_schema = EventTalkStorySchema()
        event_talk_call_text_schema = MstEventTalkCallTextSchema()

        # Construct a dict with this structure:
        # {
        #   mst_event_id: {
        #       mst_event_talk_control_id: [event_talk_story, ...],
        #       ...
        #   },
        #   ...
        # }
        event_dict = {}
        for event_talk_story in event_talk_stories:
            mst_event_id = (event_talk_story.mst_event_talk_story
                            .mst_event_talk_control.mst_event_id)
            mst_event_talk_control_id = (event_talk_story.mst_event_talk_story
                                         .mst_event_talk_control_id)
            event_talk_dict = event_dict.get(mst_event_id, {})
            event_talk_story_list = event_talk_dict.get(
                mst_event_talk_control_id, [])
            event_talk_story_list.append(event_talk_story)
            event_talk_dict[mst_event_talk_control_id] = event_talk_story_list
            event_dict[mst_event_id] = event_talk_dict

        event_talk_call_text = event_talk_call_text_schema.dump(
            mst_event_talk_call_texts, many=True)
        event_talk_archive_list = []
        for event_talk_dict in event_dict.values():
            event_data = None
            event_talk_list = []
            for event_talk_story_list in event_talk_dict.values():
                if not event_data:
                    event_data = event_schema.dump(
                        event_talk_story_list[0].mst_event_talk_story
                        .mst_event_talk_control.mst_event)
                event_talk = event_talk_control_schema.dump(
                    event_talk_story_list[0].mst_event_talk_story
                    .mst_event_talk_control)
                event_talk['event_talk_story_status_list'] = (
                    event_talk_story_schema.dump(event_talk_story_list,
                                                 many=True))
                event_talk['event_talk_call_text'] = event_talk_call_text
                event_talk_list.append(event_talk)
            event_talk_archive_list.append({
                'event_talk_list': event_talk_list,
                'event_data': event_data
            })

    return {'event_talk_archive_list': event_talk_archive_list}


@dispatcher.add_method(name='EventService.GetEventLiveInfo')
def get_event_live_info(params):
    """Service for getting event live info.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing event live info (see implementation below).
    """
    return {
        'event_live_info': {
            'mst_event_id': 0,
            'mst_song_id': 0,
            'mst_item_id': 0,
            'mst_event_macaroon_cost_list': None,
            'ratio': 0,
            'is_boost': False,
            'event_appeal_type': 0,
            'appeal_ratio': 0
        }
    }


@dispatcher.add_method(name='EventService.GetEventMacaroon')
def get_event_macaroon(params):
    """Service for getting event macaroon.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing event macaroon info (see implementation below).
    """
    return {
        'event_macaroon': {
            'event_macaroon_id': '',
            'user_id': '',
            'mst_event_id': 0,
            'amount': 0,
            'create_date': None,
            'max_event_item_count': 0,
            'vitality_scale_list': None,
            'event_item_scale_list': None
        }
    }


@dispatcher.add_method(name='EventService.GetEventStoryList',
                       context_arg='context')
def get_event_story_list(params, context):
    """Service for getting a list of event stories.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        event_story_status_list: A list of dicts representing event
                                 story info. Each dict contains the
                                 following keys.
            mst_event_story_id: Master event story ID.
            mst_idol_id_list: A list of at least 5 master idol IDs
                              representing the idols in this event
                              story. If there are less than 5 idols in
                              this story, zeros are appended to the
                              list.
            mst_event_id: Master event ID.
            event_type: Event type (3-5).
            number: A sequential number representing the event story
                    episode number, starting from number 0.
            has_mv: Whether there is MV in this event story.
            has_mv_twin: false.
            event_story_mv_status: A dict representing the event story
                                   MV info. Contains the following keys.
                mst_song_id: Master song ID (0 if none).
                mv_song_status: A dict containing the MV song info. See
                                the return value 'song_list' of the
                                method 'SongService.GetSongList' for the
                                dict definition.
                mv_unit_idol_list: A list of dicts representing the
                                   idols performing in the MV (null if
                                   none). See the return value
                                   'mv_unit_idol_list' of the method
                                   'StoryService.GetSpecialStoryList'
                                   for the dict definition.
            event_story_mv_twin_status: Same as event_story_mv_status,
                                        but contains no meaningful info.
            release_event_point: Event points required to unlock this
                                 event story episode during the event.
            released_date: Date when the user unlocked this event story.
            begin_date: Date when this event begins.
            end_date: Date when this event ends.
            page_begin_date: Date when this event page becomes
                             available.
            page_end_date: Date when this event page becomes
                           unavailable.
            is_released: Whether the user has unlocked this event story.
            is_read: Whether the user has read this event story.
            reward_item_list: A list of dicts representing the rewards
                              for reading this event story. See the
                              return value 'reward_item_list' of the
                              method 'IdolService.GetIdolList' for the
                              dict definition.
            release_mst_item_id: Master item ID of the required item to
                                 unlock this event story after the event
                                 period (0 for episodes that are
                                 unlocked by default, 3001 for episodes
                                 that require unlocking).
            release_item_amount: Number of items required to unlock this
                                 event story after the event period (0
                                 or 2).
            release_item_begin_date: Date when this event story becomes
                                     unlockable using items after the
                                     event period.
            before_scenario_id: '-'.
        event_memory_status_list: A list of dicts representing event
                                  memory info. Each dict contains the
                                  following keys.
            mst_event_memory_id: Master event memory ID.
            mst_event_id: Master event ID.
            release_mst_item_id: Master item ID of the required item to
                                 unlock this event memory after the
                                 event period (3001).
            release_item_amount: Number of items required to unlock this
                                 event memory after the event period
                                 (1).
            release_item_begin_date: Date when this event memory becomes
                                     unlockable using items after the
                                     event period.
            is_released: Whether the user has unlocked this event story.
            event_memory_type: Event memory type (1-3).
            event_contact_status: A dict representing the theater
                                  contact info for this event memory
                                  (event_memory_type=1 only). Each dict
                                  contains the following keys.
                mst_event_id: Master event ID.
                theater_room_status: See the return value
                                     'theater_room_status' of the method
                                     'StoryService.GetStoryList' for the
                                     dict definition.
                duration: Duration of this theater contact.
            mst_song_id: Master song ID for this event memory
                         (event_memory_type=3 only).
            event_encounter_message_status: A dict containing the
                                            following keys.
                mst_song_unit_id: 0.
                event_encounter_status_list: null.
                past_mst_event_id: 0.
    """
    with Session(engine) as session:
        event_stories = session.scalars(
            select(EventStory)
            .where(EventStory.user_id == UUID(context['user_id']))
        ).all()
        event_memories = session.scalars(
            select(EventMemory)
            .where(EventMemory.user_id == UUID(context['user_id']))
        ).all()

        event_story_schema = EventStorySchema()
        event_story_status_list = event_story_schema.dump(event_stories,
                                                          many=True)
        event_memory_schema = EventMemorySchema()
        event_memory_status_list = event_memory_schema.dump(event_memories,
                                                            many=True)

    return {
        'event_story_status_list': event_story_status_list,
        'event_memory_status_list': event_memory_status_list
    }

