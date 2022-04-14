from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, URL


class PlayListRegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    img = StringField('Изображение')
    submit = SubmitField('Сохранить')
