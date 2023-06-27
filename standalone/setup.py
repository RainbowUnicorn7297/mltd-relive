import csv
from base64 import b64encode
from os import listdir
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import *


def _insert_cards(session: Session, user: User):
    def _diff_before_awakened(value_max, level_max):
        return value_max / (2*level_max)

    def _diff_after_awakened(value_max, level_max):
        return value_max * (level_max+10) / (2*level_max*level_max)

    def _value(base, diff, level, master_bonus, master_rank):
        return base + round(diff*level) + master_bonus*master_rank

    def _skill_probability(base, level):
        if level <= 10:
            return base + level
        else:
            return base + 10 + 5*(level-10)

    def _min_exp(level):
        # This is the code originally used to calculate the minimum
        # possible exp for each maxed-out card.
        # ---
        # required_exp = (level-1) * (level-1) * 10
        # valid_exps = set([800, 2500, 4000, 5000])
        # for i in range(100):
        #     new_valid_exps = set(valid_exps)
        #     for a in valid_exps:
        #         for b in valid_exps:
        #             new_valid_exps.add(a + b)
        #     valid_exps = set(x for x in new_valid_exps if x <= 100_000)
        # min_exp = 100_000
        # for valid_exp in valid_exps:
        #     if valid_exp > required_exp and valid_exp < min_exp:
        #         min_exp = valid_exp
        # return min_exp
        if level == 30:
            return 8800
        if level == 50:
            return 24100
        if level == 70:
            return 47700
        if level == 90:
            return 79300
        return (level-1) * (level-1) * 10

    mst_cards = session.scalars(
        select(MstCard)
    ).all()
    for mst_card in mst_cards:
        card = Card(
            card_id=f'{user.user_id}_{mst_card.mst_card_id}',
            user_id=user.user_id,
            mst_card_id=mst_card.mst_card_id,
            exp=_min_exp(mst_card.level_max),
            level=mst_card.level_max,
            vocal_diff=_diff_after_awakened(mst_card.vocal_max,
                                            mst_card.level_max),
            dance_diff=_diff_after_awakened(mst_card.dance_max,
                                            mst_card.level_max),
            visual_diff=_diff_after_awakened(mst_card.visual_max,
                                             mst_card.level_max),
            before_awakened_vocal=_value(
                mst_card.vocal_base,
                _diff_before_awakened(mst_card.vocal_max, mst_card.level_max),
                mst_card.level_max - 10,
                mst_card.vocal_master_bonus,
                mst_card.master_rank_max
            ),
            before_awakened_dance=_value(
                mst_card.dance_base,
                _diff_before_awakened(mst_card.dance_max, mst_card.level_max),
                mst_card.level_max - 10,
                mst_card.dance_master_bonus,
                mst_card.master_rank_max
            ),
            before_awakened_visual=_value(
                mst_card.visual_base,
                _diff_before_awakened(mst_card.visual_max, mst_card.level_max),
                mst_card.level_max - 10,
                mst_card.visual_master_bonus,
                mst_card.master_rank_max
            ),
            after_awakened_vocal=_value(
                mst_card.vocal_base,
                _diff_after_awakened(mst_card.vocal_max, mst_card.level_max),
                mst_card.level_max,
                mst_card.vocal_master_bonus,
                mst_card.master_rank_max
            ),
            after_awakened_dance=_value(
                mst_card.dance_base,
                _diff_after_awakened(mst_card.dance_max, mst_card.level_max),
                mst_card.level_max,
                mst_card.dance_master_bonus,
                mst_card.master_rank_max
            ),
            after_awakened_visual=_value(
                mst_card.visual_base,
                _diff_after_awakened(mst_card.visual_max, mst_card.level_max),
                mst_card.level_max,
                mst_card.visual_master_bonus,
                mst_card.master_rank_max
            ),
            skill_level_max=(12 if mst_card.is_master_lesson_five_available
                             else 10),
            is_awakened=True,
            awakening_gauge=mst_card.awakening_gauge_max,
            master_rank=mst_card.master_rank_max,
            create_date=max(mst_card.begin_date, user.first_time_date)
        )
        card.vocal = card.after_awakened_vocal
        card.dance = card.after_awakened_dance
        card.visual = card.after_awakened_visual
        card.skill_level = card.skill_level_max
        card.skill_probability=None if not mst_card.mst_card_skill_id else (
            _skill_probability(mst_card.mst_card_skill.probability_base,
                               card.skill_level_max)
        )
        session.add(card)


