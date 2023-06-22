from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import MstJob
from mltd.models.schemas import MstJobSchema


@dispatcher.add_method(name='JobService.GetJobList')
def get_job_list(params):
    """Service for getting a list of jobs.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
            job_list: A list of dicts representing available jobs. Each
                      dict contains the following keys.
                mst_job_id: Master job ID.
                resource_id: A string for getting job-related resources.
                vitality_cost: Vitality cost (20).
                job_type: 1.
                idol_type: Job idol type (1-4).
                reward_exp: User EXP rewarded (143).
                reward_fan: Number of fans gained by the idol randomly
                            picked for the job (40).
                reward_affection: Affection value gained by the idol
                                  (9).
                reward_money: Money rewarded (630).
                reward_live_ticket: Number of live tickets rewarded
                                    (20).
                begin_date: Date when this job becomes available.
                end_date: Date when this job becomes unavailable.
            job_special_list: null.
    """
    with Session(engine) as session:
        mst_jobs = session.scalars(
            select(MstJob)
        ).all()

        mst_job_schema = MstJobSchema()
        mst_job_list = mst_job_schema.dump(mst_jobs, many=True)

    return {
        'job_list': mst_job_list,
        'job_special_list': None
    }

