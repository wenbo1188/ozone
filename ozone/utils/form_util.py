from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', 
                validators=[DataRequired(message='username can\'t be empty'), Length(1, 64)])

    password = PasswordField('password',
                validators=[InputRequired(message='password can\'t be empty'), Length(1, 64)])
    
    submit = SubmitField('登录')

class EssayForm(FlaskForm):
    title = StringField('title',
                validators=[InputRequired(message='title can\'t be empty'), Length(1, 100)])
    content = StringField('content',
                validators=[InputRequired(message='content can\'t be empty'), Length(1, 8000)])

class MessageForm(FlaskForm):
    content = StringField('content',
                validators=[InputRequired(message='message can\'t be empty'), Length(1, 1000)])