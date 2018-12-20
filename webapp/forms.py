from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired

## User registration form
class UserCreateForm(FlaskForm):
    ## username to register
    username = StringField(lazy_gettext("#Username"), validators=[DataRequired()])
    ## password of the new user
    password = PasswordField(lazy_gettext("#Password"), validators=[DataRequired()])
    ## email address to contact the user (email validation, password reset, etc)
    email = StringField(lazy_gettext("#EMail"), validators=[DataRequired()])

## User login form
class UserLoginForm(FlaskForm):
    ## username of the user
    username = StringField(lazy_gettext("#Username"), validators=[DataRequired()])
    ## password of the users
    password = PasswordField(lazy_gettext("#Password"), validators=[DataRequired()])
