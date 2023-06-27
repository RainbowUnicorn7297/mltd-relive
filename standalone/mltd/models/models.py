from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from mltd.models.engine import engine
from mltd.servers.config import server_timezone


class Base(DeclarativeBase):
    pass


class User(Base):
    """User info."""
    __tablename__ = 'user'

    user_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    search_id: Mapped[str] = mapped_column(String(8), unique=True)
    name: Mapped[str] = mapped_column(String(10), default='')
    money: Mapped[int] = mapped_column(default=0)
    max_money: Mapped[int] = mapped_column(default=9_999_999)
    vitality: Mapped[int] = mapped_column(default=60)
    max_vitality: Mapped[int] = mapped_column(default=60)
    live_ticket: Mapped[int] = mapped_column(default=0)
    max_live_ticket: Mapped[int] = mapped_column(default=500)
    exp: Mapped[int] = mapped_column(default=0)
    next_exp: Mapped[int] = mapped_column(default=50)
    level: Mapped[int] = mapped_column(default=1)
    max_level: Mapped[int] = mapped_column(default=999)
    lp: Mapped[int] = mapped_column(default=0)
    theater_fan: Mapped[int] = mapped_column(default=52)
    last_login_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    is_tutorial_finished: Mapped[bool] = mapped_column(default=False)
    lounge_id: Mapped[Optional[UUID]] = mapped_column(default='',
                                                      insert_default=None)
    lounge_name: Mapped[str] = mapped_column(default='')
    lounge_user_state: Mapped[int] = mapped_column(default=0)
    producer_rank: Mapped[int] = mapped_column(default=1)
    full_recover_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    auto_recover_interval: Mapped[int] = mapped_column(default=300)
    first_time_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    produce_gauge: Mapped[int] = mapped_column(default=0)
    max_friend: Mapped[int] = mapped_column(default=50)
    is_connected_bnid: Mapped[bool] = mapped_column(default=False)
    is_connected_facebook: Mapped[bool] = mapped_column(default=False)
    default_live_quality: Mapped[int] = mapped_column(default=0)
    default_theater_quality: Mapped[int] = mapped_column(default=0)
    default_mv_quality: Mapped[int] = mapped_column(default=0)
    mv_quality_limit: Mapped[int] = mapped_column(default=0)
    tutorial_live_quality: Mapped[int] = mapped_column(default=0)
    asset_tag: Mapped[str] = mapped_column(default='')
    user_id_hash: Mapped[str]
    disabled_massive_live: Mapped[bool] = mapped_column(default=False)
    disabled_massive_mv: Mapped[bool] = mapped_column(default=False)
    button_disabled: Mapped[bool] = mapped_column(default=False)
    training_point: Mapped[int] = mapped_column(default=0)
    total_training_point: Mapped[int] = mapped_column(default=0)

    challenge_song: Mapped['ChallengeSong'] = relationship(
        back_populates='user', lazy='joined', innerjoin=True)
    mission_summary: Mapped['PanelMissionSheet'] = relationship(
        back_populates='user', lazy='joined', innerjoin=True)
    map_level: Mapped['MapLevel'] = relationship(back_populates='user',
                                                 lazy='joined', innerjoin=True)
    un_lock_song_status: Mapped['UnLockSongStatus'] = relationship(
        back_populates='user', lazy='joined', innerjoin=True)
    pending_song: Mapped['PendingSong'] = relationship(
        back_populates='user', foreign_keys='PendingSong.user_id')
    pending_job: Mapped['PendingJob'] = relationship(back_populates='user')
    gasha_medal: Mapped['GashaMedal'] = relationship(back_populates='user')
    jewel: Mapped['Jewel'] = relationship(back_populates='user')
    lps: Mapped[List['LP']] = relationship(
        back_populates='user', order_by='[LP.lp.desc(), LP.update_date]')
    songs: Mapped[List['Song']] = relationship(back_populates='user')
    courses: Mapped[List['Course']] = relationship(back_populates='user')
    cards: Mapped[List['Card']] = relationship(back_populates='user')
    items: Mapped[List['Item']] = relationship(back_populates='user')
    idols: Mapped[List['Idol']] = relationship(back_populates='user')
    costumes: Mapped[List['Costume']] = relationship(back_populates='user')
    memorials: Mapped[List['Memorial']] = relationship(back_populates='user')
    episodes: Mapped[List['Episode']] = relationship(back_populates='user')
    costume_advs: Mapped[List['CostumeAdv']] = relationship(
        back_populates='user')
    gashas: Mapped[List['Gasha']] = relationship(back_populates='user')
    units: Mapped[List['Unit']] = relationship(back_populates='user',
                                               order_by='[Unit.unit_num]')
    song_units: Mapped[List['SongUnit']] = relationship(back_populates='user')
    main_story_chapters: Mapped[List['MainStoryChapter']] = relationship(
        back_populates='user')
    campaigns: Mapped[List['Campaign']] = relationship(back_populates='user')
    record_times: Mapped[List['RecordTime']] = relationship(
        back_populates='user')


class MstIdol(Base):
    """Master table for idol info.

    tension: Unused. tension=100 for all idols
    is_best_condition: Unused. is_best_condition=false for all idols
    area: ??? 0-7
    offer_type: ??? 0-4
    mst_agency_id: 1=765, 2=961
    default_costume: mst_costume_id of zh/ko default costume (輝煌一體)
    birthday_live: birthday_live=0 for Shika, 1 for everyone else
    """
    __tablename__ = 'mst_idol'

    mst_idol_id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[str]
    idol_type: Mapped[int]
    tension: Mapped[int] = mapped_column(default=100)
    is_best_condition: Mapped[bool] = mapped_column(default=False)
    area: Mapped[int]
    offer_type: Mapped[int]
    mst_agency_id: Mapped[int]
    default_costume_id = mapped_column(
        ForeignKey('mst_costume.mst_costume_id'), nullable=False)
    birthday_live: Mapped[int]

    default_costume: Mapped['MstCostume'] = relationship(
        foreign_keys=default_costume_id, lazy='joined', innerjoin=True)


class Idol(Base):
    """Idol info specific to each user.

    has_another_appeal: true=unlocked 異色綻放, false=not yet unlocked
    can_perform: false only when Ex card not yet obtained
    """
    __tablename__ = 'idol'

    idol_id: Mapped[str] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                nullable=False)
    fan: Mapped[int] = mapped_column(default=1)
    affection: Mapped[int] = mapped_column(default=0)
    has_another_appeal: Mapped[bool] = mapped_column(default=False)
    can_perform: Mapped[bool] = mapped_column(default=True)

    user: Mapped['User'] = relationship(back_populates='idols')
    mst_idol: Mapped['MstIdol'] = relationship(lazy='joined', innerjoin=True)
    lesson_wear_config: Mapped['LessonWearConfig'] = relationship(
        primaryjoin='Idol.user_id == LessonWearConfig.user_id',
        foreign_keys=user_id,
        viewonly=True, lazy='joined', innerjoin=True)
    mst_costumes: Mapped[List['MstCostume']] = relationship(
        secondary='costume',
        primaryjoin='and_(Idol.user_id == Costume.user_id, '
            + 'Idol.mst_idol_id == MstCostume.mst_idol_id)',
        viewonly=True, lazy='selectin')
    mst_voice_categories: Mapped[List['MstVoiceCategory']] = relationship(
        uselist=True,
        primaryjoin='and_(MstVoiceCategory.idol_detail_type == 3, '
            + 'Idol.affection >= MstVoiceCategory.value)',
        foreign_keys=affection,
        viewonly=True, lazy='selectin')
    mst_lesson_wears: Mapped[List['MstLessonWear']] = relationship(
        uselist=True,
        primaryjoin='Idol.mst_idol_id == MstLessonWear.mst_idol_id',
        foreign_keys=mst_idol_id,
        viewonly=True, lazy='selectin')


class MstCostume(Base):
    """Master table for costumes.

    mst_costume_group_id: ??? 0-993
    costume_name: ??? -,ex,ss,sr,gs, mostly ex
    costume_number: ??? 0-601
    exclude_album: true for 2nd anniversary costumes with
                   butterfly wings (excluded from costume album),
                   false for everything else
    exclude_random: true for mst_costume_id=0, false for everything else
    collabo_number: Unused. collabo_number=0 for all costumes
    replace_group_id: ??? 0,4-6, mostly 0
    gorgeous_appeal_type: 0=normal, 1=master rank 5 costume
    """
    __tablename__ = 'mst_costume'

    mst_costume_id: Mapped[int] = mapped_column(primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                nullable=False)
    resource_id: Mapped[str]
    mst_costume_group_id: Mapped[int]
    costume_name: Mapped[str]
    costume_number: Mapped[int]
    exclude_album: Mapped[bool]
    exclude_random: Mapped[bool] = mapped_column(default=False)
    collabo_number: Mapped[int] = mapped_column(default=0)
    replace_group_id: Mapped[int]
    sort_id: Mapped[int]
    release_date: Mapped[datetime]
    gorgeous_appeal_type: Mapped[int]


class Costume(Base):
    """Costumes unlocked by user."""
    __tablename__ = 'costume'

    costume_id: Mapped[str] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)

    user: Mapped['User'] = relationship(back_populates='costumes')
    mst_costume: Mapped['MstCostume'] = relationship(lazy='joined',
                                                     innerjoin=True)


class MstCenterEffect(Base):
    """Master table for card center skills.

    mst_center_effect_id: 0=No center skills
        1st digit: Center skill name prefix
            1=Princess, 2=Fairy, 3=Angel, 5=Ex, 6=三重 (Tricolor)
        2nd digit: Center skill strength
            2=R, 3=SR (including 1st and 2nd), 4=SSR (including FES)
        3rd-4th digits: Center skill name suffix
            01=閃耀 (All appeals+X%)
            02=和聲 (Vocal+X%)
            03=舞步 (Dance+X%)
            04=穿搭 (Visual+X%)
            05=凝聚 (Life+X%)
            06=技巧 (Skill prob.+X%)
            08=歌姬 (Unicolor Vocal+X%)
            09=表演者 (Unicolor Dance+X%)
            10=耀眼光輝 (Unicolor Visual+X%)
    effect_id: Unused. effect_id=1 for all center effects
    idol_type: Center skill target idol type
        1=Princess, 2=Fairy, 3=Angel, 4=All types
    specific_idol_type: Center skill requirements on unit idol type
        0=No requirements
        1=Princess unicolor
        2=Fairy unicolor
        3=Angel unicolor
        4=Tricolor
    attribute:
        1=Vocal+X%, 2=Dance+X%, 3=Visual+X%, 4=All appeals+X%,
        5=Life+X%, 6=Skill prob.+X%
    value: % increase
    song_idol_type: Unused. song_idol_type=0 for all center effects
    attribute2: Unused. attribute2=0 for all center effects
    value2: Unused. value2=0 for all center effects
    """
    __tablename__ = 'mst_center_effect'

    mst_center_effect_id: Mapped[int] = mapped_column(primary_key=True)
    effect_id: Mapped[int] = mapped_column(default=1)
    idol_type: Mapped[int]
    specific_idol_type: Mapped[int]
    attribute: Mapped[int]
    value: Mapped[int]
    song_idol_type: Mapped[int] = mapped_column(default=0)
    attribute2: Mapped[int] = mapped_column(default=0)
    value2: Mapped[int] = mapped_column(default=0)


