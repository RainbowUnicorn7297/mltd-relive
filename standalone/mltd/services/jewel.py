from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Jewel
from mltd.models.schemas import JewelSchema


@dispatcher.add_method(name='JewelService.GetJewel', context_arg='context')
def get_jewel(params, context):
    """Service for getting jewel info for the user.

    Invoked in the following situations.
    1. As part of the initial batch requests after logging in.
    2. After the user spent jewels to contiune a song.
    3. When the user gives up a song or rehearsal.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'jewel', whose value is
        a single dict containing the following keys.
            free_jewel_amount: Amount of free jewels the user has.
            paid_jewel_amount: 0 (All purchased jewels are counted as
                               free jewels on overseas servers).
    """
    with Session(engine) as session:
        jewel = session.scalars(
            select(Jewel)
            .where(Jewel.user_id == UUID(context['user_id']))
        ).one()

        jewel_schema = JewelSchema()
        jewel_dict = jewel_schema.dump(jewel)

    return {'jewel': jewel_dict}

