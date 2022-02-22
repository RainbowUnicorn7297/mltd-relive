from connection import conn

def create_mst_costume(cursor):
    '''Master table for costumes

mst_costume_group_id: ??? 0-993
costume_name: ??? -,ex,ss,sr,gs, mostly ex
costume_number: ??? 0-601
exclude_album: Unused. exclude_album=false for all costumes
exclude_random: true for mst_costume_id=0, false for everything else
collabo_number: Unused. collabo_number=0 for all costumes
replace_group_id: ??? 0,4-6, mostly 0
gorgeous_appeal_type: 0=normal, 1=master rank 5 costume
'''

    cursor.execute('''
create table mst_costume(
    mst_costume_id int primary key,
    mst_idol_id int,
    resource_id text,
    mst_costume_group_id int,
    costume_name text,
    costume_number int,
    exclude_album int,
    exclude_random int,
    collabo_number int,
    replace_group_id int,
    sort_id int,
    release_date int,
    gorgeous_appeal_type int
)
''')


def create_costume(cursor):
    '''Costumes unlocked by user
'''

    cursor.execute('''
create table costume(
    costume_id text primary key,
    user_id text,
    mst_costume_id int
)
''')


def create_mst_center_effect(cursor):
    '''Master table for card center skills

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
'''

    cursor.execute('''
create table mst_center_effect(
    mst_center_effect_id int primary key,
    effect_id int,
    idol_type int,
    specific_idol_type int,
    attribute int,
    value int,
    song_idol_type int,
    attribute2 int,
    value2 int
)
''')


def create_mst_card_skill(cursor):
    '''Master table for card skills

effect_id:
    1=Score bonus, 2=Combo bonus, 3=Healer, 4=Life guard, 5=Combo guard,
    6=Perfect lock, 7=Double boost, 8=Multi up, 10=Overclock
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
'''

    cursor.execute('''
create table mst_card_skill(
    mst_card_skill_id int primary key,
    effect_id int,
    duration int,
    evaluation int,
    evaluation2 int,
    interval int,
    probability_base int,
    value int,
    value2 int
)
''')


def create_mst_card(cursor):
    '''Master table for card info

rarity: 1=N, 2=R, 3=SR, 4=SSR
attribute:
    1=Vocal+X%, 2=Dance+X%, 3=Visual+X%, 4=All appeals+X%,
    5=Life+X%, 6=Skill prob.+X%
begin_date: Card released
ex_type: 0=Normal, 2=PST (Ranking), 3=PST (Event Pt), 4=FES, 5=1st, 6=Ex, 7=2nd
idol_type: 1=Princess, 2=Fairy, 3=Angel, 5=Ex
level_max: max level after awakened
    If N, level_max = 30
    If R, level_max = 50
    If SR, level_max = 70
    If SSR, level_max = 90
vocal_base: Vocal base value if card level=0, before awakened, master rank=0
    If N, vocal_base = round(vocal_max * 20 / 60)
    If R, vocal_base = round(vocal_max * 40 / 100)
    If SR, vocal_base = round(vocal_max * 60 / 140)
    If SSR, vocal_base = round(vocal_max * 80 / 180)
vocal_max: Vocal max value if card level=90, after awakened, master rank=0
vocal_master_bonus: Vocal bonus per master rank
    vocal_master_bonus = round(vocal_max * 0.03)
cheer_point: Unused. cheer_point=0 for all cards
variation: ??? 1-16, older=smaller, newer=larger
master_lesson_begin_date: master lessons became available for PST card
card_category: ??? 10-35
    33=Anniversary card
extend_card_params: Anniversary card stats after trained to SSR
training_point: Unused. training_point=0 for all cards
sign_type: Unused. sign_type=0 for all cards
sign_type2: Unused. sign_type2=0 for all cards
'''

    cursor.execute('''
create table mst_card(
    mst_card_id int primary key,
    mst_idol_id int,
    sort_id int,
    rarity int,
    attribute int,
    mst_card_skill_id int,
    mst_center_effect_id int,
    begin_date int,
    ex_type int,
    resource_id text,
    mst_costume_id int,
    bonus_costume_id int,
    rank5_costume_id int,
    idol_type int,
    level_max int,
    life int,
    vocal_base int,
    vocal_max int,
    vocal_master_bonus int,
    dance_base int,
    dance_max int,
    dance_master_bonus int,
    visual_base int,
    visual_max int,
    visual_master_bonus int,
    skill_level_max int,
    awakening_gauge_max int,
    master_rank_max int,
    cheer_point int,
    variation int,
    master_lesson_begin_date int,
    card_category int,
    extend_card_level_max int,
    extend_card_life int,
    extend_card_vocal_max int,
    extend_card_vocal_master_bonus int,
    extend_card_dance_max int,
    extend_card_dance_master_bonus int,
    extend_card_visual_max int,
    extend_card_visual_master_bonus int,
    is_master_lesson_five_available int,
    training_point int,
    sign_type int,
    sign_type2 int
)
''')


