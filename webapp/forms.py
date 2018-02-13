from flask_wtf import FlaskForm
from flask_babel import gettext
from wtforms.fields import StringField, PasswordField
from wtforms.validators import Required

class UserCreateForm(FlaskForm):
    username = StringField(gettext("#Username"), validators=[Required()])
    password = PasswordField(gettext("#Password"), validators=[Required()])
    email = StringField(gettext("#EMail"), validators=[Required()])

class UserLoginForm(FlaskForm):
    username = StringField(gettext("#Username"), validators=[Required()])
    password = PasswordField(gettext("#Password"), validators=[Required()])
