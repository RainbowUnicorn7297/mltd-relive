from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (Card, MstCard, MstLessonWear, SongUnit, Unit,
                                User)
from mltd.models.schemas import SongUnitSchema, UnitSchema


@dispatcher.add_method(name='UnitService.GetUnitList', context_arg='context')
def get_unit_list(params, context):
    """Service for getting a list of user-defined units.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'unit_list', whose value is
        a list of 18 dicts. Each of the dict represents a single unit
        and contains the following keys.
            unit_num: Unit number (1-18).
            name: Unit name.
            idol_list: A list of 5 dicts representing the selected cards
                       and costumes. The order of this list is
                       important. The first dict in this list represents
                       the center of the unit. Each dict contains the
                       following keys.
                card_id: Card ID (user_id + mst_card_id) of the selected
                         card.
                mst_costume_id: Master costume ID of the selected
                                costume.
                mst_lesson_wear_id: Master lesson wear ID of the
                                    selected idol.
                costume_is_random: Whether the costume is randomly
                                   selected for each live performance.
                costume_random_type: 0.
    """
    with Session(engine) as session:
        units = session.scalars(
            select(Unit)
            .where(Unit.user_id == UUID(context['user_id']))
            .order_by(Unit.unit_num)
        ).all()

        unit_schema = UnitSchema()
        unit_list = unit_schema.dump(units, many=True)

    return {'unit_list': unit_list}


@dispatcher.add_method(name='UnitService.SetUnit', context_arg='context')
def set_unit(params, context):
    """Service for setting one or more units for a user.

    Invoked when the user makes changes to one or more units on the unit
    confirmation screen under Live tab or on the unit formation screen
    under Idols tab.
    Args:
        params: A dict containing a single key 'param_list', whose value
                is a list of dicts representing the changed units. Each
                of these dicts contain the following keys.
            unit_num: Unit number (1-18).
            card_id_list: A list of 5 card IDs representing the 5 cards
                          selected by the user. The order of this list
                          is important. The first card ID in this list
                          is the center of this unit.
            mst_costume_id_list: A list of 5 master costume IDs
                                 representing the costumes selected by
                                 the user for each card in
                                 'card_id_list' above.
            costume_is_random_list: A list of 5 bools representing
                                    whether random costume is selected
                                    by the user for each card in
                                    'card_id_list' above.
            costume_random_type_list: An empty list.
            mst_lesson_wear_id_list: A list of 5 master lesson wear IDs
                                     representing the lesson wears
                                     selected by the user for each card
                                     in 'card_id_list' above (an empty
                                     list if the changes were made under
                                     Idols tab).
            name: Unit name.
    Returns:
        A dict containing the following keys.
        unit_list: A list of dicts representing the units after applying
                   the changes. The length of this list is the same as
                   the length of 'param_list' above. See the return
                   value 'unit_list' of the method
                   'UnitService.GetUnitList' for the dict definition.
        mission_process: Empty info. See the implementation below.
        mission_list: An empty list.
    """
    with Session(engine) as session:
        user = session.scalars(
            select(User)
            .where(User.user_id == UUID(context['user_id']))
        ).one()

        card_ids = set()
        for p in params['param_list']:
            for i in range(5):
                card_ids.add(p['card_id_list'][i])
        card_to_idol = {}
        result = session.execute(
            select(Card.card_id, MstCard.mst_idol_id)
            .join(MstCard)
            .where(Card.user == user)
            .where(Card.card_id.in_(card_ids))
        )
        for card_id, idol_id in result:
            card_to_idol[card_id] = idol_id

        units = []
        for p in params['param_list']:
            unit_num: int = p['unit_num']
            unit = user.units[unit_num-1]
            unit.name = p['name']
            for i in range(5):
                idol = unit.unit_idols[i]
                if idol.card_id != p['card_id_list'][i]:
                    idol.card_id = p['card_id_list'][i]
                    idol.mst_lesson_wear_id = card_to_idol[idol.card_id]
                idol.mst_costume_id = p['mst_costume_id_list'][i]
                idol.costume_is_random = p['costume_is_random_list'][i]
                if p['mst_lesson_wear_id_list']:
                    idol.mst_lesson_wear_id = p['mst_lesson_wear_id_list'][i]
            units.append(unit)

        unit_schema = UnitSchema()
        unit_list = unit_schema.dump(units, many=True)

        session.commit()

    return {
        'unit_list': unit_list,
        'mission_process': {
            'complete_mission_list': [],
            'open_mission_list': [],
            'training_point_diff': {
                'before': 0,
                'after': 0,
                'total': 0
            }
        },
        'mission_list': []
    }