def create_card(cursor):
    '''Card info specific to each user

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
skill_probability: Current skill probability in %
    For skill levels 1-10:
        skill_probability = probability_base + skill_level
    For skill levels 11-12:
        skill_probability = probability_base + 10 + 5 * (skill_level - 10)
        TODO: verify skill level 11
create_date: Card obtained by user
'''

    cursor.execute('''
create table card(
    card_id text primary key,
    user_id text,
    mst_card_id int,
    exp int,
    level int,
    vocal int,
    vocal_diff real,
    dance int,
    dance_diff real,
    visual int,
    visual_diff real,
    before_awakened_life int,
    before_awakened_vocal int,
    before_awakened_dance int,
    before_awakened_visual int,
    after_awakened_life int,
    after_awakened_vocal int,
    after_awakened_dance int,
    after_awakened_visual int,
    skill_level int,
    skill_probability int,
    is_awakened int,
    awakening_gauge int,
    master_rank int,
    create_date int,
    is_new int
)
''')


def create_mst_direction_category(cursor):
    '''Master table for direction category (演出)


'''

    cursor.execute('''
create table mst_direction_category(
    mst_direction_category_id int primary key,
    sort_id int,
    idol_detail_type int,
    direction_type int,
    resource_id text,
    release_date int
)
''')


def create_mst_voice_category(cursor):
    '''Master table for voice category (語音)

value: Unlock condition for voice category
    For mst_voice_category_ids 3101-3106, value=required affection
    For 3101, value=50
    For 3102, value=200
    For 3103, value=500
    For 3104, value=900
    For 3105, value=1400
    For 3106, value=2000
'''

    cursor.execute('''
create table mst_voice_category(
    mst_voice_category_id int primary key,
    sort_id int,
    idol_detail_type int,
    value int,
    rarity int,
    label_header text,
    voice_label text,
    release_date int,
    mst_direction_category_id int
)
''')


##def create_idol_voice_category(cursor):
##    '''Unlocked idol voice categories (偶像特有台詞) by user
##
###1: affection=50
###2: affection=200
###3: affection=500
###4: affection=900
###5: affection=1400
###6: affection=2000
##TODO: table is redundant by comparing mst_voice_category's value with
##      current affection per idol for each user
##'''
##
##    cursor.execute('''
##create table idol_voice_category(
##    idol_voice_category_id text primary key,
##    user_id text,
##    mst_idol_id int,
##    mst_voice_category_id int
##)
##''')


def create_mst_lesson_wear(cursor):
    '''Master table for lesson wear

mst_lesson_wear_id: 1-52=訓練課程服, 9001-90052=1週年記念
mst_lesson_wear_group_id: 1=訓練課程服, 9001=1週年記念
costume_number: costume_number=1 for all lesson wear
costume_name: tr=訓練課程服, cr=1週年記念
collabo_no: 0=, 55=1週年記念
resource_id: resource_id=training_01 for all lesson wear
'''

    cursor.execute('''
create table mst_lesson_wear(
    mst_lesson_wear_id int primary key,
    mst_idol_id int,
    mst_lesson_wear_group_id int,
    costume_number int,
    costume_name text,
    collabo_no int,
    resource_id text
)
''')


##def create_idol_lesson_wear(cursor):
##    '''Default lesson wear chosen by each user
##
##TODO: table is redundant by combining tables "mst_lesson_wear",
##      "lesson_wear_config" and "mst_lesson_wear_config"
##'''
##
##    cursor.execute('''
##create table idol_lesson_wear(
##    idol_lesson_wear_id text primary key,
##    user_id text,
##    mst_lesson_wear_id int,
##    default_flag int
##)
##''')


