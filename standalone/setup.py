import csv
from base64 import b64encode
from os import listdir
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from mltd.models.engine import engine
from mltd.models.models import *
from mltd.servers.config import server_language, server_timezone


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

        # TODO: For a new user, Shika's card is already at max level.
        # level=60 (level=70 after awakened)
        # exp=47610
        # skill_level=10
        # awakening_gauge=300
        # master_rank=0
        # skill_probability=45
        _insert_cards(session, user)

        # TODO: Filter and set amount properly
        mst_item_ids = session.scalars(
            select(MstItem.mst_item_id)
            .where(MstItem.is_visible == True)
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
                name=f'{"團體" if server_language == "zh" else "유닛"}'
                    + f'{unit_num}'
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

        result = session.execute(
            select(MstEventTalkStory.mst_event_talk_story_id,
                   MstEventTalkStory.begin_date)
        )
        for mst_event_talk_story_id, begin_date in result:
            session.add(EventTalkStory(
                user_id=user.user_id,
                mst_event_talk_story_id=mst_event_talk_story_id,
                released_date=begin_date,
                is_released=True,
                is_read=True
            ))

        result = session.execute(
            select(MstMission.mst_mission_id, MstMission.mst_panel_mission_id,
                   MstMission.mst_idol_mission_id, MstMission.goal)
        )
        for (mst_mission_id, mst_panel_mission_id, mst_idol_mission_id,
             goal) in result:
            session.add(Mission(
                user_id=user.user_id,
                mst_mission_id=mst_mission_id,
                mst_panel_mission_id=mst_panel_mission_id,
                mst_idol_mission_id=mst_idol_mission_id,
                finish_date=datetime.now(timezone.utc),
                progress=goal,
                mission_state=3
            ))

        mst_special_story_ids = session.scalars(
            select(MstSpecialStory.mst_special_story_id)
        ).all()
        for mst_special_story_id in mst_special_story_ids:
            session.add(SpecialStory(
                user_id=user.user_id,
                mst_special_story_id=mst_special_story_id,
                is_released=True if mst_special_story_id != 0 else False,
                is_read=True if mst_special_story_id != 0 else False
            ))

        result = session.execute(
            select(MstEventStory.mst_event_story_id, MstEventStory.begin_date)
        )
        for mst_event_story_id, begin_date in result:
            session.add(EventStory(
                user_id=user.user_id,
                mst_event_story_id=mst_event_story_id,
                released_date=begin_date,
                is_released=True,
                is_read=True
            ))

        mst_event_memory_ids = session.scalars(
            select(MstEventMemory.mst_event_memory_id)
        ).all()
        for mst_event_memory_id in mst_event_memory_ids:
            session.add(EventMemory(
                user_id=user.user_id,
                mst_event_memory_id=mst_event_memory_id,
                is_released=True
            ))

        mst_login_bonus_schedule_ids = session.scalars(
            select(MstLoginBonusSchedule.mst_login_bonus_schedule_id)
        ).all()
        for mst_login_bonus_schedule_id in mst_login_bonus_schedule_ids:
            login_bonus_schedule = LoginBonusSchedule(
                user_id=user.user_id,
                mst_login_bonus_schedule_id=mst_login_bonus_schedule_id,
                next_login_date=datetime(2022, 1, 28, 16, 0, 0)
            )
            days = session.scalars(
                select(MstLoginBonusItem.day)
                .where(MstLoginBonusItem.mst_login_bonus_schedule_id
                       == mst_login_bonus_schedule_id)
            ).all()
            for day in days:
                login_bonus_schedule.login_bonus_items.append(LoginBonusItem(
                    day=day
                ))
            session.add(login_bonus_schedule)

        result = session.execute(
            select(MstOfferText.mst_offer_text_id, MstOfferText.evaluation)
        ).all()
        for mst_offer_text_id, evaluation in result:
            session.add(OfferText(
                user_id=user.user_id,
                mst_offer_text_id=mst_offer_text_id,
                evaluation=evaluation,
                acquired=True
            ))
        session.add(OfferSummary(
            user_id=user.user_id,
            concurrency_max_count=3,
            offers_completed=len(result)
        ))

        card_ids = session.scalars(
            select(Card.card_id)
        ).all()
        # TODO: Default favorite card & idol_type=4 helper card for a
        #   new user depends on the idol type they picked during
        #   tutorial.
        profile = Profile(
            id_=user.user_id,
            name=user.name,
            birthday='0830',
            is_birthday_public=True,
            favorite_card_id=f'{user.user_id}_59',
            album_count=len(card_ids) * 2,
            story_count=len(card_ids) * 2
        )
        profile.helper_cards.append(HelperCard(
            idol_type=1,
            card_id=f'{user.user_id}_59',
        ))
        profile.helper_cards.append(HelperCard(
            idol_type=2,
            card_id=f'{user.user_id}_60',
        ))
        profile.helper_cards.append(HelperCard(
            idol_type=3,
            card_id=f'{user.user_id}_61',
        ))
        profile.helper_cards.append(HelperCard(
            idol_type=4,
            card_id=f'{user.user_id}_59',
        ))
        for i in range(1, 7):
            profile.clear_song_counts.append(ClearSongCount(
                live_course=i,
                count=0
            ))
            profile.full_combo_song_counts.append(FullComboSongCount(
                live_course=i,
                count=0
            ))
        session.add(profile)

        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=1,
            last_update_date=user.last_login_date
        ))
        for i in range(2, 8):
            session.add(LastUpdateDate(
                user_id=user.user_id,
                last_update_date_type=i
            ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=8,
            last_update_date=datetime(2022, 1, 27, 4)
        ))
        for i in range(9, 11):
            session.add(LastUpdateDate(
                user_id=user.user_id,
                last_update_date_type=i,
                last_update_date=(
                    datetime(2021, 9, 27, 15, tzinfo=server_timezone)
                    .astimezone(timezone.utc))
            ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=11,
            last_update_date=(
                datetime(2018, 1, 1, 0, 0, 18, tzinfo=server_timezone)
                .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=12,
            last_update_date=(datetime(2021, 8, 31, 15, tzinfo=server_timezone)
                              .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=13,
            last_update_date=(datetime(2021, 9, 27, 12, tzinfo=server_timezone)
                              .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=17,
            last_update_date=(datetime(2021, 6, 29, tzinfo=server_timezone)
                              .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=14,
            last_update_date=(datetime(2021, 9, 26, tzinfo=server_timezone)
                              .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=15,
            last_update_date=(datetime(2020, 11, 5, 15, tzinfo=server_timezone)
                              .astimezone(timezone.utc))
        ))
        session.add(LastUpdateDate(
            user_id=user.user_id,
            last_update_date_type=16
        ))
        session.commit()