class MstCardSkill(Base):
    """Master table for card skills.

    effect_id:
        1=Score bonus, 2=Combo bonus, 3=Healer, 4=Life guard,
        5=Combo guard, 6=Perfect lock, 7=Double boost, 8=Multi up,
        10=Overclock
    evaluation: Required note types for activating skill
        0=N/A
        1=Perfect
        2=Perfect/Great
        3=Great
        4=Great/Good/Fast/Slow
        6=Fast/Slow
        7=Great/Good
    evaluation2: Required note types for activating 2nd skill
    probability_base: skill probability in % if skill level=0
    value: % or value increase for skill
    value2: % or value increase for 2nd skill
    """
    __tablename__ = 'mst_card_skill'

    mst_card_skill_id: Mapped[int] = mapped_column(primary_key=True)
    effect_id: Mapped[int]
    duration: Mapped[int]
    evaluation: Mapped[int]
    evaluation2: Mapped[int]
    interval: Mapped[int]
    probability_base: Mapped[int]
    value: Mapped[int]
    value2: Mapped[int]


class MstCard(Base):
    """Master table for card info.

    rarity: 1=N, 2=R, 3=SR, 4=SSR
    attribute:
        1=Vocal+X%, 2=Dance+X%, 3=Visual+X%, 4=All appeals+X%,
        5=Life+X%, 6=Skill prob.+X%
    begin_date: Card released
    ex_type:
        0=Normal, 2=PST (Ranking), 3=PST (Event Pt), 4=FES, 5=1st,
        6=Ex, 7=2nd
    idol_type: 1=Princess, 2=Fairy, 3=Angel, 5=Ex
    level_max: max level after awakened
        If N, level_max = 30
        If R, level_max = 50
        If SR, level_max = 70
        If SSR, level_max = 90
    vocal_base: Vocal base value if card level=0, before awakened,
                master rank=0
        If N, vocal_base = round(vocal_max * 20 / 60)
        If R, vocal_base = round(vocal_max * 40 / 100)
        If SR, vocal_base = round(vocal_max * 60 / 140)
        If SSR, vocal_base = round(vocal_max * 80 / 180)
    vocal_max: Vocal max value if card level=90, after awakened,
               master rank=0
    vocal_master_bonus: Vocal bonus per master rank
        vocal_master_bonus = round(vocal_max * 0.03)
    cheer_point: Unused. cheer_point=0 for all cards
    mst_card_skill_id: null or one skill per card (not a list)
    variation: ??? 1-16, older=smaller, newer=larger
    master_lesson_begin_date: master lessons became available for
                              PST card
    card_category: ??? 10-35
        33=Anniversary card
    extend_card_params: Anniversary card stats after trained to SSR
    training_point: Unused. training_point=0 for all cards
    sign_type: Unused. sign_type=0 for all cards
    sign_type2: Unused. sign_type2=0 for all cards
    """
    __tablename__ = 'mst_card'

    mst_card_id: Mapped[int] = mapped_column(primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                nullable=False)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)
    bonus_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                     nullable=False)
    rank5_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                     nullable=False)
    resource_id: Mapped[str]
    rarity: Mapped[int]
    idol_type: Mapped[int]
    level_max: Mapped[int]
    life: Mapped[int]
    vocal_base: Mapped[int]
    vocal_max: Mapped[int]
    vocal_master_bonus: Mapped[int]
    dance_base: Mapped[int]
    dance_max: Mapped[int]
    dance_master_bonus: Mapped[int]
    visual_base: Mapped[int]
    visual_max: Mapped[int]
    visual_master_bonus: Mapped[int]
    awakening_gauge_max: Mapped[int]
    master_rank_max: Mapped[int]
    cheer_point: Mapped[int] = mapped_column(default=0)
    mst_center_effect_id = mapped_column(
        ForeignKey('mst_center_effect.mst_center_effect_id'), nullable=False)
    mst_card_skill_id = mapped_column(
        ForeignKey('mst_card_skill.mst_card_skill_id'))
    ex_type: Mapped[int]
    variation: Mapped[int]
    master_lesson_begin_date: Mapped[datetime]
    training_item_list: Mapped[Optional[str]] = mapped_column(default=None)
    begin_date: Mapped[datetime]
    sort_id: Mapped[int]
    card_category: Mapped[int]
    extend_card_level_max: Mapped[int]
    extend_card_life: Mapped[int]
    extend_card_vocal_max: Mapped[int]
    extend_card_vocal_master_bonus: Mapped[int]
    extend_card_dance_max: Mapped[int]
    extend_card_dance_master_bonus: Mapped[int]
    extend_card_visual_max: Mapped[int]
    extend_card_visual_master_bonus: Mapped[int]
    is_master_lesson_five_available: Mapped[bool]
    barrier_mission_list: Mapped[Optional[str]] = mapped_column(default=None)
    training_point: Mapped[int] = mapped_column(default=0)
    sign_type: Mapped[int] = mapped_column(default=0)
    sign_type2: Mapped[int] = mapped_column(default=0)

    mst_center_effect: Mapped['MstCenterEffect'] = relationship(
        lazy='joined', innerjoin='true')
    mst_card_skill: Mapped['MstCardSkill'] = relationship(
        lazy='joined')
    mst_costume: Mapped['MstCostume'] = relationship(
        lazy='joined', innerjoin=True, foreign_keys=mst_costume_id)
    bonus_costume: Mapped['MstCostume'] = relationship(
        lazy='joined', innerjoin=True, foreign_keys=bonus_costume_id)
    rank5_costume: Mapped['MstCostume'] = relationship(
        lazy='joined', innerjoin=True, foreign_keys=rank5_costume_id)


class Card(Base):
    """Card info specific to each user.

    vocal: Current Vocal value
        vocal = vocal_base + round(vocal_diff * level) +
                vocal_master_bonus * master_rank
    vocal_diff: Vocal bonus per level
        Before awakened:
            If N, vocal_diff = vocal_max / 60
            If R, vocal_diff = vocal_max / 100
            If SR, vocal_diff = vocal_max / 140
            If SSR, vocal_diff = vocal_max / 180
        After awakened:
            If N, vocal_diff += vocal_max * 10 / 60 / 30
            If R, vocal_diff += vocal_max * 10 / 100 / 50
            If SR, vocal_diff += vocal_max * 10 / 140 / 70
            If SSR, vocal_diff += vocal_max * 10 / 180 / 90
    skill_level_max: 12 only if trained to master rank 5, 10 otherwise
    skill_probability: Current skill probability in %
        For skill levels 1-10:
            skill_probability = probability_base + skill_level
        For skill levels 11-12:
            skill_probability = probability_base + 10 + 5 * (skill_level - 10)
            TODO: verify skill level 11
    create_date: Card obtained by user
    """
    __tablename__ = 'card'

    card_id: Mapped[str] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                nullable=False)
    exp: Mapped[int] = mapped_column(default=0)
    level: Mapped[int] = mapped_column(default=1)
    vocal: Mapped[int]
    vocal_diff: Mapped[float]
    dance: Mapped[int]
    dance_diff: Mapped[float]
    visual: Mapped[int]
    visual_diff: Mapped[float]
    before_awakened_vocal: Mapped[int]
    before_awakened_dance: Mapped[int]
    before_awakened_visual: Mapped[int]
    after_awakened_vocal: Mapped[int]
    after_awakened_dance: Mapped[int]
    after_awakened_visual: Mapped[int]
    skill_level: Mapped[int] = mapped_column(default=1)
    skill_level_max: Mapped[int] = mapped_column(default=10)
    skill_probability: Mapped[Optional[int]]
    is_awakened: Mapped[bool] = mapped_column(default=False)
    awakening_gauge: Mapped[int] = mapped_column(default=1)
    master_rank: Mapped[int] = mapped_column(default=0)
    create_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    is_new: Mapped[bool] = mapped_column(default=False)

    mst_card: Mapped['MstCard'] = relationship(lazy='joined', innerjoin=True)
    user: Mapped['User'] = relationship(back_populates='cards')


class MstDirectionCategory(Base):
    """Master table for direction category (演出).

    idol_detail_type: 1=shown in idol details,
                      2=hidden from idol details
    direction_type:
        1=idol birthday greeting
        2=seasonal greeting
        4-6=default greeting???
    3rd idol birthday greeting (mst_direction_category_id=2010) is only
    available for idols with birthdays between June 29 and September 30.
    1st new year greeting (mst_direction_category_id=2002) is only
    available for Mirai, Shizuka and Tsubasa.
    """
    __tablename__ = 'mst_direction_category'

    mst_direction_category_id: Mapped[int] = mapped_column(primary_key=True)
    sort_id: Mapped[int]
    idol_detail_type: Mapped[int]
    direction_type: Mapped[int]
    resource_id: Mapped[str]
    release_date: Mapped[datetime]


class MstVoiceCategory(Base):
    """Master table for voice category (語音).

    value: Unlock condition for voice category
        For mst_voice_category_ids 3101-3106, value=required affection
        For 3101, value=50
        For 3102, value=200
        For 3103, value=500
        For 3104, value=900
        For 3105, value=1400
        For 3106, value=2000
    mst_direction_category_id: Unused. 0 for all voice categories
    """
    __tablename__ = 'mst_voice_category'

    mst_voice_category_id: Mapped[int] = mapped_column(primary_key=True)
    sort_id: Mapped[int]
    idol_detail_type: Mapped[int]
    value: Mapped[int]
    rarity: Mapped[int]
    label_header: Mapped[str]
    voice_label: Mapped[str]
    release_date: Mapped[datetime]
    mst_direction_category_id: Mapped[int] = mapped_column(default=0)


# class IdolVoiceCategory(Base):
#     """Unlocked idol voice categories (偶像特有台詞) by user.

#     #1: affection=50
#     #2: affection=200
#     #3: affection=500
#     #4: affection=900
#     #5: affection=1400
#     #6: affection=2000
#     TODO: table is redundant by comparing mst_voice_category's value
#           with current affection per idol for each user
#     """
#     __tablename__ = 'idol_voice_category'