def create_mst_idol(cursor):
    '''Master table for idol info

tension: Unused. tension=100 for all idols
is_best_condition: Unused. is_best_condition=false for all idols
area: ??? 0-7
offer_type: ??? 0-4
mst_agency_id: 1=765, 2=961
default_costume: mst_costume_id of casual wear
birthday_live: birthday_live=0 for Shika, 1 for everyone else
'''

    cursor.execute('''
create table mst_idol(
    mst_idol_id int primary key,
    idol_type int,
    tension int,
    is_best_condition int,
    area int,
    offer_type int,
    mst_agency_id int,
    default_costume int,
    birthday_live int
)
''')


def create_idol(cursor):
    '''Idol info specific to each user

has_another_appeal: true=unlocked 異色綻放, false=not yet unlocked
can_perform: false only when Ex card not yet obtained
'''

    cursor.execute('''
create table idol(
    idol_id text primary key,
    user_id text,
    mst_idol_id int,
    fan int,
    affection int,
    has_another_appeal int,
    can_perform int
)
''')


def create_mst_memorial(cursor):
    '''Master table for memorials

reward_type=4, reward_mst_item_id=3, reward_item_type=1, reward_amount=50
'''

    cursor.execute('''
create table mst_memorial(
    mst_memorial_id int primary key,
    scenario_id text,
    mst_idol_id int,
    release_affection int,
    number int,
    reward_type int,
    reward_mst_item_id int,
    reward_item_type int,
    reward_amount int,
    is_available int,
    begin_date int
)
''')


def create_memorial(cursor):
    '''Memorial states for each user

released_date: Unused. released_date=null for all memorials
'''

    cursor.execute('''
create table memorial(
    memorial_id text primary key,
    user_id text,
    mst_memorial_id int,
    is_released int,
    is_read int,
    released_date int
)
''')


def create_episode(cursor):
    '''Awakening story states for each card for each user

released_date: Unused. released_date=null for all episodes
reward_type=4, reward_mst_item_id=3, reward_item_type=1, reward_amount=25
'''

    cursor.execute('''
create table episode(
    episode_id text primary key,
    user_id text,
    mst_card_id int,
    is_released int,
    is_read int,
    released_date int,
    reward_type int,
    reward_mst_item_id int,
    reward_item_type int,
    reward_amount int
)
''')


def create_mst_theater_costume_blog(cursor):
    '''Master table for costume blogs

reward_type=4, reward_mst_item_id=3, reward_item_type=1, reward_amount=50
'''

    cursor.execute('''
create table mst_theater_costume_blog(
    mst_theater_costume_blog_id int primary key,
    mst_card_id int,
    reward_type int,
    reward_mst_item_id int,
    reward_item_type int,
    reward_amount int
)
''')


def create_costume_adv(cursor):
    '''Costume blog states for each user

released_date: Unused. released_date=null for all costume blogs
'''

    cursor.execute('''
create table costume_adv(
    costume_adv_id text primary key,
    user_id text,
    mst_theater_costume_blog_id int,
    is_released int,
    is_read int,
    released_date int
)
''')


def create_mst_item(cursor):
    '''Master table for items

item_navi_type:
    0=Others (money, memory piece, anniversary idol-specific piece)
    1=Vitality recovery item (spark drink, macaron, present from idol)
    2=Awakening item
    3=Lesson ticket
    4=Master rank item (including PST piece)
    5=Gacha ticket/medal
    6=Live item (live ticket, auto live pass, singing voice master key)
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
    13=Selection ticket/Platinum selection ticket/Platinum SR selection ticket
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
'''

    cursor.execute('''
create table mst_item(
    mst_item_id int primary key,
    name text,
    item_navi_type int,
    max_amount int,
    item_type int,
    sort_id int,
    value1 int,
    value2 int,
    is_extend int
)
''')


def create_item(cursor):
    '''Items obtained by user
'''

    cursor.execute('''
create table item(
    item_id text primary key,
    user_id text,
    mst_item_id int,
    amonut int,
    expire_date int
)
''')


