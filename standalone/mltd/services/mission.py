from datetime import datetime, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session, contains_eager

from mltd.models.engine import engine
from mltd.models.models import (Mission, MstMission, MstMissionReward,
                                MstMissionSchedule, MstPanelMissionSheet,
                                PanelMissionSheet, Song)
from mltd.models.schemas import (MissionSchema, MstMissionScheduleSchema,
                                 MstPanelMissionSheetSchema,
                                 PanelMissionSheetSchema, SongSchema)
from mltd.services.item import add_item


def update_mission_progress(session: Session, user_id, mission: Mission,
                            progress):
    """Update mission progress for a user.

    The mission to be updated can have a state of 0 (prerequisite not
    met), 1 (in progress) or even 3 (completed). It is up to the caller
    to decide whether a mission that has not been started or has already
    been completed should update its progress in the first place.
    Args:
        session: Existing SQLAlchemy session.
        user_id: User ID.
        mission: A Mission object representing the mission to be
                 updated.
        progress: An int representing the new progress.
    Returns:
        A bool indicating whether the updated mission has just changed
        state from in progress to completed.
    """
    now = datetime.now(timezone.utc)
    if progress > mission.progress:
        mission.update_date = now
        mission.progress = progress
        if (mission.mission_state == 1
                and mission.progress >= mission.mst_mission.goal):
            mission.finish_date = now
            mission.mission_state = 3
            receive_mission_rewards(
                session=session,
                user_id=user_id,
                mst_mission=mission.mst_mission
            )
            next_missions = session.scalars(
                select(Mission)
                .join(MstMission)
                .where(Mission.user_id == user_id)
                .where(MstMission.premise_mst_mission_id_list
                       == mission.mst_mission_id)
                .where(Mission.mission_state == 0)
            ).all()
            for mission in next_missions:
                mission.mission_state = 1
            if mission.mst_mission.mst_mission_class_id == 36:
                next_idol_mission = session.scalar(
                    select(Mission)
                    .join(MstMission)
                    .where(Mission.user_id == user_id)
                    .where(MstMission.mst_mission_class_id == 36)
                    .where(MstMission.option == mission.mst_mission.option)
                    .where(Mission.mission_state == 0)
                    .order_by(MstMission.sort_id)
                    .limit(1)
                )
                if next_idol_mission:
                    next_idol_mission.mission_state = 1
            return True
    return False


def receive_mission_rewards(session: Session, user_id,
                            mst_mission: MstMission):
    """User receives the rewards after completing a mission.

    Args:
        session: Existing SQLAlchemy session.
        user_id: User ID.
        mst_mission: A MstMission object representing the completed
                     mission.
    Returns:
        None.
    """
    # FIXME: reward is added to user's present box instead
    for mission_reward in mst_mission.mst_mission_rewards:
        if mission_reward.mst_item_id:
            add_item(
                session=session,
                user_id=user_id,
                mst_item_id=mission_reward.mst_item_id,
                item_type=mission_reward.item_type_id,
                amount=mission_reward.amount
            )
        elif mission_reward.mst_song_id:
            session.execute(
                update(Song)
                .where(Song.user_id == user_id)
                .where(Song.mst_song_id == mission_reward.mst_song_id)
                .values(is_disable=False)
            )
        elif mission_reward.mst_achievement_id:
            # TODO: Handle achievement
            raise NotImplementedError('achievement not yet implemented')


@dispatcher.add_method(name='MissionService.GetMissionList',
                       context_arg='context')
