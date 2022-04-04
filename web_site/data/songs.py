import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Songs(SqlAlchemyBase, UserMixin):
    __tablename__ = 'songs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("playlist.name"), nullable=True)
    name_video = sqlalchemy.Column(sqlalchemy.String)
    video_length = sqlalchemy.Column(sqlalchemy.String)
    playlist_id = sqlalchemy.Column(sqlalchemy.Integer)
    playlist = orm.relation('PlayList')

    def __repr__(self):
        return self.name, self.playlist_id