#     idol_voice_category_id: Mapped[str] = mapped_column(primary_key=True)
#     user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
#     mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
#                                 nullable=False)
#     mst_voice_category_id = mapped_column(
#         ForeignKey('mst_voice_category.mst_voice_category_id'), nullable=False)


class MstLessonWear(Base):
    """Master table for lesson wear.

    mst_lesson_wear_id: 1-53=訓練課程服, 90001-90052=1週年記念
    mst_lesson_wear_group_id: 1=訓練課程服, 9001=1週年記念
    costume_number: costume_number=1 for all lesson wear
    costume_name: tr,gs=訓練課程服, cr=1週年記念
    collabo_no: 0=訓練課程服, 55=1週年記念
    resource_id: 201xxx0013 for Shika, training_01 for everyone else
    """
    __tablename__ = 'mst_lesson_wear'

    mst_lesson_wear_id: Mapped[int] = mapped_column(primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                nullable=False)
    mst_lesson_wear_group_id: Mapped[int]
    costume_number: Mapped[int] = mapped_column(default=1)
    costume_name: Mapped[str]
    collabo_no: Mapped[int]
    resource_id: Mapped[str]


# class IdolLessonWear(Base):
#     """Default lesson wear chosen by each user.

#     TODO: table is redundant by combining tables 'mst_lesson_wear',
#           'lesson_wear_config' and 'mst_lesson_wear_config'
#     """
#     __tablename__ = 'idol_lesson_wear'

#     idol_lesson_wear_id: Mapped[str] = mapped_column(primary_key=True)
#     user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
#     mst_lesson_wear_id = mapped_column(
#         ForeignKey('mst_lesson_wear.mst_lesson_wear_id'), nullable=False)
#     default_flag: Mapped[bool]


class MstItem(Base):
    """Master table for items.

    item_navi_type:
        0=Others (money, memory piece, anniversary idol-specific piece)
        1=Vitality recovery item (spark drink, macaron,
            present from idol)
        2=Awakening item
        3=Lesson ticket
        4=Master rank item (including PST piece)
        5=Gacha ticket/medal
        6=Live item (live ticket, auto live pass,
            singing voice master key)
        7=Gift for affection
        8=Gift for awakening gauge
    item_type:
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
    value1/value2:
        For vitality recovery item:
            Spark drink 10: value1=10, value2=0
            Spark drink 20: value1=20, value2=0
            Spark drink 30: value1=30, value2=0
            Spark drink MAX/equivalent: value1=0, value2=100
        For lesson ticket,
            Lesson ticket N: value1=800, value2=0
            Lesson ticket R: value1=2500, value2=300
            Lesson ticket SR: value1=4000, value2=1000
            Lesson ticket SSR: value1=5000, value2=2000
        For gift for affection,
            Throat lozenge: value1=50, value2=0
            Tapioca drink: value1=100, value2=0
            High cocoa chocolate: value1=150, value2=0
            Roll cake: value1=200, value2=0
        For gift for awakening gauge,
            Fan letter: value1=10, value2=0
            Single flower: value1=20, value2=0
            Hand cream: value1=30, value2=0
            Bath additive: value1=40, value2=0
            Preserved flower: value1=50, value2=0
        For money, value1=200, value2=0
    is_extend:
        is_extend=true for some Platinum/Selection/SSR tickets
        is_extend=false for everything else
    """
    __tablename__ = 'mst_item'

    mst_item_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    item_navi_type: Mapped[int]
    max_amount: Mapped[int]
    item_type: Mapped[int]
    sort_id: Mapped[int]
    value1: Mapped[int]
    value2: Mapped[int]
    is_extend: Mapped[bool]


class Item(Base):
    """Items obtained by user."""
    __tablename__ = 'item'

    item_id: Mapped[str] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                nullable=False)
    amount: Mapped[int]
    expire_date: Mapped[Optional[datetime]] = mapped_column(
        default=datetime(
            2099, 12, 31, 23, 59, 59, tzinfo=server_timezone
        ).astimezone(timezone.utc))

    user: Mapped['User'] = relationship(back_populates='items')
    mst_item: Mapped['MstItem'] = relationship(lazy='joined', innerjoin=True)


# class ExtendItem(Base):
#     """Extended info for items obtained by user."""
#     __tablename__ = 'extend_item'

#     extend_item_id: Mapped[int] = mapped_column(primary_key=True)
#     item_id: Mapped[str] = mapped_column(ForeignKey('item.item_id'))
#     expire_date: Mapped[Optional[datetime]] = mapped_column(
#         default=datetime(
#             2099, 12, 31, 23, 59, 59, tzinfo=server_timezone
#         ).astimezone(timezone.utc))


class MstRewardItem(Base):
    """Reward items given for completing certain tasks.

    is_new: Unused. is_new=False for all reward items
    """
    __tablename__ = 'mst_reward_item'

    mst_reward_item_id: Mapped[int] = mapped_column(primary_key=True)
    reward_type: Mapped[int]
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'), default=0,
                                insert_default=None)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'), default=0,
                                nullable=False)
    item_type: Mapped[int] = mapped_column(default=0)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   default=0, nullable=False)
    mst_achievement_id: Mapped[int] = mapped_column(default=0)
    amount: Mapped[int]
    is_new: Mapped[bool] = mapped_column(default=False)

    # mst_card: Mapped[Optional['MstCard']] = relationship(lazy='joined')
    mst_costume: Mapped['MstCostume'] = relationship(lazy='joined',
                                                     innerjoin=True)


class MstMemorial(Base):
    """Master table for memorials.

    1st memorial reward per idol:
        reward_type=4, reward_mst_item_id=405, reward_item_type=2,
        reward_amount=3000
    2nd memorial reward:
        reward_type=4, reward_mst_item_id=3, reward_item_type=1,
        reward_amount=25
    subsequent rewards:
        reward_type=4, reward_mst_item_id=3, reward_item_type=1,
        reward_amount=50
    """
    __tablename__ = 'mst_memorial'

    mst_memorial_id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[str]
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                nullable=False)
    release_affection: Mapped[int]
    number: Mapped[int]
    mst_reward_item_id = mapped_column(
        ForeignKey('mst_reward_item.mst_reward_item_id'), nullable=False)
    is_available: Mapped[bool]
    begin_date: Mapped[datetime]

    mst_reward_item: Mapped['MstRewardItem'] = relationship(lazy='joined',
                                                            innerjoin=True)


class Memorial(Base):
    """Memorial states for each user.

    released_date: Unused. released_date=null for all memorials
    """
    __tablename__ = 'memorial'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_memorial_id = mapped_column(ForeignKey('mst_memorial.mst_memorial_id'),
                                    primary_key=True)
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    released_date: Mapped[Optional[datetime]] = mapped_column(default=None)

    user: Mapped['User'] = relationship(back_populates='memorials')
    mst_memorial: Mapped['MstMemorial'] = relationship(lazy='joined',
                                                       innerjoin=True)


class Episode(Base):
    """Awakening story states for each card for each user.

    released_date: Unused. released_date=null for all episodes
    Reward for each N card:
        reward_type=4, reward_mst_item_id=3, reward_item_type=1,
        reward_amount=25
    Reward for each R, SR and SSR card:
        reward_type=4, reward_mst_item_id=3, reward_item_type=1,
        reward_amount=50
    """
    __tablename__ = 'episode'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                primary_key=True)
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    released_date: Mapped[Optional[datetime]] = mapped_column(default=None)
    mst_reward_item_id = mapped_column(
        ForeignKey('mst_reward_item.mst_reward_item_id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates='episodes')
    mst_card: Mapped['MstCard'] = relationship(lazy='joined', innerjoin=True)
    mst_reward_item: Mapped['MstRewardItem'] = relationship(lazy='joined',
                                                            innerjoin=True)


class MstTheaterCostumeBlog(Base):
    """Master table for costume blogs.

    reward_type=4, reward_mst_item_id=3, reward_item_type=1,
    reward_amount=50
    """
    __tablename__ = 'mst_theater_costume_blog'

    mst_theater_costume_blog_id: Mapped[int] = mapped_column(primary_key=True)
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                nullable=False)
    mst_reward_item_id = mapped_column(
        ForeignKey('mst_reward_item.mst_reward_item_id'), nullable=False)

    mst_card: Mapped['MstCard'] = relationship(lazy='joined', innerjoin=True)
    mst_reward_item: Mapped['MstRewardItem'] = relationship(lazy='joined',
                                                            innerjoin=True)


class CostumeAdv(Base):
    """Costume blog states for each user.

    released_date: Unused. released_date=null for all costume blogs
    """
    __tablename__ = 'costume_adv'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_theater_costume_blog_id = mapped_column(
        ForeignKey('mst_theater_costume_blog.mst_theater_costume_blog_id'),
        primary_key=True)
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    released_date: Mapped[Optional[datetime]] = mapped_column(default=None)

    user: Mapped['User'] = relationship(back_populates='costume_advs')
    mst_theater_costume_blog: Mapped['MstTheaterCostumeBlog'] = relationship(
        lazy='joined', innerjoin=True
    )


class MstGasha(Base):
    """Master table for gachas.

    currency_type_list: comma-separated currency types
                        1 = Paid jewels
                        2 = Gacha medals
                        6 = Free jewels
    """
    __tablename__ = 'mst_gasha'

    mst_gasha_id: Mapped[int] = mapped_column(primary_key=True)
    mst_gasha_ticket_item_id: Mapped[int] = mapped_column(default=0)
    name: Mapped[str]
    display_category: Mapped[int]
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime]
    currency_type_list: Mapped[Optional[str]]
    is_paid_jewel_only: Mapped[bool]
    draw1_jewel_value: Mapped[int]
    draw10_jewel_value: Mapped[int]
    draw1_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                      nullable=False)
    draw10_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                       default=0, nullable=False)
    daily_limit: Mapped[int]
    total_limit: Mapped[int]
    sr_passport: Mapped[int]
    ssr_passport: Mapped[int] = mapped_column(default=0)
    has_new_idol: Mapped[bool]
    has_limited: Mapped[bool] = mapped_column(default=False)
    notify_num: Mapped[int] = mapped_column(default=0)
    mst_gasha_kind_id: Mapped[int]
    mst_gasha_bonus_id: Mapped[int] = mapped_column(default=0)
    gasha_bonus_item_list: Mapped[Optional[str]] = mapped_column(default=None)
    gasha_bonus_mst_achievement_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    gasha_bonus_costume_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    is_limit: Mapped[bool]
    draw_point_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                           default=40, nullable=False)
    draw_point_max: Mapped[int] = mapped_column(default=300)
    pickup_signature: Mapped[str] = mapped_column(default='')
    pickup_gasha_card_list: Mapped[Optional[str]] = mapped_column(default=None)


