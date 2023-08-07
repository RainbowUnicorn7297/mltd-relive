from datetime import datetime, timezone
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Birthday, MstBirthdayCalendar, MstIdol
from mltd.models.schemas import BirthdaySchema, MstBirthdayCalendarSchema
from mltd.servers.config import server_timezone


def get_birthday_entrance_direction_resource(  
        session: Session,
        mst_character_id,
        birthday_month):
    """Get the entrance direction resource ID for a birthday character.

    Args:
        session: Existing SQLAlchemy session.
        mst_character_id: Master idol ID (1-11, 13-52) or Master
                          secretary ID (101-102) of the birthday
                          character.
        birthday_month: Birthday month.
    Returns:
        A string representing the latest available entrance direction
        resource ID for the birthday character.
    """
    if mst_character_id == 12:      # 雙海真美
        raise ValueError('No resource for mst_character_id=12')
    elif mst_character_id == 101:   # 音無小鳥
        return '101kot,003'
    elif mst_character_id == 102:   # 青羽美咲
        return '102mis,2018'
    else:
        idol_resource_id = session.scalars(
            select(MstIdol.resource_id)
            .where(MstIdol.mst_idol_id == mst_character_id)
        ).one()
        if 7 <= birthday_month and birthday_month <= 9:
            # Return 2019 resource for birthdays between Jul and Sep.
            return f'{idol_resource_id},003'
        else:
            # Return 2018 resource for birthdays in other months.
            return f'{idol_resource_id},2018'


@dispatcher.add_method(name='BirthdayService.GetBirthday',
                       context_arg='context')
def get_birthday(params, context):
    """Service for getting character birthday info for a user.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the game is transitioning to the theater screen.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        birthday_list: A list of dicts representing the birthday info of
                       today's birthday characters (null if today is no
                       one's birthday). Each dict contains the following
                       keys.
            year: Server's current year.
            mst_character_id: Master character ID of this birthday
                              character (1-52, 101-102).
            is_executed: Whether the birthday party has been executed
                         for this user.
            is_birthday_live_played: Whether the user has played the
                                     birthday live.
            mst_idol_id_list: null.
        birthday_calendar_list: A list of dicts representing the
                                birthdays of all characters. Each dict
                                contains the following keys.
            mst_character_id: Master character ID of this character
                              (1-52, 101-102).
            idol_type: Idol type (0 if not an idol).
            birthday_month: Birthday month of this character.
            birthday_day: Birthday day of this character.
        entrance_direction_resource_id_list: A list of strings for
                                             getting resources related
                                             to birthday entrance
                                             direction.
    """
    user_id = UUID(context['user_id'])
    now = datetime.now(timezone.utc)
    server_year = now.astimezone(server_timezone).year
    server_month = now.astimezone(server_timezone).month
    server_day = now.astimezone(server_timezone).day

    with Session(engine) as session:
        birthday_calendars = session.scalars(
            select(MstBirthdayCalendar)
        ).all()

        birthday_calendar_schema = MstBirthdayCalendarSchema()
        birthday_calendar_list = (
            birthday_calendar_schema.dump(birthday_calendars, many=True))

        birthday_list = None
        entrance_direction_resource_id_list = None
        birthday_character_ids = []
        for birthday in birthday_calendars:
            if (server_month == birthday.birthday_month
                    and server_day == birthday.birthday_day):
                birthday_character_ids.append(birthday.mst_character_id)
        if birthday_character_ids:
            inserted_character_ids = session.scalars(
                select(Birthday.mst_character_id)
                .where(Birthday.user_id == user_id)
                .where(Birthday.year == server_year)
                .where(Birthday.mst_character_id.in_(birthday_character_ids))
            ).all()
            for character_id in birthday_character_ids:
                if character_id not in inserted_character_ids:
                    session.add(Birthday(
                        user_id=user_id,
                        year=server_year,
                        mst_character_id=character_id
                    ))
            birthdays = session.scalars(
                select(Birthday)
                .where(Birthday.user_id == user_id)
                .where(Birthday.year == server_year)
                .where(Birthday.mst_character_id.in_(birthday_character_ids))
            ).all()

            birthday_schema = BirthdaySchema()
            birthday_list = birthday_schema.dump(birthdays, many=True)

            entrance_direction_resource_id_list = []
            for character_id in birthday_character_ids:
                if character_id == 12:
                    # Mami uses the same resources as Ami
                    continue
                entrance_direction_resource_id_list.append(
                    get_birthday_entrance_direction_resource(
                        session=session,
                        mst_character_id=character_id,
                        birthday_month=server_month))

        session.commit()

    return {
        'birthday_list': birthday_list,
        'birthday_calendar_list': birthday_calendar_list,
        'entrance_direction_resource_id_list': (
            entrance_direction_resource_id_list)
    }

