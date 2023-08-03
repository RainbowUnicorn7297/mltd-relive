from uuid import UUID
from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Item, MstBanner, Present
from mltd.models.schemas import MstBannerSchema


@dispatcher.add_method(name='BannerService.GetBannerList',
                       context_arg='context')
def get_banner_list(params, context):
    """Service for getting a list of banners.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        banner_list: A list of dicts representing banner info. Each dict
                     contains the following keys.
            banner_id: Banner ID in UUID format.
            jump: Which part of the game it should jump to after
                  pressing the banner.
            banner_type: 0.
            open_date: Banner open date.
            close_date: Banner close date.
            banner_image_link: A URL to the banner image.
            announce_web_view_link: ''.
            is_gasha_view: True only for Welcome!! guaranteed SSR gacha
                           banner.
            url: ''.
            simple_view_text: ''.
        fixed_banner: A dict with empty banner info. See 'banner_list'
                      above for the dict definition.
    """
    with Session(engine) as session:
        # Check whether the user has Welcome!! guaranteed SSR gacha
        # ticket.
        user_id = UUID(context['user_id'])
        gacha_ticket_amount = session.scalar(
            select(Item.amount)
            .where(Item.user_id == user_id)
            .where(Item.mst_item_id == 719)
        )
        gacha_ticket_present_id = session.scalar(
            select(Present.present_id)
            .where(Present.user_id == user_id)
            .where(Present.present_type == 1)
            .where(Present.item_id == f'{user_id}_719')
            .where(Present.present_state == 1)
            .limit(1)
        )

        banner_stmt = select(MstBanner)
        if not gacha_ticket_amount and not gacha_ticket_present_id:
            banner_stmt = banner_stmt.where(MstBanner.is_gasha_view == False)
        banners = session.scalars(banner_stmt).all()

        banner_schema = MstBannerSchema()
        banner_list = banner_schema.dump(banners, many=True)

    return {
        'banner_list': banner_list,
        'fixed_banner': {
            'banner_id': '',
            'jump': '',
            'banner_type': 0,
            'open_date': None,
            'close_date': None,
            'banner_image_link': '',
            'announce_web_view_link': '',
            'is_gasha_view': False,
            'url': '',
            'simple_view_text': ''
        }
    }

