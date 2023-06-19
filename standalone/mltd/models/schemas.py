from marshmallow import post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from mltd.models.models import *
from mltd.servers.utilities import str_to_datetime


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        exclude = ('pending_song', 'pending_job', 'songs', 'cards', 'items',
                   'idols', 'costumes')
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
        data['card_status'] = {
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


class MstSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstSong


class MstCourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCourse


class LessonWearConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LessonWearConfig
        include_fk = True
        exclude = ('user_id',)


class PanelMissionSheetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PanelMissionSheet
        include_fk = True
        exclude = ('user_id',)


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

