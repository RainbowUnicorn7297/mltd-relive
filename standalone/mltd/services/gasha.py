from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Gasha
from mltd.models.schemas import GashaSchema


@dispatcher.add_method(name='GashaService.GetGashaList', context_arg='context')
def get_gasha_list(params, context):
    """Service for getting a list of available gachas.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        gasha_list: A list of dicts representing available gacha
                    banners. Each dict contains the following keys.
            mst_gasha_id: Master gacha ID.
            mst_gasha_ticket_item_id: 0.
            name: Name of the gacha banner.
            display_category: Display category.
            begin_date: Gacha banner begin date.
            end_date: Gacha banner end date.
            currency_type_list: A list of integers representing the
                                currency types (empty if none).
                                1 = Paid jewels
                                2 = Gacha medals
                                6 = Free jewels
            is_paid_jewel_only: Whether the gacha is paid jewel only.
            draw1_jewel_value: Number of jewels required to cast a
                               single draw.
            draw10_jewel_value: Number of jewels required to cast 10
                                draws.
            draw1_mst_item_id: The master item ID of the item required
                               to cast a single draw (0 if none).
            draw10_mst_item_id: The master item ID of the item required
                                to cast 10 draws (0 if none).
            daily_limit: Maximum number of draws allowed per day.
            total_limit: Maximum total number of draws allowed.
            sr_passport: If an SR card is guaranteed for casting 10
                         draws, this value is 1. Otherwise, this value
                         is 0.
            ssr_passport: 0.
            has_new_idol: Unknown.
            has_limited: false.
            notify_num: 0.
            today_count: Number of draws the user has casted today.
            total_count: Total number of draws the user has casted.
            mst_gasha_kind_id: Master gacha kind ID.
            mst_gasha_bonus_id: 0.
            gasha_bonus_item_list: null.
            gasha_bonus_mst_achievement_id_list: null.
            gasha_bonus_costume_list: null.
            ticket_item_list: A list of dicts representing the required
                              items to cast draws for this gacha (empty
                              if none). See the return value 'item_list'
                              of the method 'ItemService.GetItemList'
                              for the dict definition.
            is_limit: Unknown.
                      Possible meaning #1: Whether the draw point max
                      limit is applied to this gacha banner.
                      Possible meaning #2: Whether this is a limited-
                      time gacha banner.
            draw_point_mst_item_id: Master item ID representing draw
                                    points (40).
            draw_point: Number of draw points the user currently has.
            draw_point_max: Maximum number of draw points a user can
                            have before they are required to use them in
                            exchange for a card (300).
            draw1_free_count: Number of free single draws the user
                              currently has. This number can reset
                              daily.
            draw10_free_count: Number of free 10 draws the user
                               currently has (0).
            pickup_signature: An empty string.
            pickup_gasha_card_list: null.
            balloon: Whether the UI should place a balloon (alert icon)
                     on the gacha button. This value is 1 if the user
                     has free draws remaining. Otherwise, this value is
                     0.
        has_need_refresh_gasha_draw_point: false.
    """
    with Session(engine) as session:
        gashas = session.scalars(
            select(Gasha)
            .where(Gasha.user_id == UUID(context['user_id']))
        ).all()

        gasha_schema = GashaSchema()
        gasha_list = gasha_schema.dump(gashas, many=True)

    return {
        'gasha_list': gasha_list,
        'has_need_refresh_gasha_draw_point': False
    }