class Gasha(Base):
    """Gacha info specific to each user."""
    __tablename__ = 'gasha'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_gasha_id = mapped_column(ForeignKey('mst_gasha.mst_gasha_id'),
                                 primary_key=True)
    today_count: Mapped[int] = mapped_column(default=0)
    total_count: Mapped[int] = mapped_column(default=0)
    draw_point: Mapped[int] = mapped_column(default=0)
    draw1_free_count: Mapped[int] = mapped_column(default=0)
    draw10_free_count: Mapped[int] = mapped_column(default=0)
    balloon: Mapped[int] = mapped_column(default=0)

    user: Mapped['User'] = relationship(back_populates='gashas')
    mst_gasha: Mapped['MstGasha'] = relationship(lazy='joined', innerjoin=True)
    draw1_item: Mapped['Item'] = relationship(
        secondary='mst_gasha',
        primaryjoin='and_(Gasha.user_id == Item.user_id, '
            + 'Gasha.mst_gasha_id == MstGasha.mst_gasha_id)',
        secondaryjoin='MstGasha.draw1_mst_item_id == Item.mst_item_id',
        viewonly=True, lazy='selectin')


class MstJob(Base):
    """Master table for jobs."""
    __tablename__ = 'mst_job'

    mst_job_id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[str]
    vitality_cost: Mapped[int] = mapped_column(default=20)
    job_type: Mapped[int] = mapped_column(default=1)
    idol_type: Mapped[int]
    reward_exp: Mapped[int] = mapped_column(default=143)
    reward_fan: Mapped[int] = mapped_column(default=40)
    reward_affection: Mapped[int] = mapped_column(default=9)
    reward_money: Mapped[int] = mapped_column(default=630)
    reward_live_ticket: Mapped[int] = mapped_column(default=20)
    begin_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2019, 3, 30, tzinfo=server_timezone
        ).astimezone(timezone.utc))
    end_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2099, 12, 31, 23, 59, 59, tzinfo=server_timezone
        ).astimezone(timezone.utc))


class MstSong(Base):
    """Master table for songs.
    
    song_unit_idol_id_list: comma-separated mst_idol_ids
    part_permitted_mst_idol_id_list: null or one mst_idol_id
    """
    __tablename__ = 'mst_song'

    mst_song_id: Mapped[int] = mapped_column(primary_key=True)
    song_type: Mapped[int]
    sort_id: Mapped[int]
    is_released_mv: Mapped[bool] = mapped_column(default=True)
    resource_id: Mapped[str]
    idol_type: Mapped[int]
    kind: Mapped[int]
    stage_id: Mapped[int]
    stage_ts_id: Mapped[int]
    bpm: Mapped[int] = mapped_column(default=234)
    is_visible: Mapped[bool] = mapped_column(default=True)
    apple_song_url: Mapped[str] = mapped_column(default='')
    google_song_url: Mapped[str] = mapped_column(default='')
    song_open_type: Mapped[int]
    song_open_type_value: Mapped[int]
    song_open_level: Mapped[int]
    song_unit_idol_id_list: Mapped[str]
    mst_song_unit_id: Mapped[int]
    idol_count: Mapped[int]
    icon_type: Mapped[int]
    unit_selection_type: Mapped[int]
    only_default_unit: Mapped[bool]
    only_extend: Mapped[bool]
    is_off_vocal_available: Mapped[bool]
    off_vocal_cue_sheet: Mapped[str]
    off_vocal_cue_name: Mapped[str]
    song_permit_control: Mapped[bool]
    permitted_mst_idol_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    permitted_mst_agency_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    extend_song_playable_status: Mapped[int]
    live_start_voice_mst_idol_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    is_enable_random: Mapped[bool]
    part_permitted_mst_idol_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    is_recommend: Mapped[bool] = mapped_column(default=False)
    song_parts_type: Mapped[int]

    mst_extend_song: Mapped['MstExtendSong'] = relationship(lazy='joined')


class MstExtendSong(Base):
    """Master table for extend songs.

    song_unit_idol_id_list: comma-separated mst_idol_ids
    """
    __tablename__ = 'mst_extend_song'

    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                primary_key=True)
    resource_id: Mapped[str]
    kind: Mapped[int]
    stage_id: Mapped[int]
    stage_ts_id: Mapped[int]
    mst_song_unit_id: Mapped[int]
    song_unit_idol_id_list: Mapped[str]
    unit_selection_type: Mapped[int]
    unit_song_type: Mapped[int]
    icon_type: Mapped[int]
    idol_count: Mapped[int]
    extend_type: Mapped[int]
    filter_type: Mapped[int]
    song_open_type: Mapped[int] = mapped_column(default=0)
    song_open_type_value: Mapped[int] = mapped_column(default=0)
    song_open_level: Mapped[int] = mapped_column(default=0)


class Song(Base):
    """Song info specific to each user."""
    __tablename__ = 'song'

    song_id: Mapped[str] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey('user.user_id'), nullable=False)
    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                nullable=False)
    is_released_horizontal_mv: Mapped[bool] = mapped_column(default=False)
    is_released_vertical_mv: Mapped[bool] = mapped_column(default=False)
    is_cleared: Mapped[bool] = mapped_column(default=False)
    first_cleared_date: Mapped[datetime] = mapped_column(
        default=datetime(1, 1, 1))
    is_played: Mapped[bool] = mapped_column(default=False)
    lp: Mapped[int] = mapped_column(default=0)
    is_disable: Mapped[bool] = mapped_column(default=False)
    is_off_vocal_released: Mapped[bool] = mapped_column(default=False)
    is_new: Mapped[bool] = mapped_column(default=True)

    user: Mapped['User'] = relationship(back_populates='songs')
    mst_song: Mapped['MstSong'] = relationship(lazy='joined', innerjoin=True)
    courses: Mapped[List['Course']] = relationship(
        uselist=True,
        primaryjoin='and_(Song.user_id == Course.user_id, '
            + 'Song.mst_song_id == Course.mst_song_id)',
        foreign_keys=[user_id, mst_song_id],
        viewonly=True, lazy='selectin')


class MstCourse(Base):
    """Master table for course info for each song.

    course_id: 
        1=Solo 2M?
        2=2M?
        3=Solo 2M+
        4=4M
        5=6M
        6=MM
    TODO: add score/combo/clear rank requirements?
    """
    __tablename__ = 'mst_course'

    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                primary_key=True)
    course_id: Mapped[int] = mapped_column(primary_key=True)
    cost: Mapped[int]
    level: Mapped[int]
    appeal: Mapped[int]
    notes: Mapped[int]


class Course(Base):
    """Course info specific to each user."""
    __tablename__ = 'course'
    __table_args__ = (
        ForeignKeyConstraint(
            ['mst_song_id', 'course_id'],
            ['mst_course.mst_song_id', 'mst_course.course_id']
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_song_id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(default=0)
    combo: Mapped[int] = mapped_column(default=0)
    clear: Mapped[int] = mapped_column(default=0)
    score_rank: Mapped[int] = mapped_column(default=0)
    combo_rank: Mapped[int] = mapped_column(default=0)
    clear_rank: Mapped[int] = mapped_column(default=0)
    is_released: Mapped[bool]

    user: Mapped['User'] = relationship(back_populates='courses')
    mst_course: Mapped['MstCourse'] = relationship(lazy='joined',
                                                   innerjoin=True)


class Unit(Base):
    """Unit info specific to each user."""
    __tablename__ = 'unit'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    unit_num: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    user: Mapped['User'] = relationship(back_populates='units')
    unit_idols: Mapped[List['UnitIdol']] = relationship(
        lazy='selectin', order_by='[UnitIdol.position]')


class UnitIdol(Base):
    """Idol list (selected card & costume) for each unit for each user."""
    __tablename__ = 'unit_idol'
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'unit_num'],
            ['unit.user_id', 'unit.unit_num']
        ),
    )

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    unit_num: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    card_id = mapped_column(ForeignKey('card.card_id'), nullable=False)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)
    mst_lesson_wear_id = mapped_column(
        ForeignKey('mst_lesson_wear.mst_lesson_wear_id'), nullable=False)
    costume_is_random: Mapped[bool] = mapped_column(default=False)
    costume_random_type: Mapped[int] = mapped_column(default=0)


class SongUnit(Base):
    """Unit info specific to each song for each user."""
    __tablename__ = 'song_unit'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                primary_key=True)
    unit_song_type: Mapped[int]
    is_new: Mapped[bool] = mapped_column(default=True)

    user: Mapped['User'] = relationship(back_populates='song_units')
    song_unit_idols: Mapped[List['SongUnitIdol']] = relationship(
        lazy='selectin', order_by='[SongUnitIdol.position]')


class SongUnitIdol(Base):
    """Idol list (selected card & costume) for each song unit for each user."""
    __tablename__ = 'song_unit_idol'
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'mst_song_id'],
            ['song_unit.user_id', 'song_unit.mst_song_id']
        ),
    )

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    mst_song_id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    card_id = mapped_column(ForeignKey('card.card_id'), nullable=False)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)
    mst_lesson_wear_id = mapped_column(
        ForeignKey('mst_lesson_wear.mst_lesson_wear_id'), nullable=False)
    costume_is_random: Mapped[bool] = mapped_column(default=False)
    costume_random_type: Mapped[int] = mapped_column(default=0)


class MstMainStory(Base):
    """Master table for main stories.

    mst_idol_id_list: comma-separated mst_idol_ids
    """
    __tablename__ = 'mst_main_story'

    mst_main_story_id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]
    mst_idol_id_list: Mapped[str]
    release_level: Mapped[int]
    release_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                    nullable=False)
    reward_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                   nullable=False)
    intro_contact_mst_idol_id = mapped_column(
        ForeignKey('mst_idol.mst_idol_id'), nullable=False)
    blog_contact_mst_idol_id = mapped_column(
        ForeignKey('mst_idol.mst_idol_id'), nullable=False)

    reward_song: Mapped['MstSong'] = relationship(
        foreign_keys=reward_song_id,
        viewonly=True, lazy='joined', innerjoin=True)
    mst_reward_items: Mapped[List['MstRewardItem']] = relationship(
        secondary='mst_main_story_reward',
        viewonly=True, lazy='selectin')


class MstMainStoryChapter(Base):
    """Master table for main story chapters."""
    __tablename__ = 'mst_main_story_chapter'

    mst_main_story_id = mapped_column(
        ForeignKey('mst_main_story.mst_main_story_id'), primary_key=True)
    chapter: Mapped[int] = mapped_column(primary_key=True)


