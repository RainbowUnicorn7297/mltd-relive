from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import GashaMedal
from mltd.models.schemas import GashaMedalSchema


@dispatcher.add_method(name='GashaMedalService.GetGashaMedal',
                       context_arg='context')
def get_gasha_medal(params, context):
    """Service for getting gasha medal info for the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        gasha_medal: A dict containing the following keys.
            point_amount: Amount of gacha medal points the user
                          currently owns (10 points = 1 medal).
            expire_date_list: A list of strs. Each str represents the
                              expire date of a gasha medal. The length
                              of this list is equal to the number of
                              gasha medals the user currently owns.
        gasha_medal_max: Maximum possible number of gacha medals a user
                         can own (10).
    """
    with Session(engine) as session:
        gasha_medal = session.scalars(
            select(GashaMedal)
            .where(GashaMedal.user_id == UUID(context['user_id']))
        ).one()

        gasha_medal_schema = GashaMedalSchema()
        gasha_medal_dict = gasha_medal_schema.dump(gasha_medal)

    return {
        'gasha_medal': gasha_medal_dict,
        'gasha_medal_max': 10
    }