if __name__ == '__main__':
    # Create tables.
    Base.metadata.create_all(engine)

    # Insert master data.
    mst_data_dir = 'mltd/models/mst_data/'
    with Session(engine) as session:
        session.execute(text('PRAGMA foreign_keys=OFF'))

        for filename in listdir(mst_data_dir):
            if 'mst' not in filename:
                continue
            table_name = filename.split('.')[0]
            table = Base.metadata.tables[table_name]
            with open(f'{mst_data_dir}{table_name}.csv',
                      encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                data = list(reader)
            # Convert CSV data into proper data types because they are
            # all read as strs.
            for row in data:
                for fieldname in fieldnames:
                    column = table.c[fieldname]
                    if column.nullable and not row[fieldname]:
                        # If column is nullable, replace null-equivalent
                        # values with None.
                        row[fieldname] = None
                    elif str(column.type) == 'BOOLEAN' and row[fieldname]:
                        row[fieldname] = (False if row[fieldname] == '0'
                                          else True)
                    elif str(column.type) == 'INTEGER' and row[fieldname]:
                        row[fieldname] = int(row[fieldname])
                    elif str(column.type) == 'DATETIME' and row[fieldname]:
                        # Convert str to UTC datetime.
                        row[fieldname] = datetime.strptime(
                            row[fieldname], '%Y-%m-%dT%H:%M:%S%z'
                        ).astimezone(timezone.utc)
                    elif (column.type.__class__.__name__ == 'Uuid'
                            and row[fieldname]):
                        row[fieldname] = UUID(row[fieldname])
            session.execute(table.insert(), data)

        session.execute(text('PRAGMA foreign_keys=ON'))
        # Validate foreign keys after inserting master data.
        session.execute(text('PRAGMA foreign_key_check'))
        session.commit()

    # Insert "admin" data (user with everything fully unlocked).
    with Session(engine) as session:
        user = User(
            user_id=UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'),
            search_id='00000000',
            name='MLTDrelive',
            money=9_999_999,
            vitality=240,
            max_vitality=240,
            live_ticket=500,
            exp=40_410_050,
            next_exp=40_500_000,
            level=900,
            theater_fan=3_978_000_000,
            last_login_date=datetime(2022, 1, 28, 4, 0, 0),
            is_tutorial_finished=True,
            producer_rank=8,
            first_time_date=datetime(2019, 8, 30, 3, 0, 0),
            max_friend=100
        )
        user.user_id_hash = b64encode(
            bytes(str(user.user_id), encoding='ascii') + bytes.fromhex(
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
        )
        user.challenge_song = ChallengeSong(
            daily_challenge_mst_song_id=1,
            update_date=datetime(1, 1, 1)
        )
        user.mission_summary = PanelMissionSheet(
            current_mst_panel_mission_sheet_id=3,
            current_panel_mission_sheet_state=3
        )
        user.map_level = MapLevel(
            user_map_level=20,
            user_recognition=100,
            actual_map_level=20,
            actual_recognition=100
        )
        user.un_lock_song_status = UnLockSongStatus()
        session.add(user)

        mst_idol_ids = session.scalars(
            select(MstIdol.mst_idol_id)
        ).all()
        for mst_idol_id in mst_idol_ids:
            session.add(Idol(
                idol_id=f'{user.user_id}_{mst_idol_id}',
                user_id=user.user_id,
                mst_idol_id=mst_idol_id,
                fan=76_500_000 if mst_idol_id != 201 else 0,
                affection=20_000_000 if mst_idol_id != 201 else 0,
                has_another_appeal=True
            ))

        mst_costume_ids = session.scalars(
            select(MstCostume.mst_costume_id)
            .where(MstCostume.mst_costume_id != 0)
        ).all()
        for mst_costume_id in mst_costume_ids:
            session.add(Costume(
                costume_id=f'{user.user_id}_{mst_costume_id}',
                user_id=user.user_id,
                mst_costume_id=mst_costume_id
            ))

        _insert_cards(session, user)

        # TODO: Filter and set amount properly
        mst_item_ids = session.scalars(
            select(MstItem.mst_item_id)
        ).all()
        for mst_item_id in mst_item_ids:
            session.add(Item(
                item_id=f'{user.user_id}_{mst_item_id}',
                user_id=user.user_id,
                mst_item_id=mst_item_id,
                amount=0
            ))

        result = session.execute(
            select(MstMemorial.mst_memorial_id, MstMemorial.is_available)
        )
        for mst_memorial_id, is_available in result:
            session.add(Memorial(
                user_id=user.user_id,
                mst_memorial_id=mst_memorial_id,
                is_released=is_available,
                is_read=is_available
            ))

        result = session.execute(
            select(MstCard.mst_card_id, MstCard.rarity)
        )
        for mst_card_id, rarity in result:
            session.add(Episode(
                user_id=user.user_id,
                mst_card_id=mst_card_id,
                is_released=True,
                is_read=True,
                mst_reward_item_id=2 if rarity == 1 else 3
            ))

        mst_theater_costume_blog_ids = session.scalars(
            select(MstTheaterCostumeBlog.mst_theater_costume_blog_id)
        ).all()
        for mst_theater_costume_blog_id in mst_theater_costume_blog_ids:
            session.add(CostumeAdv(
                user_id=user.user_id,
                mst_theater_costume_blog_id=mst_theater_costume_blog_id,
                is_released=True,
                is_read=True
            ))

        mst_gasha_ids = session.scalars(
            select(MstGasha.mst_gasha_id)
        ).all()
        for mst_gasha_id in mst_gasha_ids:
            session.add(Gasha(
                user_id=user.user_id,
                mst_gasha_id=mst_gasha_id,
                draw1_free_count=1 if mst_gasha_id == 99002 else 0,
                balloon=1 if mst_gasha_id == 99002 else 0
            ))

        result = session.execute(
            select(MstSong.mst_song_id, MstSong.is_off_vocal_available)
        )
        for mst_song_id, is_off_vocal_available in result:
            session.add(Song(
                song_id=f'{user.user_id}_{mst_song_id}',
                user_id=user.user_id,
                mst_song_id=mst_song_id,
                is_released_horizontal_mv=True,
                is_released_vertical_mv=True,
                is_cleared=True,
                first_cleared_date=user.first_time_date,
                is_played=True,
                is_off_vocal_released=is_off_vocal_available,
                is_new=False
            ))

        result = session.execute(
            select(MstCourse.mst_song_id, MstCourse.course_id)
        )
        for mst_song_id, course_id in result:
            session.add(Course(
                user_id=user.user_id,
                mst_song_id=mst_song_id,
                course_id=course_id,
                is_released=True
            ))

        for unit_num in range(1, 19):
            unit = Unit(
                user_id=user.user_id,
                unit_num=unit_num,
                name=f'團體{unit_num}'
            )
            # TODO: Default center for a new user depends on the idol
            #   type they picked during tutorial.
            unit.unit_idols.append(UnitIdol(
                position=1,
                card_id=f'{user.user_id}_59',
                mst_costume_id=14,
                mst_lesson_wear_id=14
            ))
            unit.unit_idols.append(UnitIdol(
                position=2,
                card_id=f'{user.user_id}_60',
                mst_costume_id=15,
                mst_lesson_wear_id=15
            ))
            unit.unit_idols.append(UnitIdol(
                position=3,
                card_id=f'{user.user_id}_61',
                mst_costume_id=16,
                mst_lesson_wear_id=16
            ))
            unit.unit_idols.append(UnitIdol(
                position=4,
                card_id=f'{user.user_id}_50',
                mst_costume_id=51,
                mst_lesson_wear_id=51
            ))
            unit.unit_idols.append(UnitIdol(
                position=5,
                card_id=f'{user.user_id}_51',
                mst_costume_id=52,
                mst_lesson_wear_id=52
            ))
            session.add(unit)

        result = session.execute(
            select(MstExtendSong.mst_song_id, MstExtendSong.unit_song_type,
                   MstExtendSong.song_unit_idol_id_list)
        )
        n_card_ids = session.scalars(
            select(Card.card_id)
            .join(Card.mst_card)
            .where(Card.user == user)
            .where(MstCard.rarity == 1)
            .order_by(MstCard.mst_idol_id)
        ).all()
        for mst_song_id, unit_song_type, song_unit_idol_id_list in result:
            song_unit = SongUnit(
                user_id=user.user_id,
                mst_song_id=mst_song_id,
                unit_song_type=unit_song_type,
                is_new=False
            )
            song_unit_idols = [
                int(x) for x in song_unit_idol_id_list.split(',')][
                :5 if unit_song_type == 1 else 13]
            unused_idols = [i for i in range(1, 53)]
            for i in range(len(song_unit_idols)):
                if song_unit_idols[i]:
                    unused_idols.remove(song_unit_idols[i])
                else:
                    song_unit_idols[i] = unused_idols.pop(0)
            position = 1
            for idol in song_unit_idols:
                song_unit.song_unit_idols.append(SongUnitIdol(
                    position=position,
                    card_id=n_card_ids[idol-1],
                    mst_costume_id=idol,
                    mst_lesson_wear_id=idol
                ))
                position += 1
            session.add(song_unit)
        song_unit = SongUnit(
            user_id=user.user_id,
            mst_song_id=10021,
            unit_song_type=2,
            is_new=True
        )
        for i in range(1, 14):
            song_unit.song_unit_idols.append(SongUnitIdol(
                position=i,
                card_id=n_card_ids[i-1],
                mst_costume_id=i,
                mst_lesson_wear_id=i
            ))
        session.add(song_unit)

        result = session.execute(
            select(MstMainStoryChapter.mst_main_story_id,
                   MstMainStoryChapter.chapter)
        )
        for mst_main_story_id, chapter in result:
            session.add(MainStoryChapter(
                user_id=user.user_id,
                mst_main_story_id=mst_main_story_id,
                chapter=chapter,
                released_date=user.first_time_date,
                is_released=True,
                is_read=True
            ))

        session.add(LessonWearConfig(
            user_id=user.user_id,
            mst_lesson_wear_setting_id=1
        ))

        session.add(Campaign(
            user_id=user.user_id,
            mst_campain_id=90011
        ))

        session.add(GashaMedal(
            user_id=user.user_id
        ))

        session.add(Jewel(
            user_id=user.user_id
        ))
        session.commit()

