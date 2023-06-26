from jsonrpc import dispatcher
from sqlalchemy import select
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import (MstAwakeningConfig, MstComicMenu,
                                MstExMasterLessonConfig, MstGameSetting,
                                MstLessonMoneyConfig,
                                MstLessonSkillLevelUpConfig,
                                MstLessonWearConfig, MstLoadingCharacter,
                                MstMasterLesson2Config,
                                MstMasterLessonFiveConfig, MstTitleImage,
                                MstTrainingUnit)
from mltd.models.schemas import (MstAwakeningConfigSchema, MstComicMenuSchema,
                                 MstExMasterLessonConfigSchema,
                                 MstGameSettingSchema,
                                 MstLessonMoneyConfigSchema,
                                 MstLessonSkillLevelUpConfigSchema,
                                 MstLessonWearConfigSchema,
                                 MstLoadingCharacterSchema,
                                 MstMasterLesson2ConfigSchema,
                                 MstMasterLessonFiveConfigSchema,
                                 MstTitleImageSchema, MstTrainingUnitSchema)


@dispatcher.add_method(name='GameSettingService.GetSetting')
def get_setting(params):
    """Service for getting game settings.

    Invoked as part of the initial batch requests after logging in.
    Args:
        params: An empty dict.
    Returns:
        A dict containing the following keys.
            game_setting: A dict representing various game settings.
                          Contains the following keys.
                awakening_config_list: A list of dicts representing the
                                       required items for awakening.
                                       Each dict contains the following
                                       keys.
                    rarity: Card rarity (1-4).
                    idol_type: Card idol type (1-3, 5).
                    mst_card_id: To which card does this config applies
                                 (0 if this config applies to all cards
                                 of the specified rarity and idol type).
                    required_item_list: A list of dicts containing the
                                        following keys.
                        mst_item_id: Master item ID.
                        amount: Number of items needed.
                master_lesson2_config_list: A list of dicts representing
                                            the required master pieces
                                            for master rank lessons.
                                            Each dict contains the
                                            following keys.
                    rarity: Card rarity (1-4).
                    idol_type: Card idol type (1-3).
                    master_piece_list: A list of dicts containing the
                                       following keys.
                        mst_item_id: Master item ID of the master piece.
                        amount: Number of master pieces needed.
                ex_master_lesson_config_list: A list of dicts
                                              representing the required
                                              number of PST/FES pieces
                                              for master rank lessons.
                                              Each dict contains the
                                              following keys.
                    ex_type: Card extra type [2=PST (Ranking), 3=PST
                             (Event Pt), 4=FES, 5=1st, 6=Ex].
                    mst_item_id: Master item ID of the PST piece/FES
                                 master piece.
                    amount: A list of 4 ints representing the required
                            number of PST/FES pieces for master ranks
                            1-4.
                    mst_card_id: To which card does this config applies
                                 (0 if this config applies to all cards
                                 of the specified ex_type).
                lesson_money_config_list: A list of dicts representing
                                          the money required per ticket
                                          for lessons. Each dict
                                          contains the following keys.
                    rarity: Ticket rarity (1-4).
                    money: Money required to use one ticket on any card.
                    mst_item_id: Master item ID of the ticket.
                lesson_skill_level_up_config_list: A list of dicts
                                                   representing the
                                                   required 'skill EXP'
                                                   for each skill level
                                                   for guaranteed level
                                                   up. Each dict
                                                   contains the
                                                   following keys.
                    skill_level: Target skill level (1-12).
                    rarity: Card rarity (1-4).
                    value: Required 'skill EXP' for guaranteed level up
                           to the target skill level. 'Skill EXP'
                           provided per ticket is defined as follows:
                                Lesson ticket N=0
                                Lesson ticket R=300
                                Lesson ticket SR=1000
                                Lesson ticket SSR=2000
                rank5_skill_level_max: Maximum possible skill level for
                                       a master rank 5 card (12).
                lesson_wear_config_list: A list of dicts representing
                                         the available lesson wears.
                                         Each dict contains the
                                         following keys.
                    mst_lesson_wear_setting_id: Master lesson wear
                                                setting ID (1, 9001).
                    mst_lesson_wear_group_id_list: A list containing a
                                                   single int
                                                   representing the
                                                   lesson wear group ID
                                                   (1, 9001).
                awakening_bonus_level: Number of additional levels a
                                       card can be trained after
                                       awakening (10).
                max_master_rank: Maximum possible master rank for a non-
                                 master rank 5 card (4).
                master_rank_bonus: Bonus % increase in vocal/dance/
                                   visual values per master rank (3).
                card_lv_base: Increase in required card EXP per level
                              (20).
                card_lv_diff: Required card EXP to level up a level 1
                              card to level 2 (10).
                user_lv_base: Increase in required user EXP per level
                              (100).
                user_lv_diff: Required user EXP to level up from level 1
                              to level 2 (50).
                recover_jewel: A dict representing the required jewels
                               to recover 100% vitality. Contains the
                               following keys.
                    amount: Number of jewels required.
                    begin_date: '2018-01-01T00:00:00+0800'.
                    end_date: '2099-12-31T23:59:59+0800'.
                continue_jewel: A dict representing the required jewels
                                to continue a song when life reaches 0.
                                See 'recover_jewel' for the dict
                                definition.
                enable_lounge: Whether lounge is enabled (true).
                rehearsal_cost: Money required for rehearsal (2000).
                live_ticket_scale: Unknown (10).
                enable_sale: Whether shop is enabled (true).
                enable_sales_costume: Whether costume shop is enabled
                                      (true).
                enable_gasha_exchange_limit_point: Whether gacha
                                                   exchange limit point
                                                   is enabled (true).
                enable_event_shop: Whether event shop is enabled (true).
                enable_unit: Whether user-defined units are enabled
                             (true).
                overflow_date: Unknown ('2018-01-31T13:00:00+0800').
                enable_song_unit: Whether song units are enabled (true).
                enable_song_unit_duo: Whether duo song units are enabled
                                      (true).
                enable_song_full_random: Whether full random is enabled
                                         in song select (true).
                enable_song_song_random: Whether song random is enabled
                                         in song select (true).
                enable_a1st_card_shop: Whether 1st anniversary card shop
                                       is enabled (false).
                enable_training: Whether 2nd anniversary training is
                                 enabled (true).
                lounge_chat_fetch_cycle: A list of ints representing
                                         how often the lounge chat is
                                         fetched.
                enable_comic_button: Unknown (true).
                comic_button_url: Unknown ('defaultComic').
                comic_menu_list: A list of dicts representing available
                                 comic menu items. Each dict contains
                                 the following keys.
                    mst_comic_menu_id: Master comic menu ID.
                    url: URL.
                    resource_id: A string for getting comic-related
                                 resources.
                    enable_button: Whether the button is enabled.
                enable_item_shop: Whether item shop is enabled (true).
                board_write_limit_level: Unknown (0).
                training_unit_list: A list of dicts representing the
                                    required songs and idols for 2nd
                                    anniversary training missions. Each
                                    dict contains the following keys.
                    mst_song_unit_id: Master song unit ID.
                    idol_id_list: A list of 54 master idol IDs
                                  representing the song unit idols for
                                  this mission. If the song unit has
                                  less than 54 idols, zeros are appended
                                  to this list.
                master_lesson_five_config_list: A list of dicts
                                                representing the
                                                required items for
                                                master rank 5 lessons.
                                                Each dict contains the
                                                following keys.
                    ex_type: Card extra type (0=Normal, 4=FES).
                    idol_type: Card idol type (1-3).
                    required_item_list: A list of dicts containing the
                                        following keys.
                        mst_item_id: Master item ID.
                        amount: Number of items needed.
                un_lock_song_jewel: A dict representing the required
                                    jewels to unlock a song in the shop.
                                    See 'recover_jewel' for the dict
                                    definition.
                mst_item_id_with_type_master_key: Master item ID of
                                                  singing voice master
                                                  key (51).
                title_image_list: A list of dicts representing available
                                  title screen images. Each dict
                                  contains the following keys.
                    mst_title_image_id: Master title image ID.
                    title_image_type: Title image type (2=event,
                                      3=others).
                    sort_id: Sort ID.
                    begin_date: Date when this title image becomes
                                available.
                    end_date: Date when this title image becomes
                              unavailable.
                profile_achievement_list_limit_count: Maximum possible
                                                      number of
                                                      achievements a
                                                      user can set in
                                                      their profile
                                                      (52).
                enable_thank_you_mode: Unknown (true).
                enable_new_gasha_view: Unknown (true).
                enable_flower_stand_multi: Whether multiple flower
                                           stands can be gifted to
                                           friends at the same time
                                           (true).
                enable_n_t4: Unknown (false).
                function_release_id_list: Unknown (a list of ints).
                default_release_all_song_difficulty_lv: At which user
                                                        level all main
                                                        story songs are
                                                        unlocked (50).
                max_training_point: Unknown (0).
            theater_poster: A dict containing the following keys.
                theater_poster_id: ''.
                place: 0.
                resource_id: ''.
                begin_date: null.
                end_date: null.
                poster_image_url: ''.
            theater_poster_list: null.
            loading_character_list: A list of dicts representing loading
                                    screen characters. Contains the
                                    following keys.
                resource_id: A string for getting resources related to
                             this loading screen character.
                weight: 1.
                begin_date: Date when this loading screen character
                            becomes available.
                end_date: Date when this loading screen character
                          becomes unavailable.
    """
    with Session(engine) as session:
        mst_game_setting = session.scalar(
            select(MstGameSetting)
        )
        mst_awakening_configs = session.scalars(
            select(MstAwakeningConfig)
        ).all()
        mst_master_lesson2_configs = session.scalars(
            select(MstMasterLesson2Config)
        ).all()
        mst_ex_master_lesson_configs = session.scalars(
            select(MstExMasterLessonConfig)
        ).all()
        mst_lesson_money_configs = session.scalars(
            select(MstLessonMoneyConfig)
        ).all()
        mst_lesson_skill_level_up_configs = session.scalars(
            select(MstLessonSkillLevelUpConfig)
        ).all()
        mst_lesson_wear_configs = session.scalars(
            select(MstLessonWearConfig)
        ).all()
        mst_comic_menus = session.scalars(
            select(MstComicMenu)
        ).all()
        mst_training_units = session.scalars(
            select(MstTrainingUnit)
        ).all()
        mst_master_lesson_five_configs = session.scalars(
            select(MstMasterLessonFiveConfig)
        ).all()
        mst_title_images = session.scalars(
            select(MstTitleImage)
        ).all()

        mst_game_setting_schema = MstGameSettingSchema()
        game_setting = mst_game_setting_schema.dump(mst_game_setting)
        awakening_config_schema = MstAwakeningConfigSchema()
        game_setting['awakening_config_list'] = awakening_config_schema.dump(
            mst_awakening_configs, many=True)
        master_lesson2_config_schema = MstMasterLesson2ConfigSchema()
        game_setting['master_lesson2_config_list'] = (
            master_lesson2_config_schema.dump(mst_master_lesson2_configs,
                                              many=True))
        ex_master_lesson_config_schema = MstExMasterLessonConfigSchema()
        game_setting['ex_master_lesson_config_list'] = (
            ex_master_lesson_config_schema.dump(mst_ex_master_lesson_configs,
                                                many=True))
        lesson_money_config_schema = MstLessonMoneyConfigSchema()
        game_setting['lesson_money_config_list'] = (
            lesson_money_config_schema.dump(mst_lesson_money_configs,
                                            many=True))
        lesson_skill_level_up_config_schema = (
            MstLessonSkillLevelUpConfigSchema())
        game_setting['lesson_skill_level_up_config_list'] = (
            lesson_skill_level_up_config_schema.dump(
                mst_lesson_skill_level_up_configs, many=True))
        lesson_wear_config_schema = MstLessonWearConfigSchema()
        game_setting['lesson_wear_config_list'] = (
            lesson_wear_config_schema.dump(mst_lesson_wear_configs, many=True))
        comic_menu_schema = MstComicMenuSchema()
        game_setting['comic_menu_list'] = comic_menu_schema.dump(
            mst_comic_menus, many=True)
        training_unit_schema = MstTrainingUnitSchema()
        game_setting['training_unit_list'] = training_unit_schema.dump(
            mst_training_units, many=True)
        master_lesson_five_config_schema = MstMasterLessonFiveConfigSchema()
        game_setting['master_lesson_five_config_list'] = (
            master_lesson_five_config_schema.dump(
                mst_master_lesson_five_configs, many=True))
        title_image_schema = MstTitleImageSchema()
        game_setting['title_image_list'] = title_image_schema.dump(
            mst_title_images, many=True)

        mst_loading_characters = session.scalars(
            select(MstLoadingCharacter)
        ).all()

        mst_loading_character_schema = MstLoadingCharacterSchema()
        loading_character_list = mst_loading_character_schema.dump(
            mst_loading_characters, many=True)

    return {
        'game_setting': game_setting,
        'theater_poster': {
            'theater_poster_id': '',
            'place': 0,
            'resource_id': '',
            'begin_date': None,
            'end_date': None,
            'poster_image_url': ''
        },
        'theater_poster_list': None,
        'loading_character_list': loading_character_list
    }