def create_mst_gasha(cursor):
    '''Master table for gachas

currency_type_list: comma-separated currency types
'''

    cursor.execute('''
create table mst_gasha(
    mst_gasha_id int primary key,
    mst_gasha_ticket_item_id int,
    name text,
    display_category int,
    begin_date int,
    end_date int,
    currency_type_list text,
    is_paid_jewel_only int,
    draw1_jewel_value int,
    draw10_jewel_value int,
    draw1_mst_item_id int,
    draw10_mst_item_id int,
    daily_limit int,
    total_limit int,
    sr_passport int,
    ssr_passport int,
    has_new_idol int,
    has_limited int,
    notify_num int,
    today_count int,
    total_count int,
    mst_gasha_kind_id int,
    mst_gasha_bonus_id int,
    gasha_bonus_item int,
    gasha_bonus_mst_achievement_id int,
    gasha_bonus_costume int,
    ticket_item text,
    is_limit int,
    draw_point_mst_item_id int,
    draw_point int,
    draw_point_max int,
    draw1_free_count int,
    draw10_free_count int,
    pickup_signature text,
    pickup_gasha_card int,
    balloon int
)
''')


def create_mst_job(cursor):
    '''Master table for jobs
'''

    cursor.execute('''
create table mst_job(
    mst_job_id int primary key,
    resource_id text,
    vitality_cost int,
    job_type int,
    idol_type int,
    reward_exp int,
    reward_fan int,
    reward_affection int,
    reward_money int,
    reward_live_ticket int,
    begin_date int,
    end_date int
)
''')


def create_mst_course(cursor):
    '''Master table for course info for each song

course_id: 
    1=Solo 2M?
    2=2M?
    3=Solo 2M+?
    4=4M
    5=6M?
    6=MM
TODO: add score/combo/clear rank requirements?
'''

    cursor.execute('''
create table mst_course(
    mst_song_id int,
    course_id int,
    cost int,
    level int,
    appeal int,
    notes int,
    primary key (mst_song_id, course_id)
)
''')


def create_course(cursor):
    '''Course info specific to each user
'''

    cursor.execute('''
create table course(
    user_id text,
    mst_song_id int,
    course_id int,
    score int,
    combo int,
    clear int,
    score_rank int,
    combo_rank int,
    clear_rank int,
    is_released int,
    primary key (user_id, mst_song_id, course_id)
)
''')


def create_mst_extend_song(cursor):
    '''Master table for extend songs

song_unit_idol_id_list: comma-separated mst_idol_ids
'''

    cursor.execute('''
create table mst_extend_song(
    mst_song_id int primary_key,
    resource_id text,
    kind int,
    stage_id int,
    stage_ts_id int,
    mst_song_unit_id int,
    song_unit_idol_id_list text,
    unit_selection_type int,
    unit_song_type int,
    icon_type int,
    idol_count int,
    extend_type int,
    filter_type int,
    song_open_type int,
    song_open_type_value int,
    song_open_level int
)
''')


def create_mst_song(cursor):
    '''Master table for songs
'''

    cursor.execute('''
create table mst_song(
    mst_song_id int primary key,
    sort_id int,
    resource_id text,
    idol_type int,
    song_type int,
    kind int,
    stage_id int,
    stage_ts_id int,
    bpm int,
    apple_song_url text,
    google_song_url text,
    song_open_type int,
    song_open_type_value int,
    song_open_level int,
    song_unit_idol_id_list text,
    mst_song_unit_id int,
    idol_count int,
    icon_type int,
    unit_selection_type int,
    only_default_unit int,
    only_extend int,
    is_off_vocal_available int,
    off_vocal_cue_sheet text,
    off_vocal_cue_name text,
    song_permit_control int,
    permitted_mst_idol_id_list text,
    permitted_mst_agency_id_list text,
    extend_song_playable_status int,
    live_start_voice_mst_idol_id_list text,
    is_enable_random int,
    part_permitted_mst_idol_id_list text,
    is_recommend int,
    song_parts_type int
)
''')


def create_song(cursor):
    '''Song info specific to each user
'''

    cursor.execute('''
create table song(
    song_id text primary key,
    user_id text,
    mst_song_id int,
    is_released_mv int,
    is_released_horizontal_mv int,
    is_released_vertical_mv int,
    is_cleared int,
    first_cleared_date int,
    is_played int,
    lp int,
    is_visible int,
    is_disable int,
    is_off_vocal_released int,
    is_new int
)
''')


def create_unit_idol(cursor):
    '''Idol list (selected card & costume) for each unit for each user
'''

    cursor.execute('''
create table unit_idol(
    user_id text,
    unit_num int,
    card_id text,
    mst_costume_id int,
    mst_lesson_wear_id int,
    costume_is_random int,
    costume_random_type int,
    primary key (user_id, unit_num, card_id)
)
''')


