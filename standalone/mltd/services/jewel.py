from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Jewel
from mltd.models.schemas import JewelSchema


@dispatcher.add_method(name='JewelService.GetJewel', context_arg='context')
def get_card_list(params, context):
    """Service for getting jewel info for the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'jewel', whose value is
        a single dict containing the following keys.
            free_jewel_amount: Amount of free jewels the user has.
            paid_jewel_amount: Amount of paid jewels the user has.
    """
    with Session(engine) as session:
        jewel = session.scalars(
            select(Jewel)
            .where(Jewel.user_id == UUID(context['user_id']))
        ).one()

        jewel_schema = JewelSchema()
        jewel_dict = jewel_schema.dump(jewel)

    return {'jewel': jewel_dict}

