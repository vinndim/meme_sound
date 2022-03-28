import datetime

import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    playlist = orm.relation("PlayList", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'<User> {self.name} {self.email} {self.hashed_password}'
