from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Campaign
from mltd.models.schemas import CampaignSchema


@dispatcher.add_method(name='CampaignService.GetCampaignList',
                       context_arg='context')
def get_campaign_list(params, context):
    """Service for getting a list of campaigns for the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'campaign_list', whose
        value is a list of dicts. Each of the dict represents a single
        campaign and contains the following keys.
            mst_campain_id: Master campaign ID.
            type: Campaign type.
            value: 0.
            footer_button: A list containing a single int representing
                           the footer button.
            start_date: Campaign start date.
            end_date: Capmaign end date.
    """
    with Session(engine) as session:
        campaigns = session.scalars(
            select(Campaign)
            .where(Campaign.user_id == UUID(context['user_id']))
        ).all()

        campaign_schema = CampaignSchema()
        campaign_list = campaign_schema.dump(campaigns, many=True)

    return {'campaign_list': campaign_list}

