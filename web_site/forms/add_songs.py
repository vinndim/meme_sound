from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField, StringField
from wtforms.validators import DataRequired


class AddSongForm(FlaskForm):
    url = URLField('Ссылка', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
