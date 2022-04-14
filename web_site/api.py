import flask
from flask import jsonify, session

from data import db_session
from data.playlist import PlayList
from data.songs import Songs
from data.users import User
from web_site.config import TOKEN, CLIENT_SECRET
from zenora import APIClient

blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)

client = APIClient(TOKEN, client_secret=CLIENT_SECRET)


@blueprint.route('/api/<str:user_id>')
def get_playlists(user_id):
    db_sess = db_session.create_session()
    playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == user_id)
    print(playlists)
    return jsonify(
        {
            'playlists':
                ([item.to_dict(only=('name', 'user.name', 'songs.name'))
                 for item in playlists])
        }
    )