def create_unit(cursor):
    '''Unit info specific to each user
'''

    cursor.execute('''
create table unit(
    user_id text,
    unit_num int,
    name text,
    primary key (user_id, unit_num)
)
''')


def create_song_unit_idol(cursor):
    '''Idol list (selected card & costume) for each song unit for each user
'''

    cursor.execute('''
create table song_unit_idol(
    user_id text,
    mst_song_id int,
    card_id text,
    mst_costume_id int,
    mst_lesson_wear_id int,
    costume_is_random int,
    costume_random_type int,
    primary key (user_id, mst_song_id, card_id)
)
''')


def create_song_unit(cursor):
    '''Unit info specific to each song for each user
'''

    cursor.execute('''
create table song_unit(
    user_id text,
    mst_song_id int,
    unit_song_type int,
    is_new int,
    primary key (user_id, mst_song_id)
)
''')


def create_mst_theater_main_story_idol(cursor):
    '''Master table for theater room idol list for each main story
'''

    cursor.execute('''
create table mst_theater_main_story_idol(
    mst_theater_main_story_id int,
    mst_idol_id int,
    position_id text,
    motion_id text,
    reaction_id text,
    reaction_id_2 text,
    primary key (mst_theater_main_story_id, mst_idol_id)
)
''')


def create_mst_theater_main_story(cursor):
    '''Master table for theater room status for each main story

TODO: Some columns for theater_room_status seem to be designed for other
      purposes. API is returning everything using a common data structure.
      May need to refactor later.
'''

    cursor.execute('''
create table mst_theater_main_story(
    mst_theater_main_story_id int primary key,
    mst_main_story_id int,
    mst_room_id int,
    theater_contact_category_type int,
    resource_id text,
    mst_theater_contact_schedule_id int,
    mst_theater_contact_id int,
    mst_theater_guest_main_story_id int,
    guest_main_story_has_intro int,
    mst_guest_main_story_id int,
    mst_theater_blog_id int,
    mst_theater_costume_blog_id int,
    mst_costume_id int,
    mst_theater_event_story_id int,
    mst_event_story_id int,
    mst_event_id int,
    duration int
)
''')


def create_mst_main_story(cursor):
    '''Master table for main stories

mst_idol_id_list: comma-separated mst_idol_ids
reward_type=4, reward_mst_item_id=3, reward_item_type=1, reward_amount=50
'''

    cursor.execute('''
create table mst_main_story(
    mst_main_story_id int,
    number int,
    chapter int,
    mst_idol_id_list text,
    release_level int,
    release_song_id int,
    reward_song_id int,
    reward_type int,
    reward_mst_item_id int,
    reward_item_type int,
    reward_amount int,
    intro_contact_mst_idol_id int,
    blog_contact_mst_idol_id int,
    primary key (mst_main_story_id, number, chapter)
)
''')


def create_main_story(cursor):
    '''Main story states specific to each user
'''

    cursor.execute('''
create table main_story(
    user_id text,
    mst_main_story_id int,
    number int,
    chapter int,
    released_date int,
    is_released int,
    is_read int,
    primary key (user_id, mst_main_story_id, number, chapter)
)
''')


def create_mst_awakening_config(cursor):
    '''Required items for awakening
'''

    cursor.execute('''
create table mst_awakening_config(
    rarity int,
    idol_type int,
    mst_card_id int,
    mst_item_id int,
    amount int,
    primary key (rarity, idol_type, mst_item_id)
)
''')


def create_mst_master_lesson2_config(cursor):
    '''Required master pieces for master lessons
'''

    cursor.execute('''
create table mst_master_lesson2_config(
    rarity int,
    idol_type int,
    mst_item_id int,
    amount int,
    primary key (rarity, idol_type, mst_item_id)
)
''')


def create_mst_ex_master_lesson_config(cursor):
    '''Required items for ex master lessons

ex_type: ??? 2-6
    2=PST
amount: comma-separated values, one for each master rank
'''

    cursor.execute('''
create table mst_ex_master_lesson_config(
    ex_type int primary key,
    mst_item_id int,
    amount text,
    mst_card_id int
)
''')


def create_mst_lesson_money_config(cursor):
    '''Required money per ticket for lessons
'''

    cursor.execute('''
create table mst_lesson_money_config(
    rarity int primary key,
    money int,
    mst_item_id int
)
''')


