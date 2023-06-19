from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Idol
from mltd.models.schemas import IdolSchema


@dispatcher.add_method(name='IdolService.GetIdolList', context_arg='context')
def get_idol_list(params, context):
    """Get a list of idol info for the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'idol_list', whose value is
        a list of dicts. Each of the dict represents a single idol and
        contains the following keys.
            idol_id: Unique idol ID per user per idol (user_id +
                     mst_idol_id).
            mst_idol_id: Master idol ID (1-52, 201).
            resource_id: A string for getting idol-related resources.
            idol_type: Idol type (1-3, 5).
            fan: Number of fans for this idol.
            affection: Affection value for this idol.
            tension: 100.
            is_best_condition: false.
            area: Unknown (0-7).
            offer_type: Unknown (0-4):
            mst_costume_id: 0.
            having_costume_list: A list of 'mst_costume_ids' of all
                                 unlocked costumes for this idol.
            costume_list: A list of dicts representing all unlocked
                          costumes for this idol. This list matches
                          'having_costume_list' above. See the return
                          value 'costume_list' of the method
                          'CardService.GetCardList' for the dict
                          definition.
            favorite_costume_list: null.
            voice_category_list: A list of dicts representing unlocked
                                 idol-specific voice categories
                                 (偶像特有台詞) for this idol.
                                 Contains the following keys.
                mst_voice_category_id: Master voice category ID (3001-
                                       3106).
                sort_id: Sort ID:
                idol_detail_type: 3.
                value: Required affection to unlock this voice category
                       (0 if unlocked by default).
                rarity: 0.
                label_header: 'system_storyidol'.
                voice_label: Voice label.
                release_date: '2019-08-19T13:00:00+0800'.
                mst_direction_category_id: 0.
            has_another_appeal: Whether the alternate burst appeal
                                (異色綻放) has been unlocked for this
                                idol.
            can_perform: The only case for this to be false is when the
                         user has not obtained the Ex card for Shika. In
                         all other cases, this is set to true.
            lesson_wear_list: A list of dicts representing available
                              lesson wears for this idol. Contains the
                              following keys.
                mst_lesson_wear_id: Master lesson wear ID (1-53, 90001-
                                    90052).
                mst_idol_id: Master idol ID (1-52, 201).
                mst_lesson_wear_group_id: An int representing the lesson
                                          wear group [1=Normal
                                          (訓練課程服), 9001=1st
                                          Anniversary (1週年記念)].
                costume_number: 1.
                costume_name: Unknown (tr/gs/cr).
                collabo_no: Collaboration number [0=Normal (訓練課程服),
                            1=1st Anniversary (1週年記念)].
                resource_id: A string for getting resources related to
                             this lesson wear.
                default_flag: Whether this lesson wear is the defualt.
            mst_agency_id_list: A list containing a single int
                                representing the agency of the idol
                                (1=765, 2=961).
            default_costume: A dict representing the default costume for
                             this idol. See the return value
                             'costume_list' of the method
                             'CardService.GetCardList' for the dict
                             definition.
            birthday_live: 0 for Shika, 1 for everyone else.
    """
    with Session(engine) as session:
        idols = session.scalars(
            select(Idol)
            .where(Idol.user_id == UUID(context['user_id']))
        ).all()

        idol_schema = IdolSchema()
        idol_list = idol_schema.dump(idols, many=True)

    return {'idol_list': idol_list}

