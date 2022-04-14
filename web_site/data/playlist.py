import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class PlayList(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'playlist'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    playlist_length = sqlalchemy.Column(sqlalchemy.String, default='0:00:00', nullable=False)
    user = orm.relation('User')
    songs = orm.relation("Songs", back_populates='playlist')

    def __repr__(self):
        return self.name
