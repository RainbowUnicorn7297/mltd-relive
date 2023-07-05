import random
from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, contains_eager

from mltd.models.engine import engine
from mltd.models.models import (Idol, MstIdol, MstOffer, MstOfferText, Offer,
                                OfferSummary, OfferText)
from mltd.models.schemas import OfferSchema


@dispatcher.add_method(name='OfferService.GetOfferList', context_arg='context')
def get_offer_list(params, context):
    """Service for getting a list of offers for a user.

    Invoked after logging in.
    A new list of offers is created each day according to the following
    rules.
    1. Number of new offers = available slots * 10.
    2. New offers cannot be selected from ongoing offers in existing
       slots.
    3. Each idol can appear at most once as the required idol in all of
       the new offers.
    4. One of the new offers is a recommended offer.
        a. Either the required idol or the recommended idol of the
           recommended offer is the idol which has the most number of
           fans and still has unread offer text. If all offer text are
           read for all idols, the required/recommended idols are
           selected at random.
        b. If there are unread text for any of the offers matching rule
           4.a, one of them will be selected as the recommended offer.
           Otherwise, the recommended offer is selected at random.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        concurrency_max_count: Maximum number of concurrent offers (aka
                               slots). Each user starts with one slot.
                               When 20 offers have been completed,
                               number of slots is increased to 2. When
                               60 offers have been completed, number of
                               slots is increased to 3.
        offer_list: A list of dicts representing the new offers created
                    each day and ongoing offers in existing slots (if
                    any). Each dict contains the following keys.
            mst_offer_id: Master offer ID.
            mst_event_id: 0.
            resource_id: A string for getting offer-related resources.
            resource_logo_id: ''.
            require_time: Required time to complete the offer in minutes
                          (180).
            mst_offer_type: 1.
            main_idol_id: Master idol ID of the required idol for this
                          offer.
            recommended_idol_id_list: A list containing exactly one
                                      master idol ID representing the
                                      recommended idol for this offer.
            parameter_type: Parameter type.
                            1 = Vocal
                            2 = Dance
                            3 = Visual
                            4 = All
            border_value: Target value for the parameter type.
            slot: For an ongoing offer, this is the slot number this
                  offer is in (1-3). Otherwise, this value is 0.
            status: For an ongoing offer, this is the status of this
                    offer (1=in progress, 2=completed). Otherwise, this
                    value is 0.
            start_date: Date when this offer was started
                        ('0001-01-01T00:00:00+0000' for new offers).
            card_list: A list of dicts representing the cards selected
                       for this ongoing offer (null for new offers). See
                       the return value 'card_list' of the method
                       'CardService.GetCardList' for the dict
                       definition.
            is_recommended: Whether this is a recommended offer.
            is_text_completed: Whether the user has read the offer text
                               for this offer.
    """
    user_id = UUID(context['user_id'])
    with Session(engine) as session:
        concurrency_max_count = session.scalars(
            select(OfferSummary.concurrency_max_count)
            .where(OfferSummary.user_id == user_id)
        ).one()

        new_offers = session.scalars(
            select(Offer)
            .where(Offer.user_id == user_id)
            .where(Offer.slot == 0)
        ).all()
        ongoing_offers = session.scalars(
            select(Offer)
            .where(Offer.user_id == user_id)
            .where(Offer.slot != 0)
        ).all()

        if not new_offers:
            # Select the recommended offer.
            recommended_offer_id = None
            unread_text_subq = (
                select(OfferText.mst_offer_text_id)
                .join(OfferText.mst_offer_text)
                .options(contains_eager(OfferText.mst_offer_text))
                .where(OfferText.user_id == Idol.user_id)
                .where(or_(MstOfferText.idol_id == Idol.mst_idol_id,
                           MstOfferText.to_idol_id == Idol.mst_idol_id))
                .where(OfferText.acquired == False)
            ).exists()
            recommended_idol_id = session.scalar(
                select(Idol.mst_idol_id)
                .where(Idol.user_id == user_id)
                .where(unread_text_subq)
                .order_by(Idol.fan.desc())
                .limit(1)
            )
            if recommended_idol_id:
                unread_offer_ids = session.scalars(
                    select(MstOffer)
                    .join(MstOfferText)
                    .join(OfferText, and_(OfferText.user_id == user_id,
                                          OfferText.mst_offer_text_id
                                          == MstOfferText.mst_offer_text_id))
                    .where(or_(MstOffer.main_idol_id == recommended_idol_id,
                               MstOffer.recommended_idol_id_list
                               == recommended_idol_id))
                    .where(~MstOffer.mst_offer_id.in_([
                        offer.mst_offer_id for offer in ongoing_offers]))
                    .where(OfferText.acquired == False)
                ).all()
                if unread_offer_ids:
                    recommended_offer_id = random.choice(unread_offer_ids)
            if not recommended_offer_id:
                allowed_offer_stmt = (
                    select(MstOffer.mst_offer_id)
                    .where(~MstOffer.mst_offer_id.in_([
                        offer.mst_offer_id for offer in ongoing_offers]))
                )
                if recommended_idol_id:
                    allowed_offer_stmt = allowed_offer_stmt.where(
                        or_(MstOffer.main_idol_id == recommended_idol_id,
                            MstOffer.recommended_idol_id_list
                            == recommended_idol_id))
                allowed_offer_ids = session.scalars(allowed_offer_stmt).all()
                recommended_offer_id = random.choice(allowed_offer_ids)
            session.add(Offer(
                user_id=user_id,
                mst_offer_id=recommended_offer_id,
                is_recommended=True
            ))

            # Select remaining new offers.
            recommended_offer_idol_subq = (
                select(MstOffer.main_idol_id)
                .where(MstOffer.mst_offer_id == recommended_offer_id)
                .scalar_subquery()
            )
            allowed_idol_ids = session.scalars(
                select(MstIdol.mst_idol_id)
                .where(MstIdol.mst_agency_id == 1)
                .where(MstIdol.mst_idol_id != recommended_offer_idol_subq)
            ).all()
            selected_idol_ids = random.sample(allowed_idol_ids,
                                              concurrency_max_count*10-1)
            result = session.execute(
                select(MstOffer.main_idol_id, MstOffer.mst_offer_id)
                .where(MstOffer.mst_offer_id != recommended_offer_id)
                .where(~MstOffer.mst_offer_id.in_([
                    offer.mst_offer_id for offer in ongoing_offers]))
                .where(MstOffer.main_idol_id.in_(selected_idol_ids))
            )
            idol_dict = {idol_id: [] for idol_id in selected_idol_ids}
            for main_idol_id, mst_offer_id in result:
                idol_dict[main_idol_id].append(mst_offer_id)
            for idol_id in selected_idol_ids:
                session.add(Offer(
                    user_id=user_id,
                    mst_offer_id=random.choice(idol_dict[idol_id]),
                    is_recommended=False
                ))

            session.commit()

            new_offers = session.scalars(
                select(Offer)
                .where(Offer.user_id == user_id)
                .where(Offer.slot == 0)
            ).all()

        offer_list = []
        offer_schema = OfferSchema()
        offer_list.extend(offer_schema.dump(new_offers, many=True))
        offer_list.extend(offer_schema.dump(ongoing_offers, many=True))

    return {
        'concurrency_max_count': concurrency_max_count,
        'offer_list': offer_list
    }

