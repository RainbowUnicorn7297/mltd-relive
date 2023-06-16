from marshmallow import post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from mltd.models.models import *
from mltd.servers.utilities import str_to_datetime


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        exclude = ('pending_song', 'pending_job', 'songs', 'cards')
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


class MstCostumeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCostume
        include_fk = True

    @post_dump
    def _convert(self, data, **kwargs):
        data['release_date'] = str_to_datetime(data['release_date'])
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
        data['begin_date'] = str_to_datetime(data['begin_date'])
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
        data['awakening_gauge_max'] = mst_card['awakening_guage_max']
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


class MstSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstSong


class MstCourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MstCourse


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

