from datetime import datetime, timezone

from marshmallow import post_dump, pre_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested

from mltd.models.models import (LP, ChallengeSong, MapLevel, PanelMissionSheet,
                                UnLockSongStatus, User)
from mltd.servers.config import server_timezone


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        exclude = (
            'lps',
        )
        ordered = True

    challenge_song = Nested('ChallengeSongSchema')
    mission_summary = Nested('PanelMissionSheetSchema')
    map_level = Nested('MapLevelSchema')
    un_lock_song_status = Nested('UnLockSongStatusSchema')

    # @pre_dump
    # def get_datetimes(self, user: User, **kwargs):
    #     # dt = user.last_login_date
    #     # dt = dt.replace(microsecond=0, tzinfo=timezone.utc)
    #     # user.last_login_date = dt
    #     # print(user.last_login_date.__class__.__name__)
    #     # print(user.last_login_date)
    #     # print(user.last_login_date.strftime('%Y-%m-%dT%H:%M:%S+0000'))
    #     self.last_login_date = user.last_login_date
    #     self.full_recover_date = user.full_recover_date
    #     self.first_time_date = user.first_time_date
    #     return user

    @post_dump(pass_many=True)
    def _convert(self, data, many, **kwargs):
        # if 'user_id' in in_data:
        #     in_data['user_id'] = str(in_data['user_id'])
        # in_data['last_login_date'] = self.last_login_date.replace(
        #     tzinfo=timezone.utc)
        # # print(in_data['last_login_date'])
        # in_data['full_recover_date'] = self.full_recover_date.replace(
        #     tzinfo=timezone.utc)
        # in_data['first_time_date'] = self.first_time_date.replace(
        #     tzinfo=timezone.utc)
        def _convert_single(data):
            dt = datetime.fromisoformat(data['last_login_date'])
            data['last_login_date'] = dt.replace(tzinfo=timezone.utc)
            # data['last_login_date'] = dt.replace(tzinfo=timezone.utc).astimezone(server_timezone)
            dt = datetime.fromisoformat(data['full_recover_date'])
            data['full_recover_date'] = dt.replace(tzinfo=timezone.utc)
            dt = datetime.fromisoformat(data['first_time_date'])
            data['first_time_date'] = dt.replace(tzinfo=timezone.utc)
            if data['lounge_id'] is None:
                data['lounge_id'] = ''
            data['user_recognition'] = data['map_level']['user_recognition']

        if many:
            for item in data:
                _convert_single(item)
        else:
            _convert_single(data)
        return data


class PanelMissionSheetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PanelMissionSheet
        include_fk = True
        exclude = ('user_id',)


class LPSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LP


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

    # @post_dump
    # def serialize_decimals(self, in_data, **kwargs):
    #     with localcontext() as ctx:
    #         ctx.prec = 3
    #         if 'user_recognition' in in_data:
    #             in_data['user_recognition'] = str(in_data['user_recognition'])
    #         if 'actual_recognition' in in_data:
    #             in_data['actual_recognition'] = str(
    #                 in_data['actual_recognition'])
    #     return in_data


class UnLockSongStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UnLockSongStatus