def create_mst_lesson_skill_level_up_config(cursor):
    '''Required "skill EXP" for each skill level for guanranteed level up

skill_level: target skill level
rarity: card rarity
value: required "skill EXP"
"Skill EXP" per ticket is defined by mst_item's value2:
    Lesson ticket N=0
    Lesson ticket R=300
    Lesson ticket SR=1000
    Lesson ticket SSR=2000
'''

    cursor.execute('''
create table mst_lesson_skill_level_up_config(
    skill_level int,
    rarity int,
    value int,
    primary key (skill_level, rarity)
)
''')


def create_mst_lesson_wear_config(cursor):
    '''Available lesson wear in system settings
'''

    cursor.execute('''
create table mst_lesson_wear_config(
    mst_lesson_wear_setting_id int primary key,
    mst_lesson_wear_group_id int
)
''')


def create_lesson_wear_config(cursor):
    '''Lesson wear chosen by user
'''

    cursor.execute('''
create table lesson_wear_config(
    user_id text primary key,
    mst_lesson_wear_setting_id int
)
''')


def create_mst_comic_menu(cursor):
    '''Comic menu list (unused in zh/ko versions)
'''

    cursor.execute('''
create table mst_comic_menu(
    mst_comic_menu_id int primary key,
    url text,
    resource_id text,
    enable_button int
)
''')


def create_mst_training_unit(cursor):
    '''Required songs and idols for anniversary training mission

idol_id_list: comma-separated mst_idol_ids
'''

    cursor.execute('''
create table mst_training_unit(
    mst_song_unit_id int primary key,
    idol_id_list text
)
''')


def create_mst_master_lesson_five_config(cursor):
    '''Required items for master rank 5 lessons

ex_type: ??? 0 or 4
'''

    cursor.execute('''
create table mst_master_lesson_five_config(
    ex_type int,
    idol_type int,
    mst_item_id int,
    amount int,
    primary key (ex_type, idol_type, mst_item_id)
)
''')


def create_mst_title_image(cursor):
    '''Available title images in system settings

title_image_type: 2=event, 3=others
'''

    cursor.execute('''
create table mst_title_image(
    mst_title_image_id int primary key,
    title_image_type int,
    sord_id int,
    begin_date int,
    end_date int
)
''')


def create_mst_loading_character(cursor):
    '''Loading character list
'''

    cursor.execute('''
create table mst_loading_character(
    resource_id text primary key,
    weight int,
    begin_date int,
    end_date int
)
''')


if __name__ == "__main__":
    cursor = conn.cursor()
    create_mst_costume(cursor)
    create_costume(cursor)
    create_mst_center_effect(cursor)
    create_mst_card_skill(cursor)
    create_mst_card(cursor)
    create_card(cursor)
    create_mst_direction_category(cursor)
    create_mst_voice_category(cursor)
##    create_idol_voice_category(cursor)
    create_mst_lesson_wear(cursor)
##    create_idol_lesson_wear(cursor)
    create_mst_idol(cursor)
    create_idol(cursor)
    create_mst_memorial(cursor)
    create_memorial(cursor)
    create_episode(cursor)
    create_mst_theater_costume_blog(cursor)
    create_costume_adv(cursor)
    create_mst_item(cursor)
    create_item(cursor)
    create_mst_gasha(cursor)
    create_mst_job(cursor)
    create_mst_course(cursor)
    create_course(cursor)
    create_mst_extend_song(cursor)
    create_mst_song(cursor)
    create_song(cursor)
    create_unit_idol(cursor)
    create_unit(cursor)
    create_song_unit_idol(cursor)
    create_song_unit(cursor)
    create_mst_theater_main_story_idol(cursor)
    create_mst_theater_main_story(cursor)
    create_mst_main_story(cursor)
    create_main_story(cursor)
    create_mst_awakening_config(cursor)
    create_mst_master_lesson2_config(cursor)
    create_mst_ex_master_lesson_config(cursor)
    create_mst_lesson_money_config(cursor)
    create_mst_lesson_skill_level_up_config(cursor)
    create_mst_lesson_wear_config(cursor)
    create_lesson_wear_config(cursor)
    create_mst_comic_menu(cursor)
    create_mst_training_unit(cursor)
    create_mst_master_lesson_five_config(cursor)
    create_mst_title_image(cursor)
    create_mst_loading_character(cursor)
    conn.commit()
