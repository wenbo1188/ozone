from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', 
                validators=[DataRequired(message='username can\'t be empty'), Length(1, 64)])

    password = PasswordField('password',
                validators=[InputRequired(message='password can\'t be empty'), Length(1, 64)])
    
    submit = SubmitField('登录')