class MstMainStoryReward(Base):
    """Master table for main story reward items.

    For mst_main_story_id=41:
        reward_type_list=4,4,8
        reward_mst_item_id_list=3,705,0
        reward_item_type_list=1,5,0
        reward_mst_costume_id_list=0,0,102
        reward_amount_list=50,1,1
    For other main stories:
        reward_type_list=4
        reward_mst_item_id_list=3
        reward_item_type_list=1
        reward_mst_costume_id_list=0
        reward_amount_list=50
    """
    __tablename__ = 'mst_main_story_reward'

    mst_main_story_id = mapped_column(
        ForeignKey('mst_main_story.mst_main_story_id'), primary_key=True)
    mst_reward_item_id = mapped_column(
        ForeignKey('mst_reward_item.mst_reward_item_id'), primary_key=True)


class MainStoryChapter(Base):
    """Main story chapter states specific to each user."""
    __tablename__ = 'main_story_chapter'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_main_story_id',
                'chapter'
            ],
            [
                'mst_main_story_chapter.mst_main_story_id',
                'mst_main_story_chapter.chapter'
            ]
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_main_story_id: Mapped[int] = mapped_column(primary_key=True)
    chapter: Mapped[int] = mapped_column(primary_key=True)
    released_date: Mapped[Optional[datetime]] = mapped_column(default=None)
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)

    user: Mapped['User'] = relationship(back_populates='main_story_chapters')
    mst_main_story: Mapped['MstMainStory'] = relationship(
        secondary='mst_main_story_chapter', lazy='joined', innerjoin=True)


class MstTheaterRoomStatus(Base):
    """Master table for theater room status.

    TODO: Some columns for theater_room_status seem to be designed for
          other purposes. API is returning everything using a common
          data structure. May need to refactor later.
    """
    __tablename__ = 'mst_theater_room_status'

    mst_room_id: Mapped[int]
    theater_contact_category_type: Mapped[int]
    resource_id: Mapped[str]
    mst_theater_contact_schedule_id: Mapped[int] = mapped_column(default=0)
    mst_theater_contact_id: Mapped[int] = mapped_column(default=0,
                                                        primary_key=True)
    mst_theater_main_story_id: Mapped[int] = mapped_column(default=0,
                                                           primary_key=True)
    mst_theater_guest_main_story_id: Mapped[int] = mapped_column(
        default=0, primary_key=True)
    guest_main_story_has_intro: Mapped[bool] = mapped_column(default=False)
    mst_guest_main_story_id: Mapped[int] = mapped_column(default=0)
    mst_theater_blog_id: Mapped[int] = mapped_column(default=0,
                                                     primary_key=True)
    mst_theater_costume_blog_id: Mapped[int] = mapped_column(default=0,
                                                             primary_key=True)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)
    mst_theater_event_story_id: Mapped[int] = mapped_column(default=0,
                                                            primary_key=True)
    mst_event_story_id = mapped_column(
        ForeignKey('mst_event_story.mst_event_story_id'), default=0,
        nullable=False)
    mst_event_id = mapped_column(ForeignKey('mst_event.mst_event_id'),
                                 default=0, nullable=False)

    mst_theater_room_idols: Mapped[List['MstTheaterRoomIdol']] = relationship(
        lazy='selectin')


class MstTheaterRoomIdol(Base):
    """Master table for room idol list for each theater room status."""
    __tablename__ = 'mst_theater_room_idol'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_theater_contact_id',
                'mst_theater_main_story_id',
                'mst_theater_guest_main_story_id',
                'mst_theater_blog_id',
                'mst_theater_costume_blog_id',
                'mst_theater_event_story_id'
            ],
            [
                'mst_theater_room_status.mst_theater_contact_id',
                'mst_theater_room_status.mst_theater_main_story_id',
                'mst_theater_room_status.mst_theater_guest_main_story_id',
                'mst_theater_room_status.mst_theater_blog_id',
                'mst_theater_room_status.mst_theater_costume_blog_id',
                'mst_theater_room_status.mst_theater_event_story_id'
            ]
        ),
    )

    mst_theater_contact_id: Mapped[int] = mapped_column(default=0,
                                                        primary_key=True)
    mst_theater_main_story_id: Mapped[int] = mapped_column(default=0,
                                                           primary_key=True)
    mst_theater_guest_main_story_id: Mapped[int] = mapped_column(
        default=0, primary_key=True)
    mst_theater_blog_id: Mapped[int] = mapped_column(default=0,
                                                     primary_key=True)
    mst_theater_costume_blog_id: Mapped[int] = mapped_column(default=0,
                                                             primary_key=True)
    mst_theater_event_story_id: Mapped[int] = mapped_column(default=0,
                                                            primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                primary_key=True)
    position_id: Mapped[str]
    motion_id: Mapped[str]
    reaction_id: Mapped[str] = mapped_column(default='')
    reaction_id_2: Mapped[str] = mapped_column(default='')


class MstMainStoryContactStatus(Base):
    """Master table for main story contact statuses."""
    __tablename__ = 'mst_main_story_contact_status'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_theater_contact_id',
                'mst_theater_main_story_id',
                'mst_theater_guest_main_story_id',
                'mst_theater_blog_id',
                'mst_theater_costume_blog_id',
                'mst_theater_event_story_id'
            ],
            [
                'mst_theater_room_status.mst_theater_contact_id',
                'mst_theater_room_status.mst_theater_main_story_id',
                'mst_theater_room_status.mst_theater_guest_main_story_id',
                'mst_theater_room_status.mst_theater_blog_id',
                'mst_theater_room_status.mst_theater_costume_blog_id',
                'mst_theater_room_status.mst_theater_event_story_id'
            ]
        ),
    )

    mst_theater_contact_id: Mapped[int] = mapped_column(default=0,
                                                        primary_key=True)
    mst_theater_main_story_id: Mapped[int] = mapped_column(default=0,
                                                           primary_key=True)
    mst_theater_guest_main_story_id: Mapped[int] = mapped_column(
        default=0, primary_key=True)
    mst_theater_blog_id: Mapped[int] = mapped_column(default=0,
                                                     primary_key=True)
    mst_theater_costume_blog_id: Mapped[int] = mapped_column(default=0,
                                                             primary_key=True)
    mst_theater_event_story_id: Mapped[int] = mapped_column(default=0,
                                                            primary_key=True)
    mst_main_story_id = mapped_column(
        ForeignKey('mst_main_story.mst_main_story_id'), nullable=False)
    duration: Mapped[int]

    mst_theater_room_status: Mapped['MstTheaterRoomStatus'] = relationship(
        lazy='joined', innerjoin=True)


class MstEventContactStatus(Base):
    """Master table for event contact statuses."""
    __tablename__ = 'mst_event_contact_status'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_theater_contact_id',
                'mst_theater_main_story_id',
                'mst_theater_guest_main_story_id',
                'mst_theater_blog_id',
                'mst_theater_costume_blog_id',
                'mst_theater_event_story_id'
            ],
            [
                'mst_theater_room_status.mst_theater_contact_id',
                'mst_theater_room_status.mst_theater_main_story_id',
                'mst_theater_room_status.mst_theater_guest_main_story_id',
                'mst_theater_room_status.mst_theater_blog_id',
                'mst_theater_room_status.mst_theater_costume_blog_id',
                'mst_theater_room_status.mst_theater_event_story_id'
            ]
        ),
    )

    mst_theater_contact_id: Mapped[int] = mapped_column(default=0,
                                                        primary_key=True)
    mst_theater_main_story_id: Mapped[int] = mapped_column(default=0,
                                                           primary_key=True)
    mst_theater_guest_main_story_id: Mapped[int] = mapped_column(
        default=0, primary_key=True)
    mst_theater_blog_id: Mapped[int] = mapped_column(default=0,
                                                     primary_key=True)
    mst_theater_costume_blog_id: Mapped[int] = mapped_column(default=0,
                                                             primary_key=True)
    mst_theater_event_story_id: Mapped[int] = mapped_column(default=0,
                                                            primary_key=True)
    mst_event_id: Mapped[int]
    duration: Mapped[int]

    mst_theater_room_status: Mapped['MstTheaterRoomStatus'] = relationship(
        lazy='joined', innerjoin=True)


class MstAwakeningConfig(Base):
    """Awakening config."""
    __tablename__ = 'mst_awakening_config'

    rarity: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                default=0, insert_default=None)

    mst_awakening_config_items: Mapped[
        List['MstAwakeningConfigItem']] = relationship(lazy='selectin')


class MstAwakeningConfigItem(Base):
    """Required items for awakening."""
    __tablename__ = 'mst_awakening_config_item'
    __table_args__ = (
        ForeignKeyConstraint(
            ['rarity', 'idol_type'],
            ['mst_awakening_config.rarity', 'mst_awakening_config.idol_type']
        ),
    )

    rarity: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                primary_key=True)
    amount: Mapped[int]


class MstMasterLesson2Config(Base):
    """Master lesson config."""
    __tablename__ = 'mst_master_lesson2_config'

    rarity: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)

    mst_master_lesson2_config_items: Mapped[
        List['MstMasterLesson2ConfigItem']] = relationship(lazy='selectin')


class MstMasterLesson2ConfigItem(Base):
    """Required master pieces for master lessons."""
    __tablename__ = 'mst_master_lesson2_config_item'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'rarity',
                'idol_type'
            ],
            [
                'mst_master_lesson2_config.rarity',
                'mst_master_lesson2_config.idol_type'
            ]
        ),
    )

    rarity: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                primary_key=True)
    amount: Mapped[int]


class MstExMasterLessonConfig(Base):
    """Required items for ex master lessons.

    ex_type:
        2=PST (Ranking), 3=PST (Event Pt), 4=FES, 5=1st, 6=Ex
    amount: comma-separated values, one for each master rank
    """
    __tablename__ = 'mst_ex_master_lesson_config'

    ex_type: Mapped[int] = mapped_column(primary_key=True)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                nullable=False)
    amount: Mapped[str]
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                default=0, insert_default=None)


class MstLessonMoneyConfig(Base):
    """Required money per ticket for lessons."""
    __tablename__ = 'mst_lesson_money_config'

    rarity: Mapped[int] = mapped_column(primary_key=True)
    money: Mapped[int]
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                nullable=False)


class MstLessonSkillLevelUpConfig(Base):
    """Required 'skill EXP' for each skill level for guaranteed level up.

    skill_level: target skill level
    rarity: card rarity
    value: required 'skill EXP'
    'Skill EXP' per ticket is defined by mst_item's value2:
        Lesson ticket N=0
        Lesson ticket R=300
        Lesson ticket SR=1000
        Lesson ticket SSR=2000
    """
    __tablename__ = 'mst_lesson_skill_level_up_config'

    skill_level: Mapped[int] = mapped_column(primary_key=True)
    rarity: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]


class MstLessonWearConfig(Base):
    """Available lesson wear in system settings."""
    __tablename__ = 'mst_lesson_wear_config'

    mst_lesson_wear_setting_id: Mapped[int] = mapped_column(primary_key=True)
    mst_lesson_wear_group_id_list: Mapped[int]


