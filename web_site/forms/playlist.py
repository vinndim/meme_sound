from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class PlayListRegisterForm(FlaskForm):
    name = EmailField('Имя', validators=[DataRequired()])
    command = PasswordField('Команда', validators=[DataRequired()])
    submit = SubmitField('Сохранить')