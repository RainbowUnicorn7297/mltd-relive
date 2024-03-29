from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Card, MstCard, MstCostume, User
from mltd.models.schemas import AlbumSchema, CardSchema, MstCostumeSchema


def add_card(session: Session, user: User, mst_card_id):
    """Give a new card to a user.

    Args:
        session: Existing SQLAlchemy session.
        user: A User object.
        mst_card_id: Master card ID.
    Returns:
        None.
    """
    mst_card = session.scalar(
        select(MstCard)
        .where(MstCard.mst_card_id == mst_card_id)
    )
    level_max = mst_card.level_max
    vocal_base = mst_card.vocal_base
    dance_base = mst_card.dance_base
    visual_base = mst_card.visual_base
    vocal_max = mst_card.vocal_max
    dance_max = mst_card.dance_max
    visual_max = mst_card.visual_max
    card = Card(
        card_id=f'{user.user_id}_{mst_card_id}',
        mst_card_id=mst_card_id,
        vocal_diff=vocal_max / (2*level_max),
        dance_diff=dance_max / (2*level_max),
        visual_diff=visual_max / (2*level_max),
        skill_probability=(None if not mst_card.mst_card_skill_id
                           else mst_card.mst_card_skill.probability_base + 1),
    )
    card.before_awakened_vocal = vocal_base + round(card.vocal_diff)
    card.before_awakened_dance = dance_base + round(card.dance_diff)
    card.before_awakened_visual = visual_base + round(card.visual_diff)
    card.after_awakened_vocal = vocal_base + round(
        card.vocal_diff + vocal_max*10/(2*level_max*level_max))
    card.after_awakened_dance = dance_base + round(
        card.dance_diff + dance_max*10/(2*level_max*level_max))
    card.after_awakened_visual = visual_base + round(
        card.visual_diff + visual_max*10/(2*level_max*level_max))
    card.vocal = card.before_awakened_vocal
    card.dance = card.before_awakened_dance
    card.visual = card.before_awakened_visual
    user.cards.append(card)


@dispatcher.add_method(name='CardService.GetCardList', context_arg='context')
def get_card_list(params, context):
    """Get a list of cards obtained by the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'card_list', whose value is
        a list of dicts. Each of the dict represents a single card and
        contains the following keys.
            card_id: Unique card ID per user per card (user_id +
                     mst_card_id).
            mst_card_id: Master card ID (1-686, 9001-9003).
            mst_idol_id: Master idol ID (1-52, 201).
            mst_costume_id: Master costume ID associated with the card
                            (0 if none).
            bonus_costume_id: Master costume ID of the bonus costume
                              associated with the card (0 if none).
            rank5_costume_id: Master costume ID of the master rank 5
                              costume associated with the card (0 if
                              none).
            resource_id: A string for getting card-related resources.
            rarity: An int representing the rarity of the card (1=N,
                    2=R, 3=SR, 4=SSR).
            idol_type: An int (1 to 4) representing the card's idol type
                       (Princess/Fairy/Angel/All).
            exp: Current card experience.
            level: Current card level.
            level_max: Maximum possible level of the card. Depends on
                       both the rarity of the card and whether the card
                       is awakened.
            life: Life value.
            vocal: Current vocal value. Depends on card level.
            vocal_base: Vocal base value. This value represents the
                        vocal value the card would have if the card was
                        at level 0 (hypothetically speaking since the
                        minimum level an actual card can have is 1), was
                        not awakened, and was at master rank 0.
            vocal_diff: Additional vocal value gained per level. Depends
                        on both the rarity of the card and whether the
                        card is awakened.
            vocal_max: Maximum possible vocal value. This value
                       represents the vocal value the card will have if
                       the card is at max level, is awakened, and is at
                       master rank 0.
            vocal_master_bonus: Bonus vocal value gained per master
                                rank. Depends on vocal_max.
            dance: Current dance value.
            dance_base: Dance base value.
            dance_diff: Additional dance value gained per level.
            dance_max: Maximum possible dance value.
            dance_master_bonus: Bonus dance value gained per master
                                rank.
            visual: Current visual value.
            visual_base: Visual base value.
            visual_diff: Additional visual value gained per level.
            visual_max: Maximum possible visual value.
            visual_master_bonus: Bonus visual value gained per master
                                 rank.
            before_awakened_params: A dict representing the current
                                    values of the card if it is not
                                    awakened, based on the card's
                                    current level and master rank.
                                    Contains the following keys.
                life: Before awakened life value. Same as after awakened
                      life value.
                vocal: Before awakened vocal value.
                dance: Before awakened dance value.
                visual: Before awakened visual value.
            after_awakened_params: A dict representing the current
                                   values of the card if it is awakened,
                                   based on the card's current level and
                                   master rank. Contains the same keys
                                   as 'before_awakened_params' with
                                   after awakened values.
            skill_level: Current skill level.
            skill_level_max: Maximum possible skill level. This value is
                             12 only if the card has been trained to
                             master rank 5. Otherwise, this value is 10.
            is_awakened: Whether the card is awakened.
            awakening_gauge: Current awakening gauge value.
            awakening_gauge_max: Maximum possible awakening gauge value.
                                 Depends on the rarity of the card.
            master_rank: Current master rank.
            master_rank_max: Maximum possible master rank.
            cheer_point: 0.
            center_effect: A dict representing the center effect of the
                           card. Contains the following keys. If the
                           card has no center effect, all values are set
                           to 0.
                mst_center_effect_id: Center effect ID.
                effect_id: 1 (unless no center effect).
                idol_type: Center skill target idol type (1=Princess,
                           2=Fairy, 3=Angel, 4=All types).
                specific_idol_type: Center skill requirements on unit
                                    idol type.
                                    0=No requirements
                                    1=Princess unicolor
                                    2=Fairy unicolor
                                    3=Angel unicolor
                                    4=Tricolor
                attribute: Center skill effect (1=Vocal %, 2=Dance %,
                           3=Visual %, 4=All appeals %, 5=Life %,
                           6=Skill probability %).
                value: Amount of % increase.
                song_idol_type: 0.
                attribute2: 0.
                value2: 0.
            card_skill_list: Either a list containing exactly one dict
                             representing the card skill, or null if the
                             card has no skill. The dict (if present)
                             contains the following keys.
                mst_card_skill_id: Card skill ID.
                effect_id: Effect type (1=Score bonus, 2=Combo bonus,
                           3=Healer, 4=Life guard, 5=Combo guard,
                           6=Perfect lock, 7=Double boost, 8=Multi up,
                           10=Overclock).
                duration: Skill duration.
                evaluation: Required note types for triggering the
                            effect during skill activation.
                            0=N/A
                            1=Perfect
                            2=Perfect/Great
                            3=Great
                            4=Great/Good/Fast/Slow
                            6=Fast/Slow
                            7=Great/Good
                evaluation2: Required note types for triggering the 2nd
                             effect during skill activation (0 if no 2nd
                             effect).
                interval: The interval between each skill activation.
                probability: Probability of skill activation in %.
                             Depends on the card's skill level.
                value: % or value increase for the effect.
                value2: % or value increase for the 2nd effect (0 if no
                        2nd effect).
            ex_type: Extra type [0=Normal, 2=PST (Ranking),
                     3=PST (Event Pt), 4=FES, 5=1st, 6=Ex, 7=2nd].
            create_date: Date when the user obtained this card.
            variation: Unknown (1-16).
            master_lesson_begin_date: For a PST card, this is the date
                                      when master lessons become
                                      available (usually around 6 months
                                      after its corresponding event).
                                      For any other card, this date is
                                      set to '0001-01-01T00:00:00+0000'.
            training_item_list: null.
            begin_date: Date when the card was released on the server
                        and became available for any user to obtain.
            sort_id: Sort ID.
            is_new: Whether the card is new to the user. For a newly
                    registered user, all cards are new except the five
                    cards in the default unit.
            costume_list: A nullable list of dicts representing costumes
                          associated with this card. This list matches
                          the costume IDs above. Each dict contains the
                          following keys.
                mst_costume_id: Master costume ID.
                mst_idol_id: Master idol ID.
                resource_id: A string for getting costume-related
                             resources.
                mst_costume_group_id: Unknown (0-993).
                costume_name: Unknown (-/ex/ss/sr/gs).
                costume_number: Unknown (0-601).
                exclude_album: Whether to exclude the costume from the
                               costume album. True only if this is a 2nd
                               anniversary costume with butterfly wings.
                exclude_random: false.
                collabo_number: 0.
                replace_group_id: Unknown (0, 4-6).
                sort_id: Sort ID.
                release_date: Date when the costume was released.
                gorgeous_appeal_type: This value is 1 only if this is a
                                      master rank 5 costume. Otherwise,
                                      this value is 0.
            card_category: Unknown (10-35).
            extend_card_params: A dict representing card values for
                                an anniversary card after training it to
                                SSR. For any other card, all values are
                                set to 0. Contains the following keys.
                level_max: Maximum possible level after becoming SSR.
                life: Life value after becoming SSR.
                vocal_max: Maximum possible vocal value after becoming
                           SSR.
                vocal_master_bonus: Bonus vocal value gained per master
                                    rank after becoming SSR.
                dance_max: Maximum possible dance value after becoming
                           SSR.
                dance_master_bonus: Bonus dance value gained per master
                                    rank after becoming SSR.
                visual_max: Maximum possible visual value after becoming
                            SSR.
                visual_master_bonus: Bonus visual value gained per
                                     master rank after becoming SSR.
            is_master_lesson_five_available: Whether master rank 5 is
                                             available.
            barrier_mission_list: An empty list.
            training_point: 0.
            sign_type: 0.
            sign_type2: 0.
    """
    with Session(engine) as session:
        cards = session.scalars(
            select(Card)
            .where(Card.user_id == UUID(context['user_id']))
        ).all()

        card_schema = CardSchema()
        card_list = card_schema.dump(cards, many=True)

    return {'card_list': card_list}