def get_mission_list(params, context):
    """Service for getting a list of missions for the user.

    Invoked as part of the initial batch requests after logging in, and
    by pressing the "Missions" or "Training" buttons.
    Args:
        params: A dict containing a single key named
                'mission_type_list', whose value is a list of ints
                representing what types of missions should be returned.
                If this list contains 1 and 4 (during login), return the
                following:
                    - All daily missions
                    - No weekly missions
                    - Only completed normal missions
                    - Only completed time-limited missions
                    - All panel missions
                    - Only completed idol missions
                If this list is empty (after pressing "Missions"
                button), all in-progress and completed missions are
                returned.
    Returns:
        A dict containing the following keys.
        mission_schedule_list: A list of 4 dicts representing daily,
                               weekly, normal and time-limited missions
                               (including 2nd anniversary training
                               missions). Each dict contains the
                               following keys.
            mst_mission_schedule_id: Master mission schedule ID.
            begin_date: Date when these missions begins.
            end_date: Date when these missions ends.
            mission_list: A list of dicts, each representing a single
                          mission. Each dict contains the following
                          keys.
                mission_type: Mission type (0 if in mission schedule).
                              4 = Panel missions
                              5 = Idol missions
                mst_mission_id: Master mission ID (0 if not in mission
                                schedule).
                mst_panel_mission_id: Master panel mission ID (0 if not
                                      a panel mission).
                mst_idol_mission_id: Master idol mission ID (0 if not a
                                     master mission).
                mst_mission_class_id: Master mission class ID (1-76).
                goal: An int representing the goal for this mission. The
                      meaning of this value depends on the context.
                option: A string representing additional info for this
                        mission when goal alone is insufficient ('-' if
                        none).
                option2: A second string representing additional info
                         for this mission ('-' if none).
                premise_mst_mission_id_list: A list containing a single
                                             master mission ID
                                             representing the
                                             prerequisite mission the
                                             user has to complete before
                                             this mission is unlocked
                                             (0 if no prerequisites).
                                             For panel and idol
                                             missions, this list is
                                             empty.
                mission_reward_list: A list of dicts representing the
                                     rewards for this mission. Each
                                     reward can be an item, an
                                     achievement or a song. Each dict
                                     contains the following keys.
                    mst_item_id: Master item ID (0 if not an item
                                 reward).
                    item_type_id: Item type (0 if not an item reward).
                    amount: Amount of items rewarded (1 if not an item
                            reward).
                    mst_card_id: 0.
                    card: A dict representing a null card. See the
                          return value of 'card_list' of the method
                          'CardService.GetCardList' for the dict
                          definition.
                    mst_achievement_id: Master achievement ID (0 if not
                                        an achievement reward).
                    mst_song_id: Master song ID (0 if not a song
                                 reward).
                    song: A dict representing the rewarded song (or a
                          null song if not a song reward). See the
                          return value 'song_list' of the method
                          'SongService.GetSongList' for the dict
                          definition.
                create_date: Date when this mission is unlocked for the
                             user.
                update_date: Most recent date when the user has made
                             progress and updated this mission.
                finish_date: Date when the user completed this mission
                             ('0001-01-01T00:00:00+0000' if not yet
                             completed).
                progress: Current progress of the user towards the goal.
                          This mission is completed when progress is
                          greater than or equal to the goal.
                mission_state: Mission state.
                               1 = In progress
                               3 = Completed
                sort_id: Sort ID.
                jump_type: A string representing which part of the game
                           it should jump to when the user presses the
                           Details button of this mission.
                mission_operation_label: For 2nd anniversary training
                                         missions, this is a string
                                         associating this mission with
                                         an idol. For all other
                                         missions, this value is '-'.
                song_idol_type: For the daily song mission, this is the
                                idol type of the selected song. For all
                                other missions, this value is 0.
            mission_type: Mission type.
                          0 = Normal missions
                          1 = Daily missions
                          2 = Weekly missions
                          3 = Time-limited missions
        panel_mission_sheet_list: A list of 3 dicts representing the
                                  panel mission sheets. Each dict
                                  contains the following keys.
            mst_panel_mission_sheet_id: Master panel mission sheet ID.
            begin_date: '2018-01-01T00:00:00+0800'.
            end_date: '2099-12-31T23:59:59+0800'.
            mission_list: A list of 9 dicts, each representing a single
                          panel mission on this sheet. See
                          'mission_list' above for the dict definition.
            sheet_reward_list: A list of dicts representing the rewards
                               for completing this sheet. See
                               'mission_reward_list' above for the dict
                               definition.
        idol_mission_list: A list of dicts, each representing a single
                           mission. See 'mission_list' above for the
                           dict definition.
        mission_summary: A dict. See the return value 'mission_summary'
                         of the method 'AuthService.Login' for the dict
                         definition.
    """
    with Session(engine) as session:
        mission_type_list = params['mission_type_list']
        mst_mission_schedules = session.scalars(
            select(MstMissionSchedule)
        ).all()
        mst_panel_mission_sheets = session.scalars(
            select(MstPanelMissionSheet)
        ).all()
        mission_stmt = (
            select(Mission)
            .where(Mission.user_id == UUID(context['user_id']))
            .where(Mission.mission_state.in_([1, 3]))
        )
        if mission_type_list:
            mission_stmt = (
                mission_stmt
                .join(Mission.mst_mission)
                .options(contains_eager(Mission.mst_mission))
                .where(or_(
                    MstMission.mission_type.in_(mission_type_list),
                    and_(~MstMission.mission_type.in_(mission_type_list),
                         Mission.mission_state == 3)))
                .where(MstMission.mission_type != 2)
            )
        missions = session.scalars(mission_stmt).all()
        mission_summary = session.scalars(
            select(PanelMissionSheet)
            .where(PanelMissionSheet.user_id == UUID(context['user_id']))
        ).one()

        mission_schedule_schema = MstMissionScheduleSchema()
        panel_mission_sheet_schema = MstPanelMissionSheetSchema()
        mission_schema = MissionSchema()
        mission_summary_schema = PanelMissionSheetSchema()
        song_schema = SongSchema()

        mission_schedule_list = mission_schedule_schema.dump(
            mst_mission_schedules, many=True)
        for mission_schedule in mission_schedule_list:
            mission_schedule['mission_list'] = []
        panel_mission_sheet_list = panel_mission_sheet_schema.dump(
            mst_panel_mission_sheets, many=True)
        for panel_mission_sheet in panel_mission_sheet_list:
            panel_mission_sheet['mission_list'] = []
            for sheet_reward in panel_mission_sheet['sheet_reward_list']:
                if sheet_reward['mst_song_id']:
                    song = session.scalars(
                        select(Song)
                        .where(Song.user_id == UUID(context['user_id']))
                        .where(Song.mst_song_id == sheet_reward['mst_song_id'])
                    ).one()
                    sheet_reward['song'] = song_schema.dump(song)
        idol_mission_list = []
        mission_summary_dict = mission_summary_schema.dump(mission_summary)

        for mission in missions:
            mission_dict = mission_schema.dump(mission)
            for mission_reward in mission_dict['mission_reward_list']:
                if mission_reward['mst_song_id']:
                    song = session.scalars(
                        select(Song)
                        .where(Song.user_id == UUID(context['user_id']))
                        .where(Song.mst_song_id
                               == mission_reward['mst_song_id'])
                    ).one()
                    mission_reward['song'] = song_schema.dump(song)
            if mission.mst_mission.mst_mission_schedule_id:
                for mission_schedule in mission_schedule_list:
                    if (mission_schedule['mission_type']
                            == mission.mst_mission.mission_type):
                        mission_schedule['mission_list'].append(mission_dict)
                        break
            elif mission.mst_mission.mst_panel_mission_sheet_id:
                for panel_mission_sheet in panel_mission_sheet_list:
                    if (panel_mission_sheet['mst_panel_mission_sheet_id']
                            == mission.mst_mission.mst_panel_mission_sheet_id):
                        panel_mission_sheet['mission_list'].append(
                            mission_dict)
                        break
            else:
                idol_mission_list.append(mission_dict)

    return {
        'mission_schedule_list': mission_schedule_list,
        'panel_mission_sheet_list': panel_mission_sheet_list,
        'idol_mission_list': idol_mission_list,
        'mission_summary': mission_summary_dict
    }

