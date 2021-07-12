from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, InputRequired
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField

class SignUpForm(FlaskForm):
    """Form for Creating a new User"""

    username = StringField('Username', validators=[InputRequired()])
    email = EmailField('E-mail', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6), EqualTo('confirm')])
    confirm = PasswordField('Repeat Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class JokeForm(FlaskForm):
    """Joke Form"""

    setup = StringField('Setup/Title', validators=[DataRequired()])
    body = StringField('Body', widget=TextArea(), validators=[DataRequired()])