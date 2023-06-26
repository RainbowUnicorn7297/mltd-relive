from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Unit
from mltd.models.schemas import UnitSchema


@dispatcher.add_method(name='UnitService.GetUnitList', context_arg='context')
def get_unit_list(params, context):
    """Service for getting a list of user-defined units.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'unit_list', whose value is
        a list of 18 dicts. Each of the dict represents a single unit
        and contains the following keys.
            unit_num: Unit number (1-18).
            name: Unit name.
            idol_list: A list of 5 dicts representing the selected cards
                       and costumes. The order of this list is
                       important. The first dict in this list represents
                       the center of the unit. Each dict contains the
                       following keys.
                card_id: Card ID (user_id + mst_card_id) of the selected
                         card.
                mst_costume_id: Master costume ID of the selected
                                costume.
                mst_lesson_wear_id: Master lesson wear ID of the
                                    selected idol.
                costume_is_random: Whether the costume is randomly
                                   selected for each live performance.
                costume_random_type: 0.
    """
    with Session(engine) as session:
        units = session.scalars(
            select(Unit)
            .where(Unit.user_id == UUID(context['user_id']))
            .order_by(Unit.unit_num)
        ).all()

        unit_schema = UnitSchema()
        unit_list = unit_schema.dump(units, many=True)

    return {'unit_list': unit_list}

