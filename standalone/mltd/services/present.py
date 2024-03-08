import json
import random
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timezone
from time import sleep
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Achievement, Item, LastUpdateDate, MstItem,
                                Present, User)
from mltd.models.schemas import PresentSchema
from mltd.servers.config import config
from mltd.servers.logging import logger


def add_present(session: Session, user: User, present: Present):
    """Give present to a user.

    Args:
        session: Existing SQLAlchemy session.
        user: A User object.
        present: A Present object representing the present to be given
                 to the user.
    Returns:
        None.
    """
    if present.present_type == 1:
        item_id = session.scalar(
            select(Item.item_id)
            .where(Item.item_id == present.item_id)
        )
        if not item_id:
            user.items.append(Item(
                item_id=present.item_id,
                mst_item_id=int(present.item_id.split('_')[1]),
                amount=0
            ))
    elif present.present_type == 3:
        achievement_id = session.scalar(
            select(Achievement.mst_achievement_id)
            .where(Achievement.user_id == user.user_id)
            .where(Achievement.mst_achievement_id
                   == present.mst_achievement_id)
        )
        if not achievement_id:
            session.add(Achievement(
                user_id=user.user_id,
                mst_achievement_id=present.mst_achievement_id,
                is_released=False
            ))

    # Make sure create_date is unique.
    while True:
        create_date = datetime.now(timezone.utc)
        duplicate_count = session.scalar(
            select(func.count(Present.present_id))
            .where(Present.create_date == create_date)
        )
        if not duplicate_count:
            break
        # TODO: Reproduce before deleting this log
        logger.info('Found duplicate create_date')
        sleep(random.uniform(0.001, 0.020))
    present.create_date = create_date
    session.add(present)
    session.expire(user, ['presents'])

    session.execute(
        update(LastUpdateDate)
        .where(LastUpdateDate.user_id == user.user_id)
        .where(LastUpdateDate.last_update_date_type == 1)
        .values(last_update_date=datetime.now(timezone.utc))
    )


@dispatcher.add_method(name='PresentService.GetPresentCount',
                       context_arg='context')
def get_present_count(params, context):
    """Service for getting number of presents for a user.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. When the game is transitioning to the theater screen.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key 'value', whose value is the
        number of presents in user's present box. If the user has more
        than 100 presents, this value is set to 100.
    """
    with Session(engine) as session:
        value = session.scalar(
            select(func.count(Present.present_id))
            .where(Present.user_id == UUID(context['user_id']))
            .where(datetime.now(timezone.utc) < Present.end_date)
        )

    return {'value': min(value, 100)}


@dispatcher.add_method(name='PresentService.GetPresentList',
                       context_arg='context')