class LessonWearConfig(Base):
    """Lesson wear chosen by user."""
    __tablename__ = 'lesson_wear_config'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_lesson_wear_setting_id = mapped_column(
        ForeignKey('mst_lesson_wear_config.mst_lesson_wear_setting_id'),
        primary_key=True)


class MstComicMenu(Base):
    """Comic menu list (unused in zh/ko versions)."""
    __tablename__ = 'mst_comic_menu'

    mst_comic_menu_id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    resource_id: Mapped[str]
    enable_button: Mapped[bool]


class MstTrainingUnit(Base):
    """Required songs and idols for anniversary training mission.

    idol_id_list: comma-separated mst_idol_ids
    """
    __tablename__ = 'mst_training_unit'

    mst_song_unit_id: Mapped[int] = mapped_column(primary_key=True)
    idol_id_list: Mapped[str]


class MstMasterLessonFiveConfig(Base):
    """Master rank 5 lesson config.

    ex_type: 0=Normal, 4=FES
    """
    __tablename__ = 'mst_master_lesson_five_config'

    ex_type: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)

    mst_master_lesson_five_config_items: Mapped[
        List['MstMasterLessonFiveConfigItem']] = relationship(lazy='selectin')


class MstMasterLessonFiveConfigItem(Base):
    """Required items for master rank 5 lessons."""
    __tablename__ = 'mst_master_lesson_five_config_item'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'ex_type',
                'idol_type'
            ],
            [
                'mst_master_lesson_five_config.ex_type',
                'mst_master_lesson_five_config.idol_type'
            ]
        ),
    )

    ex_type: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                primary_key=True)
    amount: Mapped[int]


class MstTitleImage(Base):
    """Available title images in system settings.

    title_image_type: 2=event, 3=others
    """
    __tablename__ = 'mst_title_image'

    mst_title_image_id: Mapped[int] = mapped_column(primary_key=True)
    title_image_type: Mapped[int]
    sort_id: Mapped[int]
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime]


class MstGameSetting(Base):
    """Master table for game settings.

    lounge_chat_fetch_cycle: comma-separated values
    function_release_id_list: comma-separated values
    """
    __tablename__ = 'mst_game_setting'

    mst_game_setting_id: Mapped[int] = mapped_column(primary_key=True)
    rank5_skill_level_max: Mapped[int]
    awakening_bonus_level: Mapped[int]
    max_master_rank: Mapped[int]
    master_rank_bonus: Mapped[int]
    card_lv_base: Mapped[int]
    card_lv_diff: Mapped[int]
    user_lv_base: Mapped[int]
    user_lv_diff: Mapped[int]
    recover_jewel_amount: Mapped[int]
    recover_jewel_begin_date: Mapped[datetime]
    recover_jewel_end_date: Mapped[datetime]
    continue_jewel_amount: Mapped[int]
    continue_jewel_begin_date: Mapped[datetime]
    continue_jewel_end_date: Mapped[datetime]
    enable_lounge: Mapped[bool]
    rehearsal_cost: Mapped[int]
    live_ticket_scale: Mapped[int]
    enable_sale: Mapped[bool]
    enable_sales_costume: Mapped[bool]
    enable_gasha_exchange_limit_point: Mapped[bool]
    enable_event_shop: Mapped[bool]
    enable_unit: Mapped[bool]
    overflow_date: Mapped[datetime]
    enable_song_unit: Mapped[bool]
    enable_song_unit_duo: Mapped[bool]
    enable_song_full_random: Mapped[bool]
    enable_song_song_random: Mapped[bool]
    enable_a1st_card_shop: Mapped[bool]
    enable_training: Mapped[bool]
    lounge_chat_fetch_cycle: Mapped[str]
    enable_comic_button: Mapped[bool]
    comic_button_url: Mapped[str]
    enable_item_shop: Mapped[bool]
    enable_release_connection: Mapped[bool]
    board_write_limit_level: Mapped[int]
    un_lock_song_jewel_amount: Mapped[int]
    un_lock_song_jewel_begin_date: Mapped[datetime]
    un_lock_song_jewel_end_date: Mapped[datetime]
    mst_item_id_with_type_master_key: Mapped[int]
    profile_achievement_list_limit_count: Mapped[int]
    enable_thank_you_mode: Mapped[bool]
    enable_new_gasha_view: Mapped[bool]
    enable_flower_stand_multi: Mapped[bool]
    enable_n_t4: Mapped[bool]
    function_release_id_list: Mapped[str]
    default_release_all_song_difficulty_lv: Mapped[int]
    max_training_point: Mapped[int]


class MstLoadingCharacter(Base):
    """Loading character list."""
    __tablename__ = 'mst_loading_character'

    resource_id: Mapped[str] = mapped_column(primary_key=True)
    weight: Mapped[int]
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime]


class MstCampaign(Base):
    """Master table for campaigns."""
    __tablename__ = 'mst_campaign'

    mst_campain_id: Mapped[int] = mapped_column(primary_key=True)  # Sic
    type: Mapped[int]
    value: Mapped[int] = mapped_column(default=0)
    footer_button: Mapped[int]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]


class Campaign(Base):
    """Campaigns available for each user."""
    __tablename__ = 'campaign'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_campain_id = mapped_column(ForeignKey('mst_campaign.mst_campain_id'),
                                   primary_key=True)

    user: Mapped['User'] = relationship(back_populates='campaigns')
    mst_campaign: Mapped['MstCampaign'] = relationship(lazy='joined',
                                                       innerjoin=True)


class GashaMedal(Base):
    """Gacha medals and expiry dates for each user."""
    __tablename__ = 'gasha_medal'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    point_amount: Mapped[int] = mapped_column(default=0)

    user: Mapped['User'] = relationship(back_populates='gasha_medal')
    gasha_medal_expire_dates: Mapped[
        List['GashaMedalExpireDate']] = relationship(
            order_by='[GashaMedalExpireDate.expire_date]')


class GashaMedalExpireDate(Base):
    """Gacha medal expiry dates for each user."""
    __tablename__ = 'gasha_medal_expire_date'

    user_id = mapped_column(ForeignKey('gasha_medal.user_id'),
                            primary_key=True)
    expire_date: Mapped[datetime] = mapped_column(
        primary_key=True, default=datetime.now(timezone.utc))


class Jewel(Base):
    """Jewels for each user."""
    __tablename__ = 'jewel'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    free_jewel_amount: Mapped[int] = mapped_column(default=0)
    paid_jewel_amount: Mapped[int] = mapped_column(default=0)

    user: Mapped['User'] = relationship(back_populates='jewel')


# class MstRecordTime(Base):
#     """Master table for user actions that require tracking (e.g. tutorials)."""
#     __tablename__ = 'mst_record_time'

#     kind: Mapped[str] = mapped_column(primary_key=True)


class RecordTime(Base):
    """Recorded times for actions performed by each user."""
    __tablename__ = 'record_time'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    kind: Mapped[str] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))

    user: Mapped['User'] = relationship(back_populates='record_times')


class MstTopics(Base):
    """Master table for topics (text/images for loading screen)."""
    __tablename__ = 'mst_topics'

    mst_topics_id: Mapped[int] = mapped_column(primary_key=True)
    topics_category: Mapped[int]
    topics_type: Mapped[int]
    mst_topics_icon_id: Mapped[int]
    number: Mapped[int]
    release_date: Mapped[datetime]


class MstEvent(Base):
    """Master table for events."""
    __tablename__ = 'mst_event'

    mst_event_id: Mapped[int] = mapped_column(primary_key=True)
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime]
    page_begin_date: Mapped[datetime]
    page_end_date: Mapped[datetime]
    boost_begin_date: Mapped[datetime] = mapped_column(
        default=datetime(1, 1, 1))
    boost_end_date: Mapped[datetime] = mapped_column(default=datetime(1, 1, 1))
    event_type: Mapped[int]
    cue_sheet: Mapped[str] = mapped_column(default='')
    cue_name: Mapped[str] = mapped_column(default='')
    cue_sheet2: Mapped[str] = mapped_column(default='')
    cue_name2: Mapped[str] = mapped_column(default='')
    ending_cue_sheet: Mapped[str] = mapped_column(default='')
    ending_cue_name: Mapped[str] = mapped_column(default='')
    appeal_type: Mapped[int] = mapped_column(default=0)
    is_board_open: Mapped[bool] = mapped_column(default=False)


class MstEventTalkStory(Base):
    """Master table for each episode of MILLION LIVE WORKING stories.
    
    mst_event_talk_speaker_id: comma-separated mst_idol_ids
    TODO: normalize lists if required
    """
    __tablename__ = 'mst_event_talk_story'

    mst_event_talk_story_id: Mapped[int] = mapped_column(primary_key=True)
    episode: Mapped[int]
    release_event_point: Mapped[int]
    mst_event_talk_speaker_id: Mapped[str]
    bg_id: Mapped[str]
    thumbnail_id: Mapped[str]
    begin_date: Mapped[datetime]


class EventTalkStory(Base):
    """MILLION LIVE WORKING story episode states for each user."""
    __tablename__ = 'event_talk_story'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_event_talk_story_id = mapped_column(
        ForeignKey('mst_event_talk_story.mst_event_talk_story_id'),
        primary_key=True)
    released_date: Mapped[datetime] = mapped_column(default=datetime(1, 1, 1))
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)


class MstEventTalkCallText(Base):
    """Master table for MILLION LIVE WORKING story call text."""
    __tablename__ = 'mst_event_talk_call_text'

    mst_event_talk_call_text_id: Mapped[int] = mapped_column(primary_key=True)
    speaker_id: Mapped[int]


class MstEventTalkControl(Base):
    """Master table for each day of MILLION LIVE WORKING stories.

    reward_type=4, reward_mst_item_id=3, reward_item_type=1,
    reward_amount=25
    """
    __tablename__ = 'mst_event_talk_control'

    mst_event_talk_control_id: Mapped[int] = mapped_column(primary_key=True)
    mst_event_id = mapped_column(ForeignKey('mst_event.mst_event_id'),
                                 nullable=False)
    event_day: Mapped[int]
    mst_event_schedule_id: Mapped[int]
    release_event_point: Mapped[int] = mapped_column(default=400)
    release_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                    default=3001, nullable=False)
    release_item_amount: Mapped[int] = mapped_column(default=1)
    reward_type: Mapped[int] = mapped_column(default=4)
    reward_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                       default=3, nullable=False)
    reward_item_type: Mapped[int] = mapped_column(default=1)
    reward_amount: Mapped[int] = mapped_column(default=25)


