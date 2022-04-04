import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, session
from flask_login import LoginManager
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from data.playlist import PlayList
from data.config import OAUTH_URL, REDIRECT_URL
from web_site.config import TOKEN, CLIENT_SECRET
from forms.playlist import PlayListRegisterForm
from forms.add_songs import AddSongForm
from data.songs import Songs
from zenora import APIClient

from pytube import YouTube
from datetime import datetime, timedelta, date
import time
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
client = APIClient(TOKEN, client_secret=CLIENT_SECRET)

login_manager = LoginManager()
login_manager.init_app(app)


def get_title(url):
    return YouTube(url).title


def main():
    db_session.global_init('db/users.db')
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    if 'token' in session:
        bearer_client = APIClient(session.get('token'), bearer=True)
        current_user = bearer_client.users.get_current_user()
        db_sess = db_session.create_session()
        playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
        songs = db_sess.query(Songs).filter(Songs.playlist_id == PlayList.id, PlayList.user_id == User.id,
                                            User.user_id == current_user.id)
        print(songs)
        return render_template('main_page.html', current_user=current_user, playlists=playlists, songs=songs)
    return render_template('main_page.html', oauth_url=OAUTH_URL, current_user=None)


@app.route('/login')
def login():
    code = request.args['code']
    access_token = client.oauth.get_access_token(code, REDIRECT_URL).access_token
    session['token'] = access_token
    db_sess = db_session.create_session()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    try:
        user = User(name=current_user.username, user_id=current_user.id)
        db_sess.add(user)
        db_sess.commit()
    except IntegrityError:
        pass
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route('/add_playlist', methods=['GET', 'POST'])
def add_playlist():
    form = PlayListRegisterForm()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.user_id == current_user.id).first()
        playlist = PlayList(name=form.name.data, user_id=user)
        playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
        songs = db_sess.query(Songs).filter(Songs.playlist_id == PlayList.id, PlayList.user_id == User.id,
                                            User.user_id == current_user.id)
        user.playlist.append(playlist)
        db_sess.commit()
        return render_template('main_page.html', playlists=playlists, current_user=current_user, songs=songs)
    return render_template('add_playlist.html', title='Новый плейлист', form=form, current_user=current_user)


@app.route('/add_songs/<playlist>', methods=['GET', 'POST'])
def add_songs(playlist):
    form = AddSongForm()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        playlist = db_sess.query(PlayList).filter(PlayList.name == playlist).first()
        video_length = YouTube(form.url.data).length
        print(playlist.playlist_length)
        time_ = datetime.strptime(playlist.playlist_length, "%H:%M:%S").time()
        print(time_)
        playlist.playlist_length = str((datetime.combine(date.today(), time_) + timedelta(seconds=video_length)).time())
        if video_length >= 3600:
            song = Songs(name=form.url.data, name_video=get_title(form.url.data),
                         video_length=timedelta(seconds=video_length), playlist_id=playlist.id)
            db_sess.add(song)
            db_sess.commit()
        else:
            song = Songs(name=form.url.data, name_video=get_title(form.url.data),
                         video_length=time.strftime("%M:%S", time.gmtime(video_length)), playlist_id=playlist.id)
            db_sess.add(song)
            db_sess.commit()
        return redirect("/")
    return render_template('add_song.html', form=form, current_user=current_user, playlist=playlist)


@app.route('/delete_songs/<int:id>', methods=['GET', 'POST'])
def delete_songs(id):
    db_sess = db_session.create_session()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    song = db_sess.query(Songs).filter(Songs.id == id, PlayList.user_id == User.id,
                                       User.user_id == current_user.id).first()
    if song:
        db_sess.delete(song)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/delete_playlist/<int:id>', methods=['GET', 'POST'])
def delete_playlist(id):
    db_sess = db_session.create_session()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    playlist = db_sess.query(PlayList).filter(PlayList.id == id, PlayList.user_id == User.id,
                                              User.user_id == current_user.id).first()
    songs = db_sess.query(Songs).filter(Songs.playlist_id == id, PlayList.user_id == User.id,
                                        User.user_id == current_user.id)
    if playlist:
        for song in songs:
            db_sess.delete(song)
        db_sess.delete(playlist)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
