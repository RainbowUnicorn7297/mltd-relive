from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Achievement
from mltd.models.schemas import AchievementSchema


@dispatcher.add_method(name='AchievementService.GetAchievementList',
                       context_arg='context')
def get_achievement_list(params, context):
    """Get a list of achievements for the user.

    Invoked in the following situations.
    1. When the user presses Data Download button under Navigation tab.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'achievement_list', whose
        value is a list of dicts representing the available achievements
        (both obtained and yet to be obtained) for the user. Each of
        these dicts contains the following keys.
            mst_achievement_id: Master achievement ID.
            resource_id: A string for getting achievement-related
                         resources.
            is_released: Whether this achievement has been obtained by
                         the user.
            achievement_type: Achievement type (1-3).
                              1=Normal
                              2=Idol
                              3=Event (including April Fools' Day and
                                Anniversary achievements)
            begin_date: When this achievement first became available to
                        obtain by any user on the server.
            sort_id: Sort ID.
    """
    with Session(engine) as session:
        achievements = session.scalars(
            select(Achievement)
            .where(Achievement.user_id == UUID(context['user_id']))
        ).all()

        achievement_schema = AchievementSchema()
        achievement_list = achievement_schema.dump(achievements, many=True)

    return {
        'achievement_list': achievement_list
    }

