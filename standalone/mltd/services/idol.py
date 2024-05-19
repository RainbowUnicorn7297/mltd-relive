from uuid import UUID

from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (CostumeAdv, Episode, Idol, Memorial,
                                MstCostumeBulkChangeGroup)
from mltd.models.schemas import (CostumeAdvSchema, EpisodeSchema, IdolSchema,
                                 MemorialSchema,
                                 MstCostumeBulkChangeGroupSchema)
from mltd.servers.i18n import translation

_ = translation.gettext


def localize_character_name(mst_character_id):
    """Get the localized name for a character.

    Args:
        mst_character_id: Master character ID (1-52, 201).
    Returns:
        A str representing the localized name of the character.
    """
    if mst_character_id <= 52:
        return [
            '',
            _('Haruka Amami'),
            _('Chihaya Kisaragi'),
            _('Miki Hoshii'),
            _('Yukiho Hagiwara'),
            _('Yayoi Takatsuki'),
            _('Makoto Kikuchi'),
            _('Iori Minase'),
            _('Takane Shijou'),
            _('Ritsuko Akizuki'),
            _('Azusa Miura'),
            _('Ami Futami'),
            _('Mami Futami'),
            _('Hibiki Ganaha'),
            _('Mirai Kasuga'),
            _('Shizuka Mogami'),
            _('Tsubasa Ibuki'),
            _('Kotoha Tanaka'),
            _('Elena Shimabara'),
            _('Minako Satake'),
            _('Megumi Tokoro'),
            _('Matsuri Tokugawa'),
            _('Serika Hakozaki'),
            _('Akane Nonohara'),
            _('Anna Mochizuki'),
            _('Roco Handa'),
            _('Yuriko Nanao'),
            _('Sayoko Takayama'),
            _('Arisa Matsuda'),
            _('Umi Kousaka'),
            _('Iku Nakatani'),
            _('Tomoka Tenkubashi'),
            _('Emily Stewart'),
            _('Shiho Kitazawa'),
            _('Ayumu Maihama'),
            _('Hinata Kinoshita'),
            _('Kana Yabuki'),
            _('Nao Yokoyama'),
            _('Chizuru Nikaido'),
            _('Konomi Baba'),
            _('Tamaki Ogami'),
            _('Fuka Toyokawa'),
            _('Miya Miyao'),
            _('Noriko Fukuda'),
            _('Mizuki Makabe'),
            _('Karen Shinomiya'),
            _('Rio Momose'),
            _('Subaru Nagayoshi'),
            _('Reika Kitakami'),
            _('Momoko Suou'),
            _('Julia'),
            _('Tsumugi Shiraishi'),
            _('Kaori Sakuramori')
        ][mst_character_id]
    else:
        return _('Shika')


