from marshmallow import post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from mltd.models.models import *
from mltd.servers.utilities import str_to_datetime

_empty_card = {
    'card_id': '',
    'mst_card_id': 0,
    'mst_idol_id': 0,
    'mst_costume_id': 0,
    'bonus_costume_id': 0,
    'rank5_costume_id': 0,
    'resource_id': '',
    'rarity': 0,
    'idol_type': 0,
    'exp': 0,
    'level': 0,
    'level_max': 0,
    'life': 0,
    'vocal': 0,
    'vocal_base': 0,
    'vocal_diff': 0,
    'vocal_max': 0,
    'vocal_master_bonus': 0,
    'dance': 0,
    'dance_base': 0,
    'dance_diff': 0,
    'dance_max': 0,
    'dance_master_bonus': 0,
    'visual': 0,
    'visual_base': 0,
    'visual_diff': 0,
    'visual_max': 0,
    'visual_master_bonus': 0,
    'before_awakened_params': {
        'life': 0,
        'vocal': 0,
        'dance': 0,
        'visual': 0
    },
    'after_awakened_params': {
        'life': 0,
        'vocal': 0,
        'dance': 0,
        'visual': 0
    },
    'skill_level': 0,
    'skill_level_max': 0,
    'is_awakened': False,
    'awakening_gauge': 0,
    'awakening_gauge_max': 0,
    'master_rank': 0,
    'master_rank_max': 0,
    'cheer_point': 0,
    'center_effect': {
        'mst_center_effect_id': 0,
        'effect_id': 0,
        'idol_type': 0,
        'specific_idol_type': 0,
        'attribute': 0,
        'value': 0,
        'song_idol_type': 0,
        'attribute2': 0,
        'value2': 0
    },
    'card_skill_list': None,
    'ex_type': 0,
    'create_date': None,
    'variation': 0,
    'master_lesson_begin_date': None,
    'training_item_list': None,
    'begin_date': None,
    'sort_id': 0,
    'is_new': False,
    'costume_list': None,
    'card_category': 0,
    'extend_card_params': {
        'level_max': 0,
        'life': 0,
        'vocal_max': 0,
        'vocal_master_bonus': 0,
        'dance_max': 0,
        'dance_master_bonus': 0,
        'visual_max': 0,
        'visual_master_bonus': 0
    },
    'is_master_lesson_five_available': False,
    'barrier_mission_list': None,
    'training_point': 0,
    'sign_type': 0,
    'sign_type2': 0
}


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        exclude = ('pending_song', 'pending_job', 'gasha_medal', 'jewel',
                   'songs', 'courses', 'cards', 'items', 'idols', 'costumes',
                   'memorials', 'episodes', 'costume_advs', 'gashas', 'units',
                   'song_units', 'main_story_chapters', 'campaigns',
                   'record_times', 'missions')
        ordered = True

    challenge_song = Nested('ChallengeSongSchema')
    mission_summary = Nested('PanelMissionSheetSchema')
    map_level = Nested('MapLevelSchema')
    un_lock_song_status = Nested('UnLockSongStatusSchema')
    lps = Nested('LPSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        data['last_login_date'] = str_to_datetime(data['last_login_date'])
        data['full_recover_date'] = str_to_datetime(data['full_recover_date'])
        data['first_time_date'] = str_to_datetime(data['first_time_date'])
        if data['lounge_id'] is None:
            data['lounge_id'] = ''
        data['user_recognition'] = data['map_level']['user_recognition']

        # Populate lp_list.
        data['lp_list'] = None if not data['lps'] else data['lps'][:10]

        # Populate type_lp_list.
        type_lp_map = {i: [] for i in range(1, 5)}
        for lp in data['lps']:
            type_lp_map[lp['idol_type']].append(lp)
        type_lp_list = []
        for i in range(1, 5):
            type_lp_list.append({
                'idol_type': i,
                'lp_song_status_list': (None if not type_lp_map[i]
                                        else type_lp_map[i]),
                'lp': sum(lp['lp'] for lp in type_lp_map[i][:10])
            })
        data['type_lp_list'] = type_lp_list
        del data['lps']

        return data


class MstIdolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstIdol
        include_relationships = True

    default_costume = Nested('MstCostumeSchema')


class IdolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Idol
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_idol = Nested('MstIdolSchema')
    lesson_wear_config = Nested('LessonWearConfigSchema')
    mst_costumes = Nested('MstCostumeSchema', many=True)
    mst_voice_categories = Nested('MstVoiceCategorySchema', many=True)
    mst_lesson_wears = Nested('MstLessonWearSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        mst_idol = data['mst_idol']
        data['resource_id'] = mst_idol['resource_id']
        data['idol_type'] = mst_idol['idol_type']
        data['tension'] = mst_idol['tension']
        data['is_best_condition'] = mst_idol['is_best_condition']
        data['area'] = mst_idol['area']
        data['offer_type'] = mst_idol['offer_type']
        data['mst_costume_id'] = 0

        # Populate having_costume_list.
        data['having_costume_list'] = [
            costume['mst_costume_id'] for costume in data['mst_costumes']]

        # Populate costume_list.
        data['costume_list'] = data['mst_costumes']
        del data['mst_costumes']

        data['favorite_costume_list'] = None

        # Populate voice_category_list.
        data['voice_category_list'] = data['mst_voice_categories']
        del data['mst_voice_categories']

        # Populate lesson_wear_list.
        data['lesson_wear_list'] = data['mst_lesson_wears']
        default_group_id = (
            data['lesson_wear_config']['mst_lesson_wear_setting_id'])
        found = False
        for lesson_wear in data['lesson_wear_list']:
            if lesson_wear['mst_lesson_wear_group_id'] == default_group_id:
                lesson_wear['default_flag'] = True
                found = True
            else:
                lesson_wear['default_flag'] = False
        if not found:
            data['lesson_wear_list'][0]['default_flag'] = True
        del data['lesson_wear_config']
        del data['mst_lesson_wears']

        data['mst_agency_id_list'] = [mst_idol['mst_agency_id']]
        data['default_costume'] = mst_idol['default_costume']
        data['birthday_live'] = mst_idol['birthday_live']
        del data['mst_idol']
        return data


class MstCostumeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCostume
        include_fk = True
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['release_date'] = str_to_datetime(
            data['release_date']).astimezone(server_timezone)
        return data


class MstCenterEffectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCenterEffect


class MstCardSkillSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCardSkill
        exclude = ('probability_base',)


class MstCardSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCard
        include_fk = True
        include_relationships = True

    mst_center_effect = Nested('MstCenterEffectSchema')
    mst_card_skill = Nested('MstCardSkillSchema')
    mst_costume = Nested('MstCostumeSchema')
    bonus_costume = Nested('MstCostumeSchema')
    rank5_costume = Nested('MstCostumeSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['master_lesson_begin_date'] = str_to_datetime(
            data['master_lesson_begin_date'])
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        return data


class CardSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Card
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_card = Nested('MstCardSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_card = data['mst_card']
        data['mst_idol_id'] = mst_card['mst_idol_id']
        data['mst_costume_id'] = mst_card['mst_costume_id']
        data['bonus_costume_id'] = mst_card['bonus_costume_id']
        data['rank5_costume_id'] = mst_card['rank5_costume_id']
        data['resource_id'] = mst_card['resource_id']
        data['rarity'] = mst_card['rarity']
        data['idol_type'] = mst_card['idol_type']
        data['level_max'] = mst_card['level_max']
        data['life'] = mst_card['life']
        data['vocal_base'] = mst_card['vocal_base']
        data['vocal_max'] = mst_card['vocal_max']
        data['vocal_master_bonus'] = mst_card['vocal_master_bonus']
        data['dance_base'] = mst_card['dance_base']
        data['dance_max'] = mst_card['dance_max']
        data['dance_master_bonus'] = mst_card['dance_master_bonus']
        data['visual_base'] = mst_card['visual_base']
        data['visual_max'] = mst_card['visual_max']
        data['visual_master_bonus'] = mst_card['visual_master_bonus']
        data['before_awakened_params'] = {
            'life': data['life'],
            'vocal': data['before_awakened_vocal'],
            'dance': data['before_awakened_dance'],
            'visual': data['before_awakened_visual']
        }
        del data['before_awakened_vocal']
        del data['before_awakened_dance']
        del data['before_awakened_visual']
        data['after_awakened_params'] = {
            'life': data['life'],
            'vocal': data['after_awakened_vocal'],
            'dance': data['after_awakened_dance'],
            'visual': data['after_awakened_visual']
        }
        del data['after_awakened_vocal']
        del data['after_awakened_dance']
        del data['after_awakened_visual']
        data['awakening_gauge_max'] = mst_card['awakening_gauge_max']
        data['master_rank_max'] = mst_card['master_rank_max']
        data['cheer_point'] = mst_card['cheer_point']
        data['center_effect'] = mst_card['mst_center_effect']
        mst_card_skill = mst_card['mst_card_skill']

        # Populate card_skill_list.
        if not mst_card_skill:
            data['card_skill_list'] = None
        else:
            mst_card_skill['probability'] = data['skill_probability']
            data['card_skill_list'] = [mst_card_skill]
        del data['skill_probability']

        data['ex_type'] = mst_card['ex_type']
        data['create_date'] = str_to_datetime(data['create_date'])
        data['variation'] = mst_card['variation']
        data['master_lesson_begin_date'] = mst_card['master_lesson_begin_date']
        data['training_item_list'] = mst_card['training_item_list']
        data['begin_date'] = mst_card['begin_date']
        data['sort_id'] = mst_card['sort_id']

        # Populate costume_list.
        costume_list = []
        if mst_card['mst_costume_id']:
            costume_list.append(mst_card['mst_costume'])
        if mst_card['bonus_costume_id']:
            costume_list.append(mst_card['bonus_costume'])
        if mst_card['rank5_costume_id']:
            costume_list.append(mst_card['rank5_costume'])
        data['costume_list'] = None if not costume_list else costume_list

        data['card_category'] = mst_card['card_category']
        data['extend_card_params'] = {
            'level_max': mst_card['extend_card_level_max'],
            'life': mst_card['extend_card_life'],
            'vocal_max': mst_card['extend_card_vocal_max'],
            'vocal_master_bonus': mst_card['extend_card_vocal_master_bonus'],
            'dance_max': mst_card['extend_card_dance_max'],
            'dance_master_bonus': mst_card['extend_card_dance_master_bonus'],
            'visual_max': mst_card['extend_card_visual_max'],
            'visual_master_bonus': mst_card['extend_card_visual_master_bonus']
        }
        data['is_master_lesson_five_available'] = (
            mst_card['is_master_lesson_five_available'])
        if not mst_card['barrier_mission_list']:
            data['barrier_mission_list'] = []
        else:
            raise NotImplementedError(
                'barrier_mission_list not expected to be non-empty')
        data['training_point'] = mst_card['training_point']
        data['sign_type'] = mst_card['sign_type']
        data['sign_type2'] = mst_card['sign_type2']
        del data['mst_card']
        return data


class MstVoiceCategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstVoiceCategory
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['release_date'] = str_to_datetime(
            data['release_date']).astimezone(server_timezone)
        return data


class MstLessonWearSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstLessonWear
        include_fk = True
        ordered = True


class MstItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstItem


class ItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_item = Nested('MstItemSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_item = data['mst_item']
        data['name'] = mst_item['name']
        data['item_navi_type'] = mst_item['item_navi_type']
        data['max_amount'] = mst_item['max_amount']
        data['item_type'] = mst_item['item_type']
        data['sort_id'] = mst_item['sort_id']
        data['value1'] = mst_item['value1']
        data['value2'] = mst_item['value2']
        data['expire_date'] = str_to_datetime(data['expire_date']).astimezone(
            server_timezone) if not mst_item['is_extend'] else None
        data['expire_date_list'] = [] if not mst_item['is_extend'] else None
        data['is_extend'] = mst_item['is_extend']
        del data['mst_item']
        return data


class MstRewardItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstRewardItem
        include_fk = True
        include_relationships = True
        exclude = ('mst_reward_item_id',)
        ordered = True

    mst_costume = Nested('MstCostumeSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        if data['mst_card_id'] != 0:
            raise NotImplementedError(
                'mst_card_id not expected to be non-zero')

        # Populate empty card_status.
        data['card_status'] = _empty_card

        # Populate costume_status.
        data['costume_status'] = data['mst_costume']
        if data['mst_costume_id'] == 0:
            data['costume_status']['resource_id'] = ''
            data['costume_status']['costume_name'] = ''
            data['costume_status']['exclude_random'] = False
            data['costume_status']['release_date'] = None
        del data['mst_costume']

        return data


class MstMemorialSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMemorial
        include_fk = True
        include_relationships = True
        exclude = ('mst_reward_item_id',)
        ordered = True

    mst_reward_item = Nested('MstRewardItemSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        return data


class MemorialSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Memorial
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_memorial = Nested('MstMemorialSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_memorial = data['mst_memorial']
        data['scenario_id'] = mst_memorial['scenario_id']
        data['mst_idol_id'] = mst_memorial['mst_idol_id']
        data['release_affection'] = mst_memorial['release_affection']
        data['number'] = mst_memorial['number']
        if data['released_date']:
            data['released_date'] = str_to_datetime(data['released_date'])

        # Populate reward_item_list.
        data['reward_item_list'] = [mst_memorial['mst_reward_item']]

        data['is_available'] = mst_memorial['is_available']
        data['begin_date'] = mst_memorial['begin_date']
        del data['mst_memorial']
        return data


class EpisodeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Episode
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'mst_reward_item_id', 'user')
        ordered = True

    mst_card = Nested('MstCardSchema')
    mst_reward_item = Nested('MstRewardItemSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['mst_idol_id'] = data['mst_card']['mst_idol_id']
        del data['mst_card']

        # Populate reward_item_list.
        data['reward_item_list'] = [data['mst_reward_item']]
        del data['mst_reward_item']

        return data


class MstTheaterCostumeBlogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTheaterCostumeBlog
        include_relationships = True

    mst_card = Nested('MstCardSchema')
    mst_reward_item = Nested('MstRewardItemSchema')


class CostumeAdvSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CostumeAdv
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_theater_costume_blog = Nested('MstTheaterCostumeBlogSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_theater_costume_blog = data['mst_theater_costume_blog']
        mst_card = mst_theater_costume_blog['mst_card']
        mst_reward_item = mst_theater_costume_blog['mst_reward_item']
        data['mst_card_id'] = mst_card['mst_card_id']
        data['mst_idol_id'] = mst_card['mst_idol_id']

        # Populate reward_item_list.
        data['reward_item_list'] = [mst_reward_item]
        del data['mst_theater_costume_blog']

        return data


class MstGashaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstGasha
        include_fk = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class GashaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Gasha
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_gasha = Nested('MstGashaSchema')
    draw1_item = Nested('ItemSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_gasha = data['mst_gasha']
        data['mst_gasha_ticket_item_id'] = mst_gasha[
            'mst_gasha_ticket_item_id']
        data['name'] = mst_gasha['name']
        data['display_category'] = mst_gasha['display_category']
        data['begin_date'] = mst_gasha['begin_date']
        data['end_date'] = mst_gasha['end_date']

        # Populate currency_type_list.
        data['currency_type_list'] = []
        if mst_gasha['currency_type_list']:
            data['currency_type_list'] = [
                int(x) for x in mst_gasha['currency_type_list'].split(',')]

        data['is_paid_jewel_only'] = mst_gasha['is_paid_jewel_only']
        data['draw1_jewel_value'] = mst_gasha['draw1_jewel_value']
        data['draw10_jewel_value'] = mst_gasha['draw10_jewel_value']
        data['draw1_mst_item_id'] = mst_gasha['draw1_mst_item_id']
        data['draw10_mst_item_id'] = mst_gasha['draw10_mst_item_id']
        data['daily_limit'] = mst_gasha['daily_limit']
        data['total_limit'] = mst_gasha['total_limit']
        data['sr_passport'] = mst_gasha['sr_passport']
        data['ssr_passport'] = mst_gasha['ssr_passport']
        data['has_new_idol'] = mst_gasha['has_new_idol']
        data['has_limited'] = mst_gasha['has_limited']
        data['notify_num'] = mst_gasha['notify_num']
        data['mst_gasha_kind_id'] = mst_gasha['mst_gasha_kind_id']
        data['mst_gasha_bonus_id'] = mst_gasha['mst_gasha_bonus_id']
        data['gasha_bonus_item_list'] = mst_gasha['gasha_bonus_item_list']
        data['gasha_bonus_mst_achievement_id_list'] = mst_gasha[
            'gasha_bonus_mst_achievement_id_list']
        data['gasha_bonus_costume_list'] = mst_gasha[
            'gasha_bonus_costume_list']

        # Populate ticket_item_list.
        data['ticket_item_list'] = []
        if mst_gasha['draw1_mst_item_id']:
            data['ticket_item_list'] = [data['draw1_item']]
        del data['draw1_item']

        data['is_limit'] = mst_gasha['is_limit']
        data['draw_point_mst_item_id'] = mst_gasha['draw_point_mst_item_id']
        data['draw_point_max'] = mst_gasha['draw_point_max']
        data['pickup_signature'] = mst_gasha['pickup_signature']
        data['pickup_gasha_card_list'] = mst_gasha['pickup_gasha_card_list']
        del data['mst_gasha']
        return data


class MstJobSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstJob
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class MstSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstSong
        include_relationships = True

    mst_extend_song = Nested('MstExtendSongSchema')


class MstExtendSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstExtendSong


class SongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Song
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_song = Nested('MstSongSchema')
    courses = Nested('CourseSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        mst_song = data['mst_song']
        del data['mst_song']

        # Populate mst_song.
        data['mst_song'] = {
            'mst_song_id': data['mst_song_id'],
            'sort_id': mst_song['sort_id'],
            'resource_id': mst_song['resource_id'],
            'idol_type': mst_song['idol_type'],
            'song_type': mst_song['song_type'],
            'kind': mst_song['kind'],
            'stage_id': mst_song['stage_id'],
            'stage_ts_id': mst_song['stage_ts_id'],
            'bpm': mst_song['bpm']
        }

        data['song_type'] = mst_song['song_type']
        data['sort_id'] = mst_song['sort_id']

        # Populate released_course_list.
        courses = data['courses']
        data['released_course_list'] = [
            course['course_id'] for course in courses if course['is_released']]

        # Populate course_list.
        data['course_list'] = []
        for course in data['courses']:
            del course['is_released']
            data['course_list'].append(course)
        del data['courses']

        data['is_released_mv'] = mst_song['is_released_mv']
        data['resource_id'] = mst_song['resource_id']
        data['idol_type'] = mst_song['idol_type']
        data['kind'] = mst_song['kind']
        data['stage_id'] = mst_song['stage_id']
        data['stage_ts_id'] = mst_song['stage_ts_id']
        data['bpm'] = mst_song['bpm']
        data['first_cleared_date'] = str_to_datetime(
            data['first_cleared_date'])
        data['is_visible'] = mst_song['is_visible']
        data['apple_song_url'] = mst_song['apple_song_url']
        data['google_song_url'] = mst_song['google_song_url']
        data['song_open_type'] = mst_song['song_open_type']
        data['song_open_type_value'] = mst_song['song_open_type_value']
        data['song_open_level'] = mst_song['song_open_level']

        # Populate song_unit_idol_id_list.
        data['song_unit_idol_id_list'] = [
            int(x) for x in mst_song['song_unit_idol_id_list'].split(',')]

        data['mst_song_unit_id'] = mst_song['mst_song_unit_id']
        data['idol_count'] = mst_song['idol_count']
        data['icon_type'] = mst_song['icon_type']

        # Populate extend_song_status.
        mst_extend_song = mst_song['mst_extend_song']
        data['extend_song_status'] = None if not mst_extend_song else {
            'resource_id': mst_extend_song['resource_id'],
            'kind': mst_extend_song['kind'],
            'stage_id': mst_extend_song['stage_id'],
            'stage_ts_id': mst_extend_song['stage_ts_id'],
            'mst_song_unit_id': mst_extend_song['mst_song_unit_id'],

            #Populate song_unit_idol_id_list.
            'song_unit_idol_id_list': [
                int(x) for x in mst_extend_song[
                    'song_unit_idol_id_list'].split(',')],

            'unit_selection_type': mst_extend_song['unit_selection_type'],
            'unit_song_type': mst_extend_song['unit_song_type'],
            'icon_type': mst_extend_song['icon_type'],
            'idol_count': mst_extend_song['idol_count'],
            'extend_type': mst_extend_song['extend_type'],
            'filter_type': mst_extend_song['filter_type'],
            'song_open_type': mst_extend_song['song_open_type'],
            'song_open_type_value': mst_extend_song['song_open_type_value'],
            'song_open_level': mst_extend_song['song_open_level']
        }

        data['unit_selection_type'] = mst_song['unit_selection_type']
        data['only_default_unit'] = mst_song['only_default_unit']
        data['only_extend'] = mst_song['only_extend']
        data['is_off_vocal_available'] = mst_song['is_off_vocal_available']

        # Populate off_vocal_status.
        if not data['is_off_vocal_available']:
            data['off_vocal_status'] = {
                'is_released': False,
                'cue_sheet': '',
                'cue_name': ''
            }
        else:
            data['off_vocal_status'] = {
                'is_released': data['is_off_vocal_released'],
                'cue_sheet': mst_song['off_vocal_cue_sheet'],
                'cue_name': mst_song['off_vocal_cue_name']
            }
        del data['is_off_vocal_released']

        data['song_permit_control'] = mst_song['song_permit_control']
        data['permitted_mst_idol_id_list'] = mst_song[
            'permitted_mst_idol_id_list']
        data['permitted_mst_agency_id_list'] = mst_song[
            'permitted_mst_agency_id_list']
        data['extend_song_playable_status'] = mst_song[
            'extend_song_playable_status']
        data['live_start_voice_mst_idol_id_list'] = mst_song[
            'live_start_voice_mst_idol_id_list']
        data['is_enable_random'] = mst_song['is_enable_random']

        # Populate part_permitted_mst_idol_id_list.
        if not mst_song['part_permitted_mst_idol_id_list']:
            data['part_permitted_mst_idol_id_list'] = None
        else:
            data['part_permitted_mst_idol_id_list'] = [
                int(x) for x in mst_song[
                    'part_permitted_mst_idol_id_list'].split(',')]

        data['is_recommend'] = mst_song['is_recommend']
        data['song_parts_type'] = mst_song['song_parts_type']
        return data


class MstCourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCourse


class CourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'mst_song_id', 'user')
        ordered = True

    mst_course = Nested('MstCourseSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['cost'] = data['mst_course']['cost']
        data['level'] = data['mst_course']['level']
        data['appeal'] = data['mst_course']['appeal']
        data['notes'] = data['mst_course']['notes']
        del data['mst_course']
        return data


class UnitSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Unit
        include_relationships = True
        exclude = ('user',)

    unit_idols = Nested('UnitIdolSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate idol_list.
        data['idol_list'] = data['unit_idols']
        del data['unit_idols']

        return data


class UnitIdolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UnitIdol
        include_fk = True
        exclude = ('user_id', 'unit_num', 'position')
        ordered = True


class SongUnitSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SongUnit
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    song_unit_idols = Nested('SongUnitIdolSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate idol_list.
        data['idol_list'] = data['song_unit_idols']
        del data['song_unit_idols']

        return data


class SongUnitIdolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SongUnitIdol
        include_fk = True
        exclude = ('user_id', 'mst_song_id', 'position')
        ordered = True


class MstMainStorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMainStory
        include_fk = True
        include_relationships = True

    reward_song = Nested('MstSongSchema')
    mst_reward_items = Nested('MstRewardItemSchema', many=True)


class MainStoryChapterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MainStoryChapter
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_main_story = Nested('MstMainStorySchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_main_story = data['mst_main_story']

        # Populate mst_idol_id_list.
        data['mst_idol_id_list'] = [
            int(x) for x in mst_main_story['mst_idol_id_list'].split(',')]

        data['release_level'] = mst_main_story['release_level']
        data['release_song_id'] = mst_main_story['release_song_id']
        data['released_date'] = str_to_datetime(data['released_date'])
        data['reward_song_id'] = mst_main_story['reward_song_id']

        # Populate reward_song.
        reward_song = mst_main_story['reward_song']
        data['reward_song'] = {
            'mst_song_id': reward_song['mst_song_id'],
            'sort_id': reward_song['sort_id'],
            'resource_id': reward_song['resource_id'],
            'idol_type': reward_song['idol_type'],
            'song_type': reward_song['song_type'],
            'kind': reward_song['kind'],
            'stage_id': reward_song['stage_id'],
            'stage_ts_id': reward_song['stage_ts_id'],
            'bpm': reward_song['bpm']
        }

        # Populate reward_extend_song.
        reward_extend_song = reward_song['mst_extend_song']
        if not reward_extend_song:
            data['reward_extend_song'] = {
                'resource_id': '',
                'kind': 0,
                'stage_id': 0,
                'stage_ts_id': 0,
                'mst_song_unit_id': 0,
                'song_unit_idol_id_list': None,
                'unit_selection_type': 0,
                'unit_song_type': 0,
                'icon_type': 0,
                'idol_count': 0,
                'extend_type': 0,
                'filter_type': 0,
                'song_open_type': 0,
                'song_open_type_value': 0,
                'song_open_level': 0
            }
        else:
            data['reward_extend_song'] =  {
                'resource_id': reward_extend_song['resource_id'],
                'kind': reward_extend_song['kind'],
                'stage_id': reward_extend_song['stage_id'],
                'stage_ts_id': reward_extend_song['stage_ts_id'],
                'mst_song_unit_id': reward_extend_song['mst_song_unit_id'],

                #Populate song_unit_idol_id_list.
                'song_unit_idol_id_list': [
                    int(x) for x in reward_extend_song[
                        'song_unit_idol_id_list'].split(',')],

                'unit_selection_type': reward_extend_song[
                    'unit_selection_type'],
                'unit_song_type': reward_extend_song['unit_song_type'],
                'icon_type': reward_extend_song['icon_type'],
                'idol_count': reward_extend_song['idol_count'],
                'extend_type': reward_extend_song['extend_type'],
                'filter_type': reward_extend_song['filter_type'],
                'song_open_type': reward_extend_song['song_open_type'],
                'song_open_type_value': reward_extend_song[
                    'song_open_type_value'],
                'song_open_level': reward_extend_song['song_open_level']
            }

        data['number'] = mst_main_story['number']

        # Populate reward_item_list.
        data['reward_item_list'] = mst_main_story['mst_reward_items']

        data['intro_contact_mst_idol_id'] = mst_main_story[
            'intro_contact_mst_idol_id']
        data['blog_contact_mst_idol_id'] = mst_main_story[
            'blog_contact_mst_idol_id']
        del data['mst_main_story']
        return data


class MstTheaterRoomStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTheaterRoomStatus
        include_fk = True
        include_relationships = True

    mst_theater_room_idols = Nested('MstTheaterRoomIdolSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        return {
            'mst_room_id': data['mst_room_id'],
            'balloon': {
                'theater_contact_category_type': data[
                    'theater_contact_category_type'],
                'room_idol_list': data['mst_theater_room_idols'],
                'resource_id': data['resource_id'],
                'mst_theater_contact_schedule_id': data[
                    'mst_theater_contact_schedule_id'],
                'mst_theater_contact_id': data['mst_theater_contact_id'],
                'mst_theater_main_story_id': data['mst_theater_main_story_id'],
                'mst_theater_guest_main_story_id': data[
                    'mst_theater_guest_main_story_id'],
                'guest_main_story_has_intro': data[
                    'guest_main_story_has_intro'],
                'mst_guest_main_story_id': data['mst_guest_main_story_id'],
                'mst_theater_blog_id': data['mst_theater_blog_id'],
                'mst_theater_costume_blog_id': data[
                    'mst_theater_costume_blog_id'],
                'mst_costume_id': data['mst_costume_id'],
                'mst_theater_event_story_id': data[
                    'mst_theater_event_story_id'],
                'mst_event_story_id': data['mst_event_story_id'],
                'mst_event_id': data['mst_event_id']
            }
        }


class MstTheaterRoomIdolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTheaterRoomIdol
        include_fk = True
        exclude = ('mst_theater_contact_id', 'mst_theater_main_story_id',
                   'mst_theater_guest_main_story_id', 'mst_theater_blog_id',
                   'mst_theater_costume_blog_id', 'mst_theater_event_story_id')
        ordered = True


class MstMainStoryContactStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMainStoryContactStatus
        include_fk = True
        include_relationships = True

    mst_theater_room_status = Nested('MstTheaterRoomStatusSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        return {
            'mst_main_story_id': data['mst_main_story_id'],
            'theater_room_status': data['mst_theater_room_status'],
            'duration': data['duration']
        }


class MstAwakeningConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstAwakeningConfig
        include_fk = True
        include_relationships = True
        ordered = True

    mst_awakening_config_items = Nested('MstAwakeningConfigItemSchema',
                                        many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate required_item_list.
        data['required_item_list'] = data['mst_awakening_config_items']
        del data['mst_awakening_config_items']

        if not data['mst_card_id']:
            data['mst_card_id'] = 0
        return data


class MstAwakeningConfigItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstAwakeningConfigItem
        include_fk = True
        exclude = ('rarity', 'idol_type')
        ordered = True


class MstMasterLesson2ConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMasterLesson2Config
        include_relationships = True
        ordered = True

    mst_master_lesson2_config_items = Nested(
        'MstMasterLesson2ConfigItemSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate master_piece_list.
        data['master_piece_list'] = data['mst_master_lesson2_config_items']
        del data['mst_master_lesson2_config_items']

        return data


class MstMasterLesson2ConfigItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMasterLesson2ConfigItem
        include_fk = True
        exclude = ('rarity', 'idol_type')
        ordered = True


class MstExMasterLessonConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstExMasterLessonConfig
        include_fk = True
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate amount.
        data['amount'] = [int(x) for x in data['amount'].split(',')]

        if not data['mst_card_id']:
            data['mst_card_id'] = 0
        return data


class MstLessonMoneyConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstLessonMoneyConfig
        include_fk = True
        ordered = True


class MstLessonSkillLevelUpConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstLessonSkillLevelUpConfig
        ordered = True


class MstLessonWearConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstLessonWearConfig

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate mst_lesson_wear_group_id_list.
        data['mst_lesson_wear_group_id_list'] = [
            data['mst_lesson_wear_group_id_list']]

        return data


class LessonWearConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LessonWearConfig
        include_fk = True
        exclude = ('user_id',)


class MstComicMenuSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstComicMenu
        ordered = True


class MstTrainingUnitSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTrainingUnit

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate idol_id_list.
        data['idol_id_list'] = [
            int(x) for x in data['idol_id_list'].split(',')]

        return data


class MstMasterLessonFiveConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMasterLessonFiveConfig
        include_relationships = True
        sorted = True

    mst_master_lesson_five_config_items = Nested(
        'MstMasterLessonFiveConfigItemSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate required_item_list.
        data['required_item_list'] = data[
            'mst_master_lesson_five_config_items']
        del data['mst_master_lesson_five_config_items']

        return data


class MstMasterLessonFiveConfigItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMasterLessonFiveConfigItem
        include_fk = True
        ordered = True
        exclude = ('ex_type', 'idol_type')


class MstTitleImageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTitleImage
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class MstGameSettingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstGameSetting
        include_relationships = True
        exclude = ('mst_game_setting_id',)
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate recover_jewel.
        data['recover_jewel'] = [
            {
                'amount': data['recover_jewel_amount'],
                'begin_date': str_to_datetime(
                    data['recover_jewel_begin_date']).astimezone(
                    server_timezone),
                'end_date': str_to_datetime(
                    data['recover_jewel_end_date']).astimezone(server_timezone)
            }
        ]
        del data['recover_jewel_amount']
        del data['recover_jewel_begin_date']
        del data['recover_jewel_end_date']

        # Populate continue_jewel.
        data['continue_jewel'] = [
            {
                'amount': data['continue_jewel_amount'],
                'begin_date': str_to_datetime(
                    data['continue_jewel_begin_date']).astimezone(
                    server_timezone),
                'end_date': str_to_datetime(
                    data['continue_jewel_end_date']).astimezone(
                    server_timezone)
            }
        ]
        del data['continue_jewel_amount']
        del data['continue_jewel_begin_date']
        del data['continue_jewel_end_date']

        data['overflow_date'] = str_to_datetime(
            data['overflow_date']).astimezone(server_timezone)

        # Populate lounge_chat_fetch_cycle.
        data['lounge_chat_fetch_cycle'] = [
            int(x) for x in data['lounge_chat_fetch_cycle'].split(',')]

        # Populate un_lock_song_jewel.
        data['un_lock_song_jewel'] = [
            {
                'amount': data['un_lock_song_jewel_amount'],
                'begin_date': str_to_datetime(
                    data['un_lock_song_jewel_begin_date']).astimezone(
                    server_timezone),
                'end_date': str_to_datetime(
                    data['un_lock_song_jewel_end_date']).astimezone(
                    server_timezone)
            }
        ]
        del data['un_lock_song_jewel_amount']
        del data['un_lock_song_jewel_begin_date']
        del data['un_lock_song_jewel_end_date']

        # Populate function_release_id_list.
        data['function_release_id_list'] = [
            int(x) for x in data['function_release_id_list'].split(',')]

        return data


class MstLoadingCharacterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstLoadingCharacter
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class MstCampaignSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCampaign

    @post_dump
    def _convert(self, data, **kwargs):
        data['start_date'] = str_to_datetime(data['start_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class CampaignSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Campaign
        include_relationships = True
        exclude = ('user',)

    mst_campaign = Nested('MstCampaignSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['mst_campain_id'] = data['mst_campaign']['mst_campain_id']
        data['type'] = data['mst_campaign']['type']
        data['value'] = data['mst_campaign']['value']

        # Populate footer_button.
        data['footer_button'] = [data['mst_campaign']['footer_button']]

        data['start_date'] = data['mst_campaign']['start_date']
        data['end_date'] = data['mst_campaign']['end_date']
        del data['mst_campaign']
        return data


class GashaMedalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GashaMedal
        include_relationships = True
        exclude = ('user',)

    gasha_medal_expire_dates = Nested('GashaMedalExpireDateSchema', many=True)

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate expire_date_list.
        data['expire_date_list'] = [
            expire_date['expire_date']
            for expire_date in data['gasha_medal_expire_dates']]
        del data['gasha_medal_expire_dates']

        return data


class GashaMedalExpireDateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GashaMedalExpireDate

    @post_dump
    def _convert(self, data, **kwargs):
        data['expire_date'] = str_to_datetime(data['expire_date'])
        return data


class JewelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Jewel
        ordered = True


class RecordTimeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RecordTime
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['time'] = str_to_datetime(data['time'])
        return data


class MstTopicsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstTopics
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['release_date'] = str_to_datetime(
            data['release_date']).astimezone(server_timezone)
        return data


class MstEventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstEvent
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        data['page_begin_date'] = str_to_datetime(
            data['page_begin_date']).astimezone(server_timezone)
        data['page_end_date'] = str_to_datetime(
            data['page_end_date']).astimezone(server_timezone)
        data['boost_begin_date'] = str_to_datetime(data['boost_begin_date'])
        data['boost_end_date'] = str_to_datetime(data['boost_end_date'])
        return data


class MstEventTalkStorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstEventTalkStory

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate mst_event_talk_speaker_id.
        data['mst_event_talk_speaker_id'] = [
            int(x) for x in data['mst_event_talk_speaker_id'].split(',')]

        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        return data


class EventTalkStorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventTalkStory
        include_fk = True
        include_relationships = True
        exclude = ('user_id',)
        ordered = True

    mst_event_talk_story = Nested('MstEventTalkStorySchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_event_talk_story = data['mst_event_talk_story']
        data['episode'] = mst_event_talk_story['episode']
        data['release_event_point'] = mst_event_talk_story[
            'release_event_point']
        data['mst_event_talk_speaker_id'] = mst_event_talk_story[
            'mst_event_talk_speaker_id']
        data['bg_id'] = mst_event_talk_story['bg_id']
        data['thumbnail_id'] = mst_event_talk_story['thumbnail_id']
        data['begin_date'] = mst_event_talk_story['begin_date']
        del data['mst_event_talk_story']
        data['released_date'] = str_to_datetime(data['released_date'])
        return data


class MstEventTalkCallTextSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstEventTalkCallText
        ordered = True


class MstEventTalkControlSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstEventTalkControl
        include_fk = True
        include_relationships = True
        exclude = ('mst_reward_item_id', 'mst_event')
        ordered = True

    mst_reward_item = Nested('MstRewardItemSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        # Populate reward_item_list.
        data['reward_item_list'] = [data['mst_reward_item']]
        del data['mst_reward_item']

        return data


class MstMissionScheduleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMissionSchedule
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)
        return data


class MstPanelMissionSheetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstPanelMissionSheet
        include_relationships = True
        ordered = True

    mst_mission_reward = Nested('MstMissionRewardSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        data['begin_date'] = str_to_datetime(data['begin_date']).astimezone(
            server_timezone)
        data['end_date'] = str_to_datetime(data['end_date']).astimezone(
            server_timezone)

        # Populate sheet_reward_list.
        data['sheet_reward_list'] = [data['mst_mission_reward']]
        del data['mst_mission_reward']
        return data


class PanelMissionSheetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PanelMissionSheet
        include_fk = True
        exclude = ('user_id',)


class MstMissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMission
        include_relationships = True

    mst_mission_rewards = Nested('MstMissionRewardSchema', many=True)


class MstMissionRewardSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstMissionReward
        include_fk = True
        exclude = ('mst_mission_id', 'mst_panel_mission_id',
                   'mst_idol_mission_id', 'mst_panel_mission_sheet_id')
        ordered = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['mst_card_id'] = 0

        # Populate empty card.
        data['card'] = _empty_card

        if not data['mst_song_id']:
            data['mst_song_id'] = 0

        # Populate empty song (defer populating non-empty song to
        # service implementation because user_id is required).
        if not data['mst_song_id']:
            data['song'] = {
                'song_id': '',
                'mst_song_id': 0,
                'mst_song': {
                    'mst_song_id': 0,
                    'sort_id': 0,
                    'resource_id': '',
                    'idol_type': 0,
                    'song_type': 0,
                    'kind': 0,
                    'stage_id': 0,
                    'stage_ts_id': 0,
                    'bpm': 0
                },
                'song_type': 0,
                'sort_id': 0,
                'released_course_list': None,
                'course_list': None,
                'is_released_mv': False,
                'is_released_horizontal_mv': False,
                'is_released_vertical_mv': False,
                'resource_id': '',
                'idol_type': 0,
                'kind': 0,
                'stage_id': 0,
                'stage_ts_id': 0,
                'bpm': 0,
                'is_cleared': False,
                'first_cleared_date': None,
                'is_played': False,
                'lp': 0,
                'is_visible': False,
                'apple_song_url': '',
                'google_song_url': '',
                'is_disable': False,
                'song_open_type': 0,
                'song_open_type_value': 0,
                'song_open_level': 0,
                'song_unit_idol_id_list': None,
                'mst_song_unit_id': 0,
                'idol_count': 0,
                'icon_type': 0,
                'extend_song_status': None,
                'unit_selection_type': 0,
                'only_default_unit': False,
                'only_extend': False,
                'is_off_vocal_available': False,
                'off_vocal_status': {
                    'is_released': False,
                    'cue_sheet': '',
                    'cue_name': ''
                },
                'song_permit_control': False,
                'permitted_mst_idol_id_list': None,
                'permitted_mst_agency_id_list': None,
                'extend_song_playable_status': 0,
                'is_new': False,
                'live_start_voice_mst_idol_id_list': None,
                'is_enable_random': False,
                'part_permitted_mst_idol_id_list': None,
                'is_recommend': False,
                'song_parts_type': 0
            }
        return data


class MissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mission
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'user')
        ordered = True

    mst_mission = Nested('MstMissionSchema')

    @post_dump
    def _convert(self, data, **kwargs):
        mst_mission = data['mst_mission']
        if mst_mission['mission_type'] <= 3:
            data['mission_type'] = 0
        else:
            data['mission_type'] = mst_mission['mission_type']
        data['mst_mission_class_id'] = mst_mission['mst_mission_class_id']
        data['goal'] = mst_mission['goal']
        data['option'] = mst_mission['option']
        data['option2'] = mst_mission['option2']

        # Populate premise_mst_mission_id_list.
        data['premise_mst_mission_id_list'] = (
            [] if mst_mission['premise_mst_mission_id_list'] is None
            else [mst_mission['premise_mst_mission_id_list']])

        # Populate mission_reward_list.
        data['mission_reward_list'] = mst_mission['mst_mission_rewards']

        data['create_date'] = str_to_datetime(data['create_date'])
        data['update_date'] = str_to_datetime(data['update_date'])
        data['finish_date'] = str_to_datetime(data['finish_date'])
        data['sort_id'] = mst_mission['sort_id']
        data['jump_type'] = mst_mission['jump_type']
        data['mission_operation_label'] = mst_mission[
            'mission_operation_label']
        del data['mst_mission']
        return data


class LPSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LP
        include_fk = True
        include_relationships = True
        exclude = ('user_id', 'update_date', 'user')

    mst_course = Nested('MstCourseSchema', only=('level',))
    mst_song = Nested('MstSongSchema',
                      only=('idol_type', 'resource_id', 'sort_id'))

    @post_dump
    def _convert(self, data, **kwargs):
        data['level'] = data['mst_course']['level']
        data['idol_type'] = data['mst_song']['idol_type']
        data['resourse_id'] = data['mst_song']['resource_id']
        data['sort_id'] = data['mst_song']['sort_id']
        del data['mst_course']
        del data['mst_song']
        return data


class ChallengeSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ChallengeSong
        include_fk = True
        exclude = ('user_id',)

    @post_dump
    def _convert(self, data, **kwargs):
        data['update_date'] = str_to_datetime(data['update_date'])
        return data


class MapLevelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MapLevel


class UnLockSongStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UnLockSongStatus