@dispatcher.add_method(name='UnitService.GetSongUnitList',
                       context_arg='context')
def get_song_unit_list(params, context):
    """Service for getting a list of song units.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing a single key named 'song_unit_list', whose
        value is a list of dicts, each representing a single song unit.
        Each dict contains the following keys.
            mst_song_id: Master song ID.
            unit_song_type: Unit song type (1=normal, 2=13 idols).
            idol_list: A list of 5 or 13 dicts (depending on unit song
                       type) representing the selected cards and
                       costumes. The order of this list is important.
                       The first dict in this list represents the center
                       of the unit. See the return value 'idol_list' of
                       the method 'UnitService.GetUnitList' for the dict
                       definition.
            is_new: Whether the user has never made any changes to this
                    song unit.
    """
    with Session(engine) as session:
        song_units = session.scalars(
            select(SongUnit)
            .where(SongUnit.user_id == UUID(context['user_id']))
        ).all()

        song_unit_schema = SongUnitSchema()
        song_unit_list = song_unit_schema.dump(song_units, many=True)

    return {'song_unit_list': song_unit_list}


@dispatcher.add_method(name='UnitService.SetSongUnit', context_arg='context')
def set_song_unit(params, context):
    """Service for setting a song unit for a user.

    Invoked when the user makes changes to a song unit on the unit
    confirmation screen under Live tab.
    Args:
        params: A dict containing the following keys.
            mst_song_id: Master song ID.
            card_id_list: A list of 5 or 13 card IDs (depending on unit
                          song type) representing the cards selected by
                          the user. The order of this list is important.
                          The first card ID in this list is the center
                          of this unit.
            mst_costume_id_list: A list of 5 or 13 master costume IDs
                                 representing the costumes selected by
                                 the user for each card in
                                 'card_id_list' above.
            costume_is_random_list: A list of 5 or 13 bools representing
                                    whether random costume is selected
                                    by the user for each card in
                                    'card_id_list' above.
            costume_random_type_list: An empty list.
            mst_lesson_wear_id_list: A list of 5 or 13master lesson wear
                                     IDs representing the lesson wears
                                     selected by the user for each card
                                     in 'card_id_list' above.
    Returns:
        A dict containing a single key named 'song_unit', whose value is
        a dict representing the song unit after applying the changes.
        See the return value 'song_unit_list' of the method
        'UnitService.GetSongUnitList' for the dict definition.
    """
    with Session(engine) as session:
        song_unit = session.scalars(
            select(SongUnit)
            .where(SongUnit.user_id == UUID(context['user_id']))
            .where(SongUnit.mst_song_id == params['mst_song_id'])
        ).one()
        song_unit.is_new = False

        n = len(params['card_id_list'])
        for i in range(n):
            idol = song_unit.song_unit_idols[i]
            idol.card_id = params['card_id_list'][i]
            idol.mst_costume_id = params['mst_costume_id_list'][i]
            idol.costume_is_random = params['costume_is_random_list'][i]
            idol.mst_lesson_wear_id = params['mst_lesson_wear_id_list'][i]

        song_unit_schema = SongUnitSchema()
        song_unit_dict = song_unit_schema.dump(song_unit)

        session.commit()

    return {'song_unit': song_unit_dict}

