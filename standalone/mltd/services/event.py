from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import EventTalkStory, MstEventTalkCallText
from mltd.models.schemas import (EventTalkStorySchema, MstEventSchema,
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

