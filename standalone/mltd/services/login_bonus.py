from datetime import datetime, timedelta, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Mission, MstMission, User
from mltd.models.schemas import LoginBonusScheduleSchema, MissionSchema
from mltd.servers.config import server_timezone
from mltd.servers.utilities import format_datetime
from mltd.services.item import add_item
from mltd.services.mission import receive_mission_reward


@dispatcher.add_method(name='LoginBonusService.ExecuteLoginBonus',
                       context_arg='context')
def execute_login_bonus(params, context):
    """Service for executing login bonus for a user.

    Invoked after logging in.
    When the user logs in for the first time each day, do the following.
        1. Give login bonus items to the user and return the new states
           of the login bonus schedules.
        2. Increase the progress of all in-progress login missions by 1.
           If goal is reached for any of those, mark them as completed,
           give mission rewards to the user and return the new states to
           the game client.
        3. Update next login date.
        4. If server's date is on these days, return the corresponding
           login direction info:
           - New Year: Jan 1
           - Valentine's Day: Feb 14
           - White Day: Mar 14
           - Christmas: Dec 25
    In all cases, do the following.
        1. If server's date is within these periods, return the
           corresponding theater poster info:
           - New Year: Jan 1-3
           - Valentine's Day: Feb 12-14
           - White Day: Mar 12-14
           - Christmas: Dec 23-25 (TBC)
    Args:
        params: A dict with user settings. Contains the following keys.
            user_live_view: Unknown ('').
            user_live_quality: An int representing live quality.
            user_theater_view: Unknown ('').
            user_theater_quality: An int representing theater quality.
            user_mv_quality: An int representing MV quality.
    Returns:
        A dict containing the following keys.
        login_bonus_list: A list of dicts representing currently ongoing
                          login bonuses. This list is empty if the user
                          has already received the login bonus item
                          today at an earlier time. Each dict contains
                          the following keys.
            mst_login_bonus_schedule_id: Master login bonus schedule ID.
            login_bonus_item_list: A list of dicts, each representing
                                   the item the user will receive on
                                   each day. Each dict contains the
                                   following keys.
                mst_item_id: Master item ID.
                item_type: Item type.
                amount: Amount of items the user will receive on this
                        day.
                day: On which day of this login bonus schedule this item
                     is given to the user (1-7).
                reward_item_state: Current status for this reward item.
                                   1 = User will receive this item on a
                                       later date
                                   2 = User is receiving this item today
                                   3 = User has received this item on an
                                       earlier date
            is_last_day: false.
            resource_id: ''.
            cue_name1: ''.
            cue_name2: ''.
            script_name: Script name for this login bonus schedule.
        mission_process: A dict representing changes in mission states
                         after executing this login bonus. Contains the
                         following keys.
            complete_mission_list: A list of dicts representing missions
                                   that have just been completed (empty
                                   if none). See the return value
                                   'mission_list' of the method
                                   'MissionService.GetMissionList' for
                                   the dict definition.
            open_mission_list: An empty list.
            update_mission_list: An empty list.
            training_point_diff: Unknown. Contains the following keys.
                'before': 0.
                'after': 0.
                'total': 0.
        mission_list: A list of dicts representing missions with changed
                      states. This list is the same as
                      'complete_mission_list' above.
        next_login_date: Next login date (The day after current server
                         date).
        theater_poster: A dict representing the main theater poster.
                        Contains the following keys.
            theater_poster_id: A unique theater poster ID in UUID
                               format (empty if default poster should be
                               displayed).
            place: Where this poster should be placed in the theater
                   (1-3).
            resource_id: A string for getting poster-related resources.
            begin_date: Date when this poster starts being displayed in
                        the theater.
            end_date: Date when this poster stops being displayed in the
                      theater.
            poster_image_url: An URL to the poster image.
        load_back_ground_resource: ''.
        theater_poster_list: A list of dicts representing the theater
                             posters. See 'theater_poster' above for the
                             dict definition.
        login_direction: A dict representing how the user will be
                         greeted by the idols during login. Contains the
                         following keys.
            mst_login_direction_id: Master login direction ID (0 if
                                    default greeting will be used).
            communication_resource_id: A string for getting
                                       communication resources related
                                       to this login direction.
            entrance_direction_resource_id: 'null'.
        login_opening_direction: Unknown. Contains the following keys.
            mst_login_opening_direction_id: 0.
            resource_id: ''.
        campaign_present_list: null.
        update_idol_list: null.
    """
    result = {
        'login_bonus_list': [],
        'mission_process': {
            'complete_mission_list': [],
            'open_mission_list': [],
            'training_point_diff': {
                'before': 0,
                'after': 0,
                'total': 0
            }
        },
        'mission_list': [],
        'next_login_date': None,
        'theater_poster': {
            'theater_poster_id': '',
            'place': 0,
            'resource_id': '',
            'begin_date': None,
            'end_date': None,
            'poster_image_url': ''
        },
        'load_back_ground_resource': '',
        'theater_poster_list': None,
        'login_direction': {
            'mst_login_direction_id': 0,
            'communication_resource_id': '',
            'entrance_direction_resource_id': ''
        },
        'login_opening_direction': {
            'mst_login_opening_direction_id': 0,
            'resource_id': ''
        },
        'campaign_present_list': None,
        'updated_idol_list': None
    }

    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()

        now = datetime.now(timezone.utc)
        server_year = now.astimezone(server_timezone).year
        server_month = now.astimezone(server_timezone).month
        server_day = now.astimezone(server_timezone).day
        next_login_date = (user.login_bonus_schedules[0].next_login_date
                           .replace(tzinfo=timezone.utc))
        if next_login_date <= now:
            for schedule in user.login_bonus_schedules:
                items = schedule.login_bonus_items
                today_item = None
                for item in items:
                    if item.reward_item_state == 2:
                        item.reward_item_state = 3
                    elif item.reward_item_state == 1:
                        item.reward_item_state = 2
                        today_item = item
                        break
                if not today_item:
                    for item in items:
                        item.reward_item_state = 1
                    items[0].reward_item_state = 2
                    today_item = items[0]
                add_item(
                    session=session,
                    user_id=user.user_id,
                    mst_item_id=today_item.mst_login_bonus_item.mst_item_id,
                    item_type=today_item.mst_login_bonus_item.item_type,
                    amount=today_item.mst_login_bonus_item.amount
                )
            login_bonus_schedule_schema = LoginBonusScheduleSchema()
            result['login_bonus_list'] = login_bonus_schedule_schema.dump(
                user.login_bonus_schedules, many=True)

            missions = session.scalars(
                select(Mission)
                .where(Mission.user == user)
                .where(Mission.mst_mission.has(
                    MstMission.mst_mission_class_id.in_([
                        10,     # Normal/Panel login missions
                        42      # Weekly login missions
                    ])))
                .where(Mission.mission_state == 1)
            ).all()
            mission_schema = MissionSchema()
            for mission in missions:
                mission.progress += 1
                mission.update_date = now
                if (mission.progress >= mission.mst_mission.goal
                        and mission.mission_state == 1):
                    mission.mission_state = 3
                    mission.finish_date = now
                    for reward in mission.mst_mission.mst_mission_rewards:
                        receive_mission_reward(
                            session=session,
                            user_id=user.user_id,
                            mission_reward=reward
                        )
                    mission_dict = mission_schema.dump(mission)
                    result['mission_process']['complete_mission_list'].append(
                        mission_dict)
                    result['mission_list'].append(mission_dict)

            next_login_date = (
                now.astimezone(server_timezone) + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).astimezone(timezone.utc)
            for schedule in user.login_bonus_schedules:
                schedule.next_login_date = next_login_date

            if server_month == 1 and server_day == 1:
                result['login_direction'] = {
                    'mst_login_direction_id': 0,    # TODO: Does this matter?
                    'communication_resource_id': 'season_a_2019_{0}_100',
                    'entrance_direction_resource_id': 'null'
                }
            elif server_month == 2 and server_day == 14:
                result['login_direction'] = {
                    'mst_login_direction_id': 0,
                    'communication_resource_id': 'season_a_2019_{0}_200',
                    'entrance_direction_resource_id': 'null'
                }
            elif server_month == 3 and server_day == 14:
                result['login_direction'] = {
                    'mst_login_direction_id': 0,
                    'communication_resource_id': 'season_a_2019_{0}_300',
                    'entrance_direction_resource_id': 'null'
                }
            elif server_month == 12 and server_day == 25:
                result['login_direction'] = {
                    'mst_login_direction_id': 0,
                    'communication_resource_id': 'season_a_2018_{0}_300',
                    'entrance_direction_resource_id': 'null'
                }

        result['next_login_date'] = format_datetime(
            next_login_date.astimezone(server_timezone))

        if server_month == 1 and server_day in [1, 2, 3]:
            result['theater_poster'] = {
                'theater_poster_id': '',    # TODO: Does this matter?
                'place': 1,
                'resource_id': 'theater_poster_201901ny',
                'begin_date': datetime(
                                server_year, 1, 1, tzinfo=server_timezone
                              ).astimezone(timezone.utc),
                'end_date': datetime(
                                server_year, 1, 3, 23, 59, 59,
                                tzinfo=server_timezone
                            ).astimezone(timezone.utc),
                'poster_image_url': ''      # TODO: Does this matter?
            }
        elif server_month == 2 and server_day in [12, 13, 14]:
            result['theater_poster'] = {
                'theater_poster_id': '',
                'place': 1,
                'resource_id': 'theater_poster_valentine2019',
                'begin_date': datetime(
                                server_year, 2, 12, tzinfo=server_timezone
                              ).astimezone(timezone.utc),
                'end_date': datetime(
                                server_year, 2, 14, 23, 59, 59,
                                tzinfo=server_timezone
                            ).astimezone(timezone.utc),
                'poster_image_url': ''
            }
        elif server_month == 3 and server_day in [12, 13, 14]:
            result['theater_poster'] = {
                'theater_poster_id': '',
                'place': 1,
                'resource_id': 'theater_poster_whiteday2019',
                'begin_date': datetime(
                                server_year, 3, 12, tzinfo=server_timezone
                              ).astimezone(timezone.utc),
                'end_date': datetime(
                                server_year, 3, 14, 23, 59, 59,
                                tzinfo=server_timezone
                            ).astimezone(timezone.utc),
                'poster_image_url': ''
            }
        elif server_month == 12 and server_day in [23, 24, 25]:
            result['theater_poster'] = {
                'theater_poster_id': '',
                'place': 1,
                'resource_id': 'theater_poster_201812xm',
                'begin_date': datetime(
                                server_year, 12, 23, tzinfo=server_timezone
                              ).astimezone(timezone.utc),
                'end_date': datetime(
                                server_year, 12, 25, 23, 59, 59,
                                tzinfo=server_timezone
                            ).astimezone(timezone.utc),
                'poster_image_url': ''
            }
        if result['theater_poster']['place']:
            result['theater_poster_list'] = [result['theater_poster']]

        session.commit()

    return result