@dispatcher.add_method(name='IdolService.GetIdolList', context_arg='context')
def get_idol_list(params, context):
    """Get a list of idol info for the user.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        idol_list: A list of dicts, where each dict represents a
                   single idol and contains the following keys.
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
            offer_type: Unknown (0-4).
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
                sort_id: Sort ID.
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
        memorial_list: A list of dicts, where each dict represents a
                       single memorial (idol story) and contains the
                       following keys.
            mst_memorial_id: Master memorial ID.
            scenario_id: A string for getting scenario-related
                         resources.
            mst_idol_id: Master idol ID.
            release_affection: Required affection value to unlock this
                               memorial.
            number: Memorial number (A sequential number starting with 1
                    for each idol).
            is_released: Whether this memorial is unlocked for the user.
            is_read: Whether the user has read this memorial.
            released_date: null.
            reward_item_list: A list containing a single dict
                              representing the rewards for reading this
                              memorial. Each dict contains the following
                              keys.
                reward_type: 4.
                mst_card_id: 0.
                card_status: A dict representing a null card. See the
                             return value 'card_list' of the method
                             'CardService.GetCardList' for the dict
                             definition.
                mst_item_id: For memorial #1, this value is set to 405
                             (money). For other memorials, this value is
                             set to 3 (free jewels).
                item_type: For memorial #1, this value is set to 2
                           (money). For other memorials, this value is
                           set to 1 (jewels).
                mst_costume_id: 0.
                costume_status: A dict representing a null costume. See
                                return value 'costume_list' of the
                                method 'CardService.GetCardList' for the
                                dict definition.
                mst_achievement_id: 0.
                amount: For memorial #1, this value is set to 3000. For
                        memorial #2, this value is set to 25. For other
                        memorials, this value is set to 50.
                is_new: false.
            is_available: Whether this memorial is available on the
                          server. Some idols do not have memorial #4 and
                          #5 at EoS.
            begin_date: Date when this memorial becomes available on the
                        server ('2099-12-31T23:59:59+0800' if not
                        available).
        episode_list: A list of dicts, where each dict represents a
                      single episode (card story unlocked through
                      awakening) and contains the following keys.
            mst_card_id: Master card ID for this episode.
            mst_idol_id: Master idol ID.
            is_released: Whether this episode is unlocked through
                         awakening the corresponding card.
            is_read: Whether the user has read this episode.
            released_date: null.
            reward_item_list: A list containing a single dict
                              representing the rewards for reading this
                              episode. See 'reward_item_list' for
                              'memorial_list' above.
        costume_adv_list: A list of dicts, where each dict represents a
                          single episode associated with an SSR card
                          costume and contains the following keys.
            mst_theater_costume_blog_id: Master costume episode ID. Each
                                         SSR card is associated with one
                                         costume episode and one costume
                                         blog. The same ID is shared
                                         among them.
            mst_card_id: Master card ID for this costume episode.
            mst_idol_id: Master idol ID.
            is_released: Whether the user has read this costume episode
                         (Both is_released and is_read have the same
                         value).
            is_read: Whether the user has read this costume episode.
            released_date: null.
            reward_item_list: A list containing a single dict
                              representing the rewards for reading this
                              costume episode. See 'reward_item_list'
                              for 'memorial_list' above.
    """
    with Session(engine) as session:
        idols = session.scalars(
            select(Idol)
            .where(Idol.user_id == UUID(context['user_id']))
        ).all()

        idol_schema = IdolSchema()
        idol_list = idol_schema.dump(idols, many=True)

        memorials = session.scalars(
            select(Memorial)
            .where(Memorial.user_id == UUID(context['user_id']))
        ).all()

        memorial_schema = MemorialSchema()
        memorial_list = memorial_schema.dump(memorials, many=True)

        episodes = session.scalars(
            select(Episode)
            .where(Episode.user_id == UUID(context['user_id']))
        ).all()

        episode_schema = EpisodeSchema()
        episode_list = episode_schema.dump(episodes, many=True)

        costume_advs = session.scalars(
            select(CostumeAdv)
            .where(CostumeAdv.user_id == UUID(context['user_id']))
        ).all()

        costume_adv_schema = CostumeAdvSchema()
        costume_adv_list = costume_adv_schema.dump(costume_advs, many=True)

    return {
        'idol_list': idol_list,
        'memorial_list': memorial_list,
        'episode_list': episode_list,
        'costume_adv_list': costume_adv_list
    }


@dispatcher.add_method(name='IdolService.GetBulkChangeCostumeGroupList')
def get_bulk_change_costume_group_list(params):
    """Get a list of costume bulk change groups.

    Invoked when the user presses Bulk Change button while changing
    costumes for 13 live (13人演唱會) on the unit confirmation screen
    under Live tab.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
        bulk_change_costume_group_list: A list of dicts, where each dict
                                        represents a single costume bulk
                                        change group and contains the
                                        following keys.
            mst_costume_bulk_change_group_id: Master costume bulk change
                                              group ID.
            cbc_group_name: Costume bulk change group name.
            cbc_target_id: An integer representing the target of this
                           costume bulk change group. Non-positive IDs
                           have special meanings.
                           0=765 MILLION ALLSTARS
                           -1=PRINCESS STARS
                           -2=FAIRY STARS
                           -3=ANGEL STARS
                           -4=765PRO ALLSTARS
            cbc_sort_id: Sort ID.
            cbc_icon_resource_id: A string for getting icon-related
                                  resources.
            cbc_target_sort_id_format: A string representing the sort ID
                                       format for the costumes within
                                       this costume bulk change group.
            cbc_target_sort_id_format_list: A list containing exactly
                                            one string. This string is
                                            the same as
                                            cbc_target_sort_id_format.
            begin_date: '2018-01-01T00:00:00+0800'.
            end_date: '2099-12-31T23:59:59+0800'.
    """
    with Session(engine) as session:
        mst_costume_bulk_change_groups = session.scalars(
            select(MstCostumeBulkChangeGroup)
        ).all()

        bulk_change_costume_group_schema = MstCostumeBulkChangeGroupSchema()
        bulk_change_costume_group_list = bulk_change_costume_group_schema.dump(
            mst_costume_bulk_change_groups, many=True
        )

    return {
        'bulk_change_costume_group_list': bulk_change_costume_group_list
    }

