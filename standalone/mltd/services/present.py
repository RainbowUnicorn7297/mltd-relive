from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Present


@dispatcher.add_method(name='PresentService.GetPresentCount',
                       context_arg='context')
def get_present_count(params, context):
    """Service for getting number of presents for a user.

    Invoked as part of the initial batch requests after logging in.
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
        )

    return min(value, 100)

