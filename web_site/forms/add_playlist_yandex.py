from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField, StringField
from wtforms.validators import DataRequired


class AddPlaylistYandex(FlaskForm):
    url_yandex = URLField('Ссылка', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
