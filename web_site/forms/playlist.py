from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PlayListRegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    command = StringField('Команда', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
