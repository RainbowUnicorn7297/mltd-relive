import json
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timezone

from jsonrpc import dispatcher
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Course, Profile
from mltd.models.schemas import GuestSchema


@dispatcher.add_method(name='SongRankingService.GetSongRanking')
def get_song_ranking(params):
    """Service for getting the top scores for a song.

    Invoked when the user presses Ranking button on the song selection
    screen.
    Args:
        params: A dict containing the following keys.
            mst_song_id: Master song ID.
            live_course: Course (1-6).
            limit: Maximum number of scores to retrieve. This value
                   starts at 100 for the first invocation, then
                   decreases by 20 for every subsequent invocation to
                   get the next page.
                   This method always return exactly 20 scores
                   irrespective of this parameter, so this value serves
                   more as a counter for the game client to keep track
                   of how many remaining scores there are to retrieve.
            cursor: Cursor returned by the previous invocation if the
                    user has just scrolled to the bottom to get the next
                    page (an empty string if no previous cursor).
    Returns:
        A dict containing the following keys.
        song_score_list: A list of 20 dicts representing the top 20
                         scores for this song (top 21-40 and so on for
                         subsequent invocations). Each dict contain the
                         following keys.
            score: Score.
            user_summary: A dict representing the user who obtained this
                          score. See the return value 'guest_list' of
                          the method 'LiveService.GetRandomGuestList'
                          for the dict definition. 'is_friend' is always
                          false here.
        cursor: Pagination cursor for the next invocation to fetch the
                next top 20 scores.
    """
    with Session(engine) as session:
        ranking_stmt = (
            select(Course.score, Course.score_update_date, Profile)
            .join(Profile, Course.user_id == Profile.id_)
            .where(Course.mst_song_id == params['mst_song_id'])
            .where(Course.course_id == params['live_course'])
        )

        if params['cursor']:
            cursor = json.loads(urlsafe_b64decode(params['cursor']))
            last_score = cursor['score']
            last_score_update_date = datetime.fromtimestamp(
                cursor['score_update_date'], tz=timezone.utc)
            ranking_stmt = ranking_stmt.where(
                or_(Course.score < last_score,
                    and_(Course.score == last_score,
                         Course.score_update_date > last_score_update_date))
            )

        ranking_stmt = (
            ranking_stmt
            .order_by(Course.score.desc(), Course.score_update_date)
            .limit(20)
        )
        result = session.execute(ranking_stmt).all()

        song_score_list = []
        guest_schema = GuestSchema()
        for score, _, profile in result:
            user_summary = guest_schema.dump(profile)
            user_summary['is_friend'] = False
            song_score_list.append({
                'score': score,
                'user_summary': user_summary
            })

        cursor = ''
        if result:
            last_score, last_score_update_date, _ = result[-1]
            cursor_dict = {
                'score': last_score,
                'score_update_date': datetime.timestamp(
                    last_score_update_date.replace(tzinfo=timezone.utc))
            }
            cursor = urlsafe_b64encode(
                json.dumps(cursor_dict).encode()
            ).decode()

        return {
            'song_score_list': song_score_list,
            'cursor': cursor
        }

