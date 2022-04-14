import json
import sys

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, session
from flask_login import LoginManager
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from Naked.toolshed.shell import execute_js, muterun_js

from data import db_session
from data.users import User
from data.playlist import PlayList
from data.config import OAUTH_URL, REDIRECT_URL, VK_URL
from web_site.config import TOKEN, CLIENT_SECRET
from forms.playlist import PlayListRegisterForm
from forms.add_songs import AddSongForm
from forms.add_playlist_yandex import AddPlaylistYandex
from data.songs import Songs
from zenora import APIClient

from pytube import YouTube
from urllib import parse
from datetime import datetime, timedelta, date
import time
from waitress import serve
from youtubesearchpython import VideosSearch
import pyperclip

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
client = APIClient(TOKEN, client_secret=CLIENT_SECRET)

login_manager = LoginManager()
login_manager.init_app(app)


def get_album_yandex(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    album_title = soup.select_one('h1').text
    if album_title is not None:
        im_album = "https:" + soup.select_one('img[class="entity-cover__image deco-pane"]').get("src")
        songs_titles = soup.select('a[class="d-track__title deco-link deco-link_stronger"]')
        lst_songs_titles = [title.get_text("\n", strip=True)
                            for title in songs_titles]
        if url.count("/") > 4:
            im_songs = soup.select('img[class="entity-cover__image deco-pane"]')
            lst_imgs_songs = ["https:" + im.get("src") for im in im_songs]
            return album_title, im_album, lst_songs_titles, lst_imgs_songs
        return album_title, im_album, lst_songs_titles, None
    return "Альбом не найден"


def get_url_yandex(name):
    videosSearch = VideosSearch(name, limit=1)
    sec = 0
    lst = videosSearch.result()["result"][0]["duration"].split(":")
    lst.reverse()
    for i in range(len(lst)):
        sec += 60 ** i * int(lst[i])
    return videosSearch.result()["result"][0]["link"], sec, \
           videosSearch.result()["result"][0]["title"]


def get_title(url):
    return YouTube(url).title


def get_preview(url):
    video_id = parse.parse_qs(parse.urlparse(url).query)['v'][0]
    thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
    return thumbnail_url


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
        return render_template('main_page.html', current_user=current_user, playlists=playlists, songs=songs,
                               url_flag=False, command=False)
    return render_template('main_page.html', oauth_url=OAUTH_URL, current_user=None, url_flag=False, command=False)


@app.route('/url')
def url():
    pyperclip.copy('http://127.0.0.1:5000/')
    pyperclip.paste()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    db_sess = db_session.create_session()
    playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
    songs = db_sess.query(Songs).filter(Songs.playlist_id == PlayList.id, PlayList.user_id == User.id,
                                        User.user_id == current_user.id)
    return render_template('main_page.html', current_user=current_user, playlists=playlists, songs=songs,
                           url_flag=True, command=False)


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


@app.route('/yandex_add', methods=['GET', 'POST'])
def yandex_add():
    form = AddPlaylistYandex()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        name_playlist, image_playlist, lst_song_name, image_song = get_album_yandex(form.url_yandex.data)
        user = db_sess.query(User).filter(User.user_id == current_user.id).first()
        playlist_ = PlayList(name=name_playlist, user_id=user, playlist_img=image_playlist, yandex_song_flag=True)
        user.playlist.append(playlist_)
        db_sess.commit()
        for i, song in enumerate(lst_song_name):
            db_sess = db_session.create_session()
            playlist = db_sess.query(PlayList).filter(PlayList.name == name_playlist).first()
            video_length = get_url_yandex(song)[1]
            time_ = datetime.strptime(playlist.playlist_length, "%H:%M:%S").time()
            playlist.playlist_length = str(
                (datetime.combine(date.today(), time_) + timedelta(seconds=video_length)).time())
            db_sess.commit()
            if not image_song:
                if video_length >= 3600:
                    playlist = db_sess.query(PlayList).filter(PlayList.name == name_playlist).first()
                    db_sess = db_session.create_session()
                    song = Songs(name=get_url_yandex(song)[0], name_video=get_url_yandex(song)[2],
                                 video_length=str(timedelta(seconds=video_length)), playlist_id=playlist.id,
                                 video_preview=image_playlist)
                    db_sess.add(song)
                    db_sess.commit()
                else:
                    playlist = db_sess.query(PlayList).filter(PlayList.name == name_playlist).first()
                    db_sess = db_session.create_session()
                    song = Songs(name=get_url_yandex(song)[0], name_video=get_url_yandex(song)[2],
                                 video_length=time.strftime("%M:%S", time.gmtime(video_length)),
                                 playlist_id=playlist.id, video_preview=image_playlist)
                    db_sess.add(song)
                    db_sess.commit()
            else:
                if video_length >= 3600:
                    playlist = db_sess.query(PlayList).filter(PlayList.name == name_playlist).first()
                    db_sess = db_session.create_session()
                    song = Songs(name=get_url_yandex(song)[0], name_video=get_url_yandex(song)[2],
                                 video_length=str(timedelta(seconds=video_length)), playlist_id=playlist.id,
                                 video_preview=image_song[i])
                    db_sess.add(song)
                    db_sess.commit()
                else:
                    playlist = db_sess.query(PlayList).filter(PlayList.name == name_playlist).first()
                    db_sess = db_session.create_session()
                    song = Songs(name=get_url_yandex(song)[0], name_video=get_url_yandex(song)[2],
                                 video_length=time.strftime("%M:%S", time.gmtime(video_length)),
                                 playlist_id=playlist.id,
                                 video_preview=image_song[i])
                    db_sess.add(song)
                    db_sess.commit()
        return redirect("/")
    return render_template('add_playlist_yandex.html', form=form, command=False)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route('/command')
def command():
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    return render_template('command.html', current_user=current_user, command=False)


@app.route('/add_playlist', methods=['GET', 'POST'])
def add_playlist():
    form = PlayListRegisterForm()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.user_id == current_user.id).first()
        if form.img.data:
            playlist = PlayList(name=form.name.data, user_id=user, playlist_img=form.img.data)
        else:
            playlist = PlayList(name=form.name.data, user_id=user)
        playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
        songs = db_sess.query(Songs).filter(Songs.playlist_id == PlayList.id, PlayList.user_id == User.id,
                                            User.user_id == current_user.id)
        user.playlist.append(playlist)
        db_sess.commit()
        return render_template('main_page.html', playlists=playlists, current_user=current_user, songs=songs, command=False)
    return render_template('add_playlist.html', title='Новый плейлист', form=form, current_user=current_user, command=False)


