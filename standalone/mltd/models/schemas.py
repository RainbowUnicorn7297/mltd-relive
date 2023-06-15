from datetime import datetime, timezone

from marshmallow import post_dump, pre_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested

from mltd.models.models import *
from mltd.servers.config import server_timezone


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        exclude = ('pending_song', 'pending_job', 'songs')
        ordered = True

    challenge_song = Nested('ChallengeSongSchema')
    mission_summary = Nested('PanelMissionSheetSchema')
    map_level = Nested('MapLevelSchema')
    un_lock_song_status = Nested('UnLockSongStatusSchema')
    lps = Nested('LPSchema', many=True)

    @post_dump(pass_many=True)
    def _convert(self, data, many, **kwargs):
        def _convert_single(data):
            dt = datetime.fromisoformat(data['last_login_date'])
            data['last_login_date'] = dt.replace(tzinfo=timezone.utc)
            dt = datetime.fromisoformat(data['full_recover_date'])
            data['full_recover_date'] = dt.replace(tzinfo=timezone.utc)
            dt = datetime.fromisoformat(data['first_time_date'])
            data['first_time_date'] = dt.replace(tzinfo=timezone.utc)
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

        if many:
            for item in data:
                _convert_single(item)
        else:
            _convert_single(data)
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

    @post_dump(pass_many=True)
    def _convert(self, data, many, **kwargs):
        def _convert_single(data):
            data['level'] = data['mst_course']['level']
            data['idol_type'] = data['mst_song']['idol_type']
            data['resourse_id'] = data['mst_song']['resource_id']
            data['sort_id'] = data['mst_song']['sort_id']
            del data['mst_course']
            del data['mst_song']

        if many:
            for item in data:
                _convert_single(item)
        else:
            _convert_single(data)
        return data


class ChallengeSongSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ChallengeSong
        include_fk = True
        exclude = ('user_id',)

    @post_dump(pass_many=True)
    def _convert(self, data, many, **kwargs):
        def _convert_single(data):
            dt = datetime.fromisoformat(data['update_date'])
            data['update_date'] = dt.replace(tzinfo=timezone.utc)

        if many:
            for item in data:
                _convert_single(item)
        else:
            _convert_single(data)
        return data


class MapLevelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MapLevel


class UnLockSongStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UnLockSongStatus

