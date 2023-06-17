from jsonrpc import dispatcher
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import Item
from mltd.models.schemas import ItemSchema


@dispatcher.add_method(name='ItemService.GetItemList', context_arg='context')
def get_item_list(params, context):
    """Service for getting items obtained by the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: A dict containing the following key.
            cursor: An empty string.
    Returns:
        A dict containing a single key named 'item_list', whose value is
        a list of dicts. Each of the dict represents a single type of
        item and contains the following keys.
            item_id: Unique item ID per user per item (user_id +
                     mst_item_id).
            mst_item_id: Master item ID (0-9712).
            name: Item name.
            item_navi_type: An int representing the item navigation
                            type.
                            0=Others (money, memory piece, anniversary
                                idol-specific piece)
                            1=Vitality recovery item (spark drink,
                                macaron, present from idol)
                            2=Awakening item
                            3=Lesson ticket
                            4=Master rank item (including PST piece)
                            5=Gacha ticket/medal
                            6=Live item (live ticket, auto live pass,
                                singing voice master key)
                            7=Gift for affection
                            8=Gift for awakening gauge
            amount: Amount of this item the user has.
            max_amount: Maximum possible amount of this item.
            item_type: An int representing the item type.
                2=Money
                3=Live ticket
                5=Gacha ticket/medal
                6=Vitality recovery item
                7=Awakening item
                8=Lesson ticket
                9=Master rank item
                13=Selection ticket/Platinum selection ticket/
                    Platinum SR selection ticket
                17=Memory piece
                18=PST piece
                19=FES master piece
                22=Anniversary idol-specific piece
                23=Auto live pass
                25=Gift for affection
                26=Gift for awakening gauge
                27=Singing voice master key
            sort_id: Sort ID.
            value1, value2: These two ints together represents the item
                            values with different meanings for different
                            item types.
                            For vitality recovery items, value1 is the
                            amount of vitality recovered by consuming
                            the item. value2 is the % of vitality
                            recovered.
                                Spark drink 10: value1=10, value2=0
                                Spark drink 20: value1=20, value2=0
                                Spark drink 30: value1=30, value2=0
                                Spark drink MAX (and other equivalent
                                    items): value1=0, value2=100
                            For lesson tickets, value1 is the amount of
                            card exp gained by consuming the ticket.
                            value2 is the card skill "exp" that is used
                            to calculate the probability of leveling up
                            the card skill.
                                Lesson ticket N: value1=800, value2=0
                                Lesson ticket R: value1=2500,
                                    value2=300
                                Lesson ticket SR: value1=4000,
                                    value2=1000
                                Lesson ticket SSR: value1=5000,
                                    value2=2000
                            For gifts used to increase idol affection,
                            value1 is the amount of affection increased
                            by consuming the gift. value2 has no
                            meaning.
                                Throat lozenge: value1=50, value2=0
                                Tapioca drink: value1=100, value2=0
                                High cocoa chocolate: value1=150,
                                    value2=0
                                Roll cake: value1=200, value2=0
                            For gifts used to increase card awakening
                            gauge, value1 is the amount of awakening
                            gauge increased by consuming the gift.
                            value2 has no meaning.
                                Fan letter: value1=10, value2=0
                                Single flower: value1=20, value2=0
                                Hand cream: value1=30, value2=0
                                Bath additive: value1=40, value2=0
                                Preserved flower: value1=50, value2=0
                            For money, value1 represents the amount of
                            money gained by obtaining this item. value2
                            has no meaning.
            expire_date: Expire date of the item (null if is_extend is
                         true).
            expire_date_list: If is_extend is false, this is an empty
                              list. Otherwise, this is a list of expire
                              dates for each individual time-limited
                              ticket (null is amount is 0).
            is_extend: true for some Platinum/Selection/SSR tickets,
                       false for everything else.
    """
    with Session(engine) as session:
        items = session.scalars(
            select(Item)
            .where(Item.user_id == UUID(context['user_id']))
        ).all()

        item_schema = ItemSchema()
        item_list = item_schema.dump(items, many=True)

    return {'item_list': item_list}