def get_present_list(params, context):
    """Service for getting a list of presents for a user.

    Invoked when the user presses Presents button.
    Args:
        params: A dict containing the following keys.
            cursor: Cursor returned by the previous invocation if the
                    user has just scrolled to the bottom to get the next
                    page (an empty string if no previous cursor).
            limit: 100.
            is_sort_asc: Whether the list should be sorted in ascending
                         order (default false).
            is_sort_end_date: Whether the list should be sorted by
                              'end_date' (default false, sorted by
                              'create_date').
            present_end_date_type: An int representing the expiration
                                   type (0-2).
                                   0=All presents
                                   1=Presents with no expiration
                                   2=Presents with expiration
            present_filter_type: An int representing the filter type
                                 (0-4).
                                 0=All presents
                                 1=Cards
                                 2=Money
                                 3=Items
                                 4=Others (Jewels/Achievements)
    Returns:
        A dict containing the following keys.
        present_list: A list of dicts containing the following keys.
            present_id: A unique present ID in UUID format.
            comment: Comment describing where the present came from.
            end_date: Date when this present expires
                      (2099-12-31T15:59:59+0000 if no expiration).
            create_date: Date when this present was created.
            amount: Amount of items the user will receive (1 for card
                    and achievement presents).
            present_type: An int representing the present type (1-3).
                          1=Item
                          2=Card
                          3=Achievement
            item: A dict representing the item to be received (empty
                  info if not an item present). See the return value
                  'item_list' of the method 'ItemService.GetItemList'
                  for the dict definition.
            card: A dict representing the card to be received (empty
                  info if not a card present). See the return value
                  'card_list' of the method 'CardService.GetCardList'
                  for the dict definition.
            achievement: A dict representing the achievement to be
                         received (empty info if not an achievement
                         present). See the return value
                         'achievement_list' of the method
                         'AchievementService.GetAchievementList' for the
                         dict definition.
            present_state: An int representing the present state (1-2).
                           1=Not yet received
                           2=Has been received
            exchange_item_list: null.
        cursor: Pagination cursor for the next invocation to fetch the
                next 100 items (an empty string if no items left).
    """
    user_id = UUID(context['user_id'])
    with Session(engine) as session:
        session.execute(
            delete(Present)
            .where(Present.user_id == user_id)
            .where(Present.end_date <= datetime.now(timezone.utc))
        )

        present_stmt = (
            select(Present)
            .where(Present.user_id == user_id)
            .where(Present.present_state == 1)
        )

        default_end_date = datetime(
            2099, 12, 31, 23, 59, 59, tzinfo=config.timezone
        ).astimezone(timezone.utc)
        if params['present_end_date_type'] == 1:
            present_stmt = present_stmt.where(
                Present.end_date == default_end_date)
        elif params['present_end_date_type'] == 2:
            present_stmt = present_stmt.where(
                Present.end_date < default_end_date)

        money_item_subq = (
            select(Item.mst_item_id)
            .join(MstItem)
            .where(Item.item_id == Present.item_id)
            .where(MstItem.item_type == 2)
        ).exists()
        if params['present_filter_type'] == 1:
            present_stmt = present_stmt.where(Present.present_type == 2)
        elif params['present_filter_type'] == 2:
            present_stmt = present_stmt.where(money_item_subq)
        elif params['present_filter_type'] == 3:
            present_stmt = (
                present_stmt
                .where(~money_item_subq)
                .where(Present.present_type == 1)
                .where(Present.item_id != f'{user_id}_3')
            )
        elif params['present_filter_type'] == 4:
            present_stmt = present_stmt.where(or_(
                Present.item_id == f'{user_id}_3',
                Present.present_type == 3
            ))

        if params['cursor']:
            cursor = json.loads(urlsafe_b64decode(params['cursor']))
            if not params['is_sort_end_date']:
                last_create_date = datetime.fromtimestamp(
                    cursor['create_date'], tz=timezone.utc)
                if params['is_sort_asc']:
                    present_stmt = present_stmt.where(
                        Present.create_date > last_create_date)
                else:
                    present_stmt = present_stmt.where(
                        Present.create_date < last_create_date)
            else:
                last_end_date = datetime.fromtimestamp(
                    cursor['end_date'], tz=timezone.utc)
                last_present_id = UUID(cursor['present_id'])
                if params['is_sort_asc']:
                    present_stmt = present_stmt.where(
                        or_(Present.end_date > last_end_date,
                            and_(Present.end_date == last_end_date,
                                 Present.present_id > last_present_id))
                    )
                else:
                    present_stmt = present_stmt.where(
                        or_(Present.end_date < last_end_date,
                            and_(Present.end_date == last_end_date,
                                 Present.present_id > last_present_id))
                    )

        if not params['is_sort_end_date']:
            if params['is_sort_asc']:
                present_stmt = present_stmt.order_by(Present.create_date)
            else:
                present_stmt = present_stmt.order_by(
                    Present.create_date.desc())
        else:
            if params['is_sort_asc']:
                present_stmt = present_stmt.order_by(
                    Present.end_date, Present.present_id)
            else:
                present_stmt = present_stmt.order_by(
                    Present.end_date.desc(), Present.present_id)

        present_stmt = present_stmt.limit(params['limit'])
        presents = session.scalars(present_stmt).all()

        present_schema = PresentSchema()
        present_list = present_schema.dump(presents, many=True)

        cursor = ''
        if len(presents) >= 100:
            last_present = presents[-1]
            cursor_dict = {}
            if not params['is_sort_end_date']:
                cursor_dict['create_date'] = datetime.timestamp(
                    last_present.create_date.replace(tzinfo=timezone.utc))
            else:
                cursor_dict['end_date'] = datetime.timestamp(
                    last_present.end_date.replace(tzinfo=timezone.utc))
                cursor_dict['present_id'] = str(last_present.present_id)
            cursor = urlsafe_b64encode(
                json.dumps(cursor_dict).encode()
            ).decode()

        session.commit()

    return {
        'present_list': present_list,
        'cursor': cursor
    }

