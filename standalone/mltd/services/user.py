from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import User
from mltd.models.schemas import UserSchema


@dispatcher.add_method(name='UserService.GetSelf', context_arg='context')
def get_self(params, context):
    """Service for getting self user info.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
            
    Returns:
        A dict containing user info. See the return value 'user' of
        AuthService.Login method for the definition.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()

        user_schema = UserSchema()
        user_dict = user_schema.dump(user)

    return user_dict

