from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import RecordTime, User
from mltd.models.schemas import RecordTimeSchema, UserSchema


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


@dispatcher.add_method(name='UserService.GetRecordTimeList',
                       context_arg='context')
def get_record_time_list(params, context):
    """Service for getting a list of recorded times for user actions.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'record_time_list', whose
        value is a list of dicts representing the recorded time for
        each action previously performed by the user (such as finished
        reading a tutorial). Each dict contains the following keys.
            kind: A string representing the kind of action performed.
            time: The time when the user performed this action.
    """
    with Session(engine) as session:
        record_times = session.scalars(
            select(RecordTime)
            .where(RecordTime.user_id == UUID(context['user_id']))
        ).all()

        record_time_schema = RecordTimeSchema()
        record_time_list = record_time_schema.dump(record_times, many=True)
        if not record_times:
            record_time_list = None

    return {'record_time_list': record_time_list}