@dispatcher.add_method(name='CardService.GetAlbumList', context_arg='context')
def get_album_list(params, context):
    """Get the card and costume albums of the user.

    Invoked in the following situations.
    1. When the user presses Cards/Costumes button under Idols tab.
    2. When the user presses Data Download button under Navigation tab.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        album_list: A list of dicts representing the states of each card
                    within the card album of the user. Each of these
                    dicts contains the following keys.
            mst_card_id: Master card ID.
            mst_idol_id: Master idol ID.
            sort_id: Sort ID.
            is_awakened: Whether the card is awakened. Each master card
                         ID corresponds to exactly two dicts in this
                         list; one with 'is_awakened' set to False, one
                         with 'is_awakened' set to True.
            is_released: If 'is_awakened' is False, this flag represents
                         whether the user has obtained this card. If
                         'is_awakened' is True, this flag is True only
                         if the user has obtained this card and this
                         card is awakened.
            rarity: An int representing the rarity of the card (1=N,
                    2=R, 3=SR, 4=SSR).
            attribute: Center skill effect of the card (1=Vocal %,
                       2=Dance %, 3=Visual %, 4=All appeals %, 5=Life %,
                       6=Skill probability %).
            effect_id_list: A list containing exactly two ints. The
                            first int is the effect type of the card
                            skill of this card (0 if this card has no
                            skill). The second int is always 0.
                            1=Score bonus
                            2=Combo bonus
                            3=Healer
                            4=Life guard
                            5=Combo guard
                            6=Perfect lock
                            7=Double boost
                            8=Multi up
                            10=Overclock
            mst_center_effect_id: Center effect ID of the card.
            begin_date: Date when the card was released on the server
                        and became available for any user to obtain.
            ex_type: Extra type [0=Normal, 2=PST (Ranking),
                     3=PST (Event Pt), 4=FES, 5=1st, 6=Ex, 7=2nd].
            resource_id: A string for getting card-related resources.
        costume_list: A list of dicts representing all costumes. See the
                      return value 'costume_list' of the method
                      'CardService.GetCardList' for the dict definition.
    """
    with Session(engine) as session:
        mst_cards = session.scalars(
            select(MstCard)
        ).all()

        owned_card_ids = session.scalars(
            select(Card.mst_card_id)
            .where(Card.user_id == UUID(context['user_id']))
        ).all()
        awakened_card_ids = session.scalars(
            select(Card.mst_card_id)
            .where(Card.user_id == UUID(context['user_id']))
            .where(Card.is_awakened == True)
        ).all()

        album_schema = AlbumSchema()
        owned_album_list = album_schema.dump(mst_cards, many=True)
        for card in owned_album_list:
            card['is_awakened'] = False
            card['is_released'] = card['mst_card_id'] in owned_card_ids
        awakened_album_list = album_schema.dump(mst_cards, many=True)
        for card in awakened_album_list:
            card['is_awakened'] = True
            card['is_released'] = card['mst_card_id'] in awakened_card_ids
        album_list = owned_album_list
        album_list.extend(awakened_album_list)

        mst_costumes = session.scalars(
            select(MstCostume)
        ).all()

        mst_costume_schema = MstCostumeSchema()
        costume_list = mst_costume_schema.dump(mst_costumes, many=True)

    return {
        'album_list': album_list,
        'costume_list': costume_list
    }