class MstMissionSchedule(Base):
    """'Master table for mission schedules."""
    __tablename__ = 'mst_mission_schedule'

    mst_mission_schedule_id: Mapped[int] = mapped_column(primary_key=True)
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2099, 12, 31, 23, 59, 59, tzinfo=server_timezone
        ).astimezone(timezone.utc))
    mission_type: Mapped[int]


class MstPanelMissionSheet(Base):
    """Master table for panel mission sheets."""
    __tablename__ = 'mst_panel_mission_sheet'

    mst_panel_mission_sheet_id: Mapped[int] = mapped_column(primary_key=True)
    begin_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2018, 1, 1, tzinfo=server_timezone
        ).astimezone(timezone.utc))
    end_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2099, 12, 31, 23, 59, 59, tzinfo=server_timezone
        ).astimezone(timezone.utc))
    reward_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                       nullable=False)
    reward_item_type_id: Mapped[int]
    reward_amount: Mapped[int]
    reward_mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'),
                                       default=0, insert_default=None)
    reward_mst_achievement_id: Mapped[int]
    reward_mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                       default=0, insert_default=None)
    reward_resource_id: Mapped[str]


class PanelMissionSheet(Base):
    """Panel mission sheet states for each user."""
    __tablename__ = 'panel_mission_sheet'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    current_mst_panel_mission_sheet_id = mapped_column(
        ForeignKey('mst_panel_mission_sheet.mst_panel_mission_sheet_id'),
        default=1, nullable=False)
    current_panel_mission_sheet_state: Mapped[int] = mapped_column(default=1)

    user: Mapped['User'] = relationship(back_populates='mission_summary')


class MstMission(Base):
    """Master table for missions.

    premise_mst_mission_id_list: comma-separated mst_mission_ids
    reward_mst_item_id_list: comma-separated mst_item_ids
    reward_item_type_id_list: comma-separated values
    reward_amount_list: comma-separated values
    reward_mst_card_id_list: comma-separated mst_card_ids
    reward_mst_achievement_id_list: comma-separated mst_achievement_ids
    reward_mst_song_id_list: comma-separated mst_song_ids
    reward_resource_id_list: comma-separated values
    TODO: normalize lists if required
    """
    __tablename__ = 'mst_mission'

    mst_mission_id: Mapped[int] = mapped_column(default=0, primary_key=True)
    mst_panel_mission_id: Mapped[int] = mapped_column(default=0,
                                                      primary_key=True)
    mst_idol_mission_id: Mapped[int] = mapped_column(default=0,
                                                     primary_key=True)
    mission_type: Mapped[int]
    mst_mission_class_id: Mapped[int]
    goal: Mapped[int]
    option: Mapped[str]
    option2: Mapped[str]
    premise_mst_mission_id_list: Mapped[Optional[str]]
    reward_mst_item_id_list: Mapped[str] = mapped_column(default='0')
    reward_item_type_id_list: Mapped[str] = mapped_column(default='0')
    reward_amount_list: Mapped[str] = mapped_column(default='1')
    reward_mst_card_id_list: Mapped[str] = mapped_column(default='0')
    reward_mst_achievement_id_list: Mapped[str] = mapped_column(default='0')
    reward_mst_song_id_list: Mapped[str] = mapped_column(default='0')
    reward_resource_id_list: Mapped[str] = mapped_column(default='')
    sort_id: Mapped[int]
    jump_type: Mapped[str]
    mission_operation_label: Mapped[str]
    mst_mission_schedule_id = mapped_column(
        ForeignKey('mst_mission_schedule.mst_mission_schedule_id'), default=0,
        insert_default=None)
    mst_panel_mission_sheet_id = mapped_column(
        ForeignKey('mst_panel_mission_sheet.mst_panel_mission_sheet_id'),
        default=0, insert_default=None)


class Mission(Base):
    """Mission states for each user."""
    __tablename__ = 'mission'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_mission_id',
                'mst_panel_mission_id',
                'mst_idol_mission_id'
            ],
            [
                'mst_mission.mst_mission_id',
                'mst_mission.mst_panel_mission_id',
                'mst_mission.mst_idol_mission_id'
            ]
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_mission_id: Mapped[int] = mapped_column(primary_key=True)
    mst_panel_mission_id: Mapped[int] = mapped_column(primary_key=True)
    mst_idol_mission_id: Mapped[int] = mapped_column(primary_key=True)
    create_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    finish_date: Mapped[datetime] = mapped_column(default=datetime(1, 1, 1))
    progress: Mapped[int] = mapped_column(default=0)
    mission_state: Mapped[int] = mapped_column(default=1)
    song_idol_type: Mapped[int] = mapped_column(default=0)


class MstSpecialStory(Base):
    """Master table for special stories.

    mst_idol_id_list: comma-separated mst_idol_ids
    TODO: normalize lists if required
    """
    __tablename__ = 'mst_special_story'

    mst_special_story_id: Mapped[int] = mapped_column(primary_key=True)
    mst_special_id: Mapped[int]
    mst_idol_id_list: Mapped[Optional[str]]
    cue_name: Mapped[str]
    scenario_id: Mapped[str]
    number: Mapped[int]
    reward_type: Mapped[Optional[int]]
    reward_amount: Mapped[Optional[int]]
    story_type: Mapped[int]
    mst_card_id = mapped_column(ForeignKey('mst_card.mst_card_id'), default=0,
                                insert_default=None)
    special_mv_mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                           default=0, insert_default=None)
    category: Mapped[int]
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime] = mapped_column(
        default=datetime(
            2099, 12, 31, tzinfo=server_timezone
        ).astimezone(timezone.utc))


class MstSpecialMVUnitIdol(Base):
    """Master table for unit idols in special MVs."""
    __tablename__ = 'mst_special_mv_unit_idol'

    mst_special_story_id = mapped_column(
        ForeignKey('mst_special_story.mst_special_story_id'), primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                primary_key=True)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)


class SpecialStory(Base):
    """Special story states for each user."""
    __tablename__ = 'special_story'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_special_story_id = mapped_column(
        ForeignKey('mst_special_story.mst_special_story_id'), primary_key=True)
    is_released: Mapped[bool] = mapped_column(default=True)
    is_read: Mapped[bool] = mapped_column(default=False)


class MstEventStory(Base):
    """Master table for event stories.

    mst_idol_id_list: comma-separated mst_idol_ids
    reward_type_list: comma-separated values
    reward_mst_item_id_list: comma-separated mst_item_ids
    reward_item_type_list: comma-separated values
    reward_amount_list: comma-separated values
    For mst_event_story_id=168-175:
        reward_type_list=4,4
        reward_mst_item_id_list=3,0
        reward_item_type_list=1,0
        reward_amount_list=50,1-8
    For other event stories:
        reward_type_list=4
        reward_mst_item_id_list=3
        reward_item_type_list=1
        reward_amount_list=50
    TODO: normalize lists if required
    """
    __tablename__ = 'mst_event_story'

    mst_event_story_id: Mapped[int] = mapped_column(primary_key=True)
    mst_idol_id_list: Mapped[str]
    mst_event_id: Mapped[int]
    event_type: Mapped[int]
    number: Mapped[int]
    has_mv: Mapped[bool]
    has_mv_twin: Mapped[bool] = mapped_column(default=False)
    event_story_mv_mst_song_id = mapped_column(
        ForeignKey('mst_song.mst_song_id'), default=0, insert_default=None)
    release_event_point: Mapped[int]
    begin_date: Mapped[datetime]
    end_date: Mapped[datetime]
    page_begin_date: Mapped[datetime]
    page_end_date: Mapped[datetime]
    reward_type_list: Mapped[str]
    reward_mst_item_id_list: Mapped[str]
    reward_item_type_list: Mapped[str]
    reward_amount_list: Mapped[str]
    release_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                        nullable=False)
    release_item_amount: Mapped[int]
    release_item_begin_date: Mapped[datetime]
    before_scenario_id: Mapped[str]


class MstEventStoryMVUnitIdol(Base):
    """Master table for unit idols in event story MVs."""
    __tablename__ = 'mst_event_story_mv_unit_idol'

    mst_event_story_id = mapped_column(
        ForeignKey('mst_event_story.mst_event_story_id'), primary_key=True)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                primary_key=True)
    mst_costume_id = mapped_column(ForeignKey('mst_costume.mst_costume_id'),
                                   nullable=False)


class EventStory(Base):
    """Event story states for each user."""
    __tablename__ = 'event_story'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_event_story_id = mapped_column(
        ForeignKey('mst_event_story.mst_event_story_id'), primary_key=True)
    released_date: Mapped[datetime] = mapped_column(default=datetime(1, 1, 1))
    is_released: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)


class MstEventMemory(Base):
    """Master table for event memories."""
    __tablename__ = 'mst_event_memory'

    mst_event_memory_id: Mapped[int] = mapped_column(primary_key=True)
    mst_event_id: Mapped[int]
    release_mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                        default=3001, nullable=False)
    release_item_amount: Mapped[int] = mapped_column(default=1)
    release_item_begin_date: Mapped[datetime]
    event_memory_type: Mapped[int]
    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'), default=0,
                                insert_default=None)
    mst_song_unit_id: Mapped[int] = mapped_column(default=0)
    event_encounter_status_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    past_mst_event_id: Mapped[int] = mapped_column(default=0)


class EventMemory(Base):
    """Event memory states for each user."""
    __tablename__ = 'event_memory'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_event_memory_id = mapped_column(
        ForeignKey('mst_event_memory.mst_event_memory_id'), primary_key=True)
    is_released: Mapped[bool] = mapped_column(default=False)


class LP(Base):
    """LP list for each user."""
    __tablename__ = 'lp'
    __table_args__ = (
        ForeignKeyConstraint(
            ['mst_song_id', 'course'],
            ['mst_course.mst_song_id', 'mst_course.course_id']
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'),
                                primary_key=True)
    course: Mapped[int]
    lp: Mapped[int]
    is_playable: Mapped[bool] = mapped_column(default=True)
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))

    user: Mapped['User'] = relationship(back_populates='lps')
    mst_course: Mapped['MstCourse'] = relationship(
        viewonly=True, lazy='joined', innerjoin=True)
    mst_song: Mapped['MstSong'] = relationship(viewonly=True, lazy='joined',
                                               innerjoin=True)


class ChallengeSong(Base):
    """Daily challenge song for each user."""
    __tablename__ = 'challenge_song'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    daily_challenge_mst_song_id = mapped_column(
        ForeignKey('mst_song.mst_song_id'), nullable=False)
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))

    user: Mapped['User'] = relationship(back_populates='challenge_song')


class MapLevel(Base):
    """Map level for each user."""
    __tablename__ = 'map_level'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    user_map_level: Mapped[int] = mapped_column(default=1)
    user_recognition: Mapped[Decimal] = mapped_column(default=Decimal(0.005))
    actual_map_level: Mapped[int] = mapped_column(default=1)
    actual_recognition: Mapped[Decimal] = mapped_column(default=Decimal(0.005))

    user: Mapped['User'] = relationship(back_populates='map_level')


