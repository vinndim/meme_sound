from flask import Flask, render_template, request, session
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import redirect

from data import db_session
from data.forms import LoginForm
from data.users import User
from data.playlist import PlayList
from data.config import TOKEN, CLIENT_SECRET, OAUTH_URL, REDIRECT_URL
from forms.user import RegisterForm
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
        return render_template('main_page.html', current_user=current_user)
    return render_template('main_page.html', oauth_url=OAUTH_URL, current_user=None)


# @app.route('/user_environment')
# def user_environment():
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).all()
#     return render_template('user_environment.html', user=user)


@app.route('/login')
def login():
    code = request.args['code']
    access_token = client.oauth.get_access_token(code, REDIRECT_URL).access_token
    session['token'] = access_token
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


# @app.route('/register', methods=['GET', 'POST'])
# def reqister():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         if form.password.data != form.password_again.data:
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Пароли не совпадают")
#         db_sess = db_session.create_session()
#         if db_sess.query(User).filter(User.email == form.email.data).first():
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Такой пользователь уже есть")
#         user = User(
#             name=form.name.data,
#             email=form.email.data,
#         )
#         user.set_password(form.password.data)
#         db_sess.add(user)
#         db_sess.commit()
#         return redirect('/login')
#     return render_template('register.html', title='Регистрация', form=form)


@app.route('/add_playlist', methods=['GET', 'POST'])
def add_playlist():
    form = PlayListRegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == 1).first()
        playlist = PlayList(name=form.name.data, command=form.command.data, user_id=user)
        user.playlist.append(playlist)
        db_sess.commit()
        return redirect('/')
    return render_template('add_playlist.html', title='Новый плейлист', form=form)


if __name__ == '__main__':
    main()