@app.route('/add_songs/<playlist>', methods=['GET', 'POST'])
def add_songs(playlist):
    form = AddSongForm()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        playlist = db_sess.query(PlayList).filter(PlayList.name == playlist).first()
        video_length = YouTube(form.url.data).length
        time_ = datetime.strptime(playlist.playlist_length, "%H:%M:%S").time()
        playlist.playlist_length = str((datetime.combine(date.today(), time_) + timedelta(seconds=video_length)).time())
        if video_length >= 3600:
            song = Songs(name=form.url.data, name_video=get_title(form.url.data),
                         video_length=str(timedelta(seconds=video_length)), playlist_id=playlist.id,
                         video_preview=get_preview(form.url.data))
            db_sess.add(song)
            db_sess.commit()
        else:
            song = Songs(name=form.url.data, name_video=get_title(form.url.data),
                         video_length=time.strftime("%M:%S", time.gmtime(video_length)), playlist_id=playlist.id,
                         video_preview=get_preview(form.url.data))
            db_sess.add(song)
            db_sess.commit()
        return redirect("/")
    return render_template('add_song.html', form=form, current_user=current_user, playlist=playlist, command=False)


@app.route('/delete_songs/<int:id>', methods=['GET', 'POST'])
def delete_songs(id):
    db_sess = db_session.create_session()
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    song = db_sess.query(Songs).filter(Songs.id == id, PlayList.user_id == User.id,
                                       User.user_id == current_user.id).first()
    playlist = db_sess.query(PlayList).filter(PlayList.id == song.playlist_id).first()
    time_ = datetime.strptime(playlist.playlist_length, "%H:%M:%S").time()
    if song:
        try:
            playlist.playlist_length = str(
                (datetime.combine(date.today(), time_) - (
                    datetime.combine(date.today(), datetime.strptime(song.video_length, "%M:%S").time()))))
        except ValueError:
            playlist.playlist_length = str(
                (datetime.combine(date.today(), time_) - (
                    datetime.combine(date.today(), datetime.strptime(song.video_length, "%H:%M:%S").time()))))
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
