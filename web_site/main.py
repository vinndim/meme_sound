from flask import Flask, render_template, request, session
from flask_login import LoginManager
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from data.playlist import PlayList
from data.config import OAUTH_URL, REDIRECT_URL
from web_site.config import TOKEN, CLIENT_SECRET
from forms.playlist import PlayListRegisterForm
from zenora import APIClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
client = APIClient(TOKEN, client_secret=CLIENT_SECRET)

login_manager = LoginManager()
login_manager.init_app(app)


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
        user = db_sess.query(User).filter(User.id == 1).first()
        playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
        return render_template('main_page.html', current_user=current_user, playlists=playlists)
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
        user = db_sess.query(User).filter(User.id == 1).first()
        playlist = PlayList(name=form.name.data, command=form.command.data, user_id=user)
        playlists = db_sess.query(PlayList).filter(PlayList.user_id == User.id, User.user_id == current_user.id)
        user.playlist.append(playlist)
        db_sess.commit()
        return render_template('main_page.html', playlists=playlists, current_user=current_user)
    return render_template('add_playlist.html', title='Новый плейлист', form=form, current_user=current_user)


if __name__ == '__main__':
    main()
