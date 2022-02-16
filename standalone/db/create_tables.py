from connection import conn

def create_mst_idol(cursor):
    '''Master table for idol info
'''

    cursor.execute('''
''')


def create_mst_costume(cursor):
    '''Master table for costumes


'''

    cursor.execute('''
create table costume(
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
    5=Perfect/Great/Good
    6=Perfect/Great/Good/Fast/Slow
    7=Great/Good
evaluation2: Required note types for activating 2nd skill
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
    probability int,
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
begin_date: Card first became available
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
master_lesson_begin_date: PST card became exchangeable in event shop
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
    is_awakened int,
    awakening_gauge int,
    master_rank int,
    create_date int,
    is_new int
)
''')


if __name__ == "__main__":
    cursor = conn.cursor()
    create_mst_costume(cursor)
    create_mst_center_effect(cursor)
    create_mst_card_skill(cursor)
    create_mst_card(cursor)
    create_card(cursor)
    conn.commit()