class UnLockSongStatus(Base):
    """Unlocked song status for each user."""
    __tablename__ = 'un_lock_song_status'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
    max_count: Mapped[int] = mapped_column(default=3)

    user: Mapped['User'] = relationship(back_populates='un_lock_song_status')


class PendingSong(Base):
    """Pending song for each user."""
    __tablename__ = 'pending_song'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    live_token: Mapped[str]
    unit_num: Mapped[int] = mapped_column(default=0)
    mst_song_id = mapped_column(ForeignKey('mst_song.mst_song_id'), default=0,
                                insert_default=None)
    mode: Mapped[int] = mapped_column(default=0)
    course: Mapped[int] = mapped_column(default=0)
    guest_user_id = mapped_column(ForeignKey('user.user_id'), default='',
                                  insert_default=None)
    start_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc))
    is_available: Mapped[bool] = mapped_column(default=True)
    is_expired: Mapped[bool] = mapped_column(default=False)
    is_rehearsal: Mapped[bool] = mapped_column(default=False)
    is_event_tour: Mapped[bool] = mapped_column(default=False)
    guest_idol_type: Mapped[int] = mapped_column(default=0)
    use_song_unit: Mapped[bool] = mapped_column(default=False)
    is_live_support: Mapped[bool] = mapped_column(default=False)
    life: Mapped[int] = mapped_column(default=0)
    appeal: Mapped[int] = mapped_column(default=0)
    use_full_random: Mapped[bool] = mapped_column(default=False)
    use_song_random: Mapped[bool] = mapped_column(default=False)
    seed: Mapped[int] = mapped_column(default=0)
    is_valid: Mapped[bool] = mapped_column(default=False)
    retry_count: Mapped[int] = mapped_column(default=0)

    user: Mapped['User'] = relationship(back_populates='pending_song',
                                        foreign_keys=user_id)


class PendingJob(Base):
    """Pending job for each user."""
    __tablename__ = 'pending_job'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    job_token: Mapped[str]
    token: Mapped[str] = mapped_column(default='')
    is_chance: Mapped[bool] = mapped_column(default=False)
    mst_job_id = mapped_column(ForeignKey('mst_job.mst_job_id'), default=0,
                               insert_default=None)
    mst_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'), default=0,
                                insert_default=None)
    text_scenario_id: Mapped[str] = mapped_column(default='')
    adv_scenario_id: Mapped[str] = mapped_column(default='')
    text_background_id: Mapped[str] = mapped_column(default='')
    is_collab_available: Mapped[bool] = mapped_column(default=False)
    is_adv_collab_available: Mapped[bool] = mapped_column(default=False)
    adv_background_id: Mapped[str] = mapped_column(default='')
    is_challenge: Mapped[bool] = mapped_column(default=False)
    is_challenge_good: Mapped[bool] = mapped_column(default=False)
    is_valid: Mapped[bool] = mapped_column(default=False)

    user: Mapped['User'] = relationship(back_populates='pending_job')


class MstLoginBonusSchedule(Base):
    """Master table for login bonus schedules."""
    __tablename__ = 'mst_login_bonus_schedule'

    mst_login_bonus_schedule_id: Mapped[int] = mapped_column(primary_key=True)
    is_last_day: Mapped[bool] = mapped_column(default=False)
    resource_id: Mapped[str] = mapped_column(default='')
    cue_name1: Mapped[str] = mapped_column(default='')
    cue_name2: Mapped[str] = mapped_column(default='')
    script_name: Mapped[str]


class MstLoginBonusItem(Base):
    """Master table for login bonus items."""
    __tablename__ = 'mst_login_bonus_item'

    mst_login_bonus_schedule_id = mapped_column(
        ForeignKey('mst_login_bonus_schedule.mst_login_bonus_schedule_id'),
        primary_key=True)
    mst_item_id = mapped_column(ForeignKey('mst_item.mst_item_id'),
                                nullable=False)
    item_type: Mapped[int]
    amount: Mapped[int]
    day: Mapped[int] = mapped_column(primary_key=True)


class LoginBonusItem(Base):
    """Login bonus item states for each user."""
    __tablename__ = 'login_bonus_item'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_login_bonus_schedule_id',
                'day'
            ],
            [
                'mst_login_bonus_item.mst_login_bonus_schedule_id',
                'mst_login_bonus_item.day'
            ]
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_login_bonus_schedule_id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[int] = mapped_column(primary_key=True)
    reward_item_state: Mapped[int] = mapped_column(default=1)
    next_login_date: Mapped[datetime] = mapped_column(
        default=(datetime.now(server_timezone) + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).astimezone(timezone.utc))


class MstOffer(Base):
    """Master table for offers.

    recommended_idol_id_list: exactly one idol
    """
    __tablename__ = 'mst_offer'

    mst_offer_id: Mapped[int] = mapped_column(primary_key=True)
    mst_event_id: Mapped[int] = mapped_column(default=0)
    resource_id: Mapped[str]
    resource_logo_id: Mapped[str] = mapped_column(default='')
    require_time: Mapped[int] = mapped_column(default=180)
    mst_offer_type: Mapped[int] = mapped_column(default=1)
    main_idol_id = mapped_column(ForeignKey('mst_idol.mst_idol_id'),
                                 nullable=False)
    recommended_idol_id_list = mapped_column(
        ForeignKey('mst_idol.mst_idol_id'), nullable=False)
    parameter_type: Mapped[int]
    border_value: Mapped[int]


class Offer(Base):
    """Offer states for each user.
    
    TODO: normalize lists if required
    """
    __tablename__ = 'offer'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_offer_id = mapped_column(ForeignKey('mst_offer.mst_offer_id'),
                                 primary_key=True)
    slot: Mapped[int] = mapped_column(default=0)
    status: Mapped[int] = mapped_column(default=0)
    start_date: Mapped[datetime] = mapped_column(default=datetime(1, 1, 1))
    card_list: Mapped[Optional[str]] = mapped_column(default=None)
    is_recommended: Mapped[bool] = mapped_column(default=False)
    is_text_completed: Mapped[bool] = mapped_column(default=False)


class MstBanner(Base):
    """Master table for banner list."""
    __tablename__ = 'mst_banner'

    banner_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    jump: Mapped[str]
    banner_type: Mapped[int] = mapped_column(default=0)
    open_date: Mapped[datetime]
    close_date: Mapped[datetime]
    banner_image_link: Mapped[str]
    announce_web_view_link: Mapped[str] = mapped_column(default='')
    is_gasha_view: Mapped[bool]
    url: Mapped[str] = mapped_column(default='')
    simple_view_text: Mapped[str] = mapped_column(default='')


class Profile(Base):
    """Profile for each user

    mst_achievement_id_list: comma-separated mst_achievement_ids
    TODO: normalize lists if required
    """
    __tablename__ = 'profile'

    id_ = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    name: Mapped[str]
    birthday: Mapped[str] = mapped_column(default='')
    is_birthday_public: Mapped[bool] = mapped_column(default=False)
    comment: Mapped[str]
    favorite_card_id = mapped_column(ForeignKey('card.card_id'))
    favorite_card_befor_awake: Mapped[bool] = mapped_column(default=False)
    mst_achievement_id: Mapped[int] = mapped_column(default=1)
    mst_achievement_id_list: Mapped[Optional[str]] = mapped_column(
        default=None)
    lp: Mapped[int] = mapped_column(default=0)
    album_count: Mapped[int] = mapped_column(default=55)
    story_count: Mapped[int] = mapped_column(default=0)


class HelperCard(Base):
    """Helper cards for each user."""
    __tablename__ = 'helper_card'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    idol_type: Mapped[int] = mapped_column(primary_key=True)
    card_id = mapped_column(ForeignKey('card.card_id'), nullable=False)


class ClearSongCount(Base):
    """Cleared song counts for each user."""
    __tablename__ = 'clear_song_count'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    live_course: Mapped[int] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(default=0)


class FullComboSongCount(Base):
    """Full combo song counts for each user."""
    __tablename__ = 'full_combo_song_count'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    live_course: Mapped[int] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(default=0)


class TheaterRoom(Base):
    """Theater room list for each user."""
    __tablename__ = 'theater_room'
    __table_args__ = (
        ForeignKeyConstraint(
            [
                'mst_theater_contact_id',
                'mst_theater_main_story_id',
                'mst_theater_guest_main_story_id',
                'mst_theater_blog_id',
                'mst_theater_costume_blog_id',
                'mst_theater_event_story_id'
            ],
            [
                'mst_theater_room_status.mst_theater_contact_id',
                'mst_theater_room_status.mst_theater_main_story_id',
                'mst_theater_room_status.mst_theater_guest_main_story_id',
                'mst_theater_room_status.mst_theater_blog_id',
                'mst_theater_room_status.mst_theater_costume_blog_id',
                'mst_theater_room_status.mst_theater_event_story_id'
            ]
        ),
    )

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    mst_room_id: Mapped[int] = mapped_column(primary_key=True)
    mst_theater_contact_id: Mapped[int] = mapped_column(default=0)
    mst_theater_main_story_id: Mapped[int] = mapped_column(default=0)
    mst_theater_guest_main_story_id: Mapped[int] = mapped_column(default=0)
    mst_theater_blog_id: Mapped[int] = mapped_column(default=0)
    mst_theater_costume_blog_id: Mapped[int] = mapped_column(default=0)
    mst_theater_event_story_id: Mapped[int] = mapped_column(default=0)


class LastUpdateDate(Base):
    """Last update dates for each user."""
    __tablename__ = 'last_update_date'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    last_update_date_type: Mapped[int] = mapped_column(primary_key=True)
    last_update_date: Mapped[datetime] = mapped_column(
        default=datetime(1, 1, 1))


class MstBirthdayCalendar(Base):
    """Birthday calendar for all characters."""
    __tablename__ = 'mst_birthday_calendar'

    mst_character_id: Mapped[int] = mapped_column(primary_key=True)
    idol_type: Mapped[int]
    birthday_month: Mapped[int]
    birthday_day: Mapped[int]


class Birthday(Base):
    """Character birthday states for each user."""
    __tablename__ = 'birthday'

    user_id = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    year: Mapped[int] = mapped_column(primary_key=True)
    mst_character_id = mapped_column(
        ForeignKey('mst_birthday_calendar.mst_character_id'), primary_key=True)
    is_executed: Mapped[bool] = mapped_column(default=False)
    is_birthday_live_played: Mapped[bool] = mapped_column(default=False)
    mst_idol_id_list: Mapped[Optional[str]] = mapped_column(default=None)


if __name__ == '__main__':
    Base.metadata.create_all(engine)

