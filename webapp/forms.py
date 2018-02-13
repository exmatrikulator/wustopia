from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, PasswordField
from wtforms.validators import Required

class UserCreateForm(FlaskForm):
    username = StringField(lazy_gettext("#Username"), validators=[Required()])
    password = PasswordField(lazy_gettext("#Password"), validators=[Required()])
    email = StringField(lazy_gettext("#EMail"), validators=[Required()])

class UserLoginForm(FlaskForm):
    username = StringField(lazy_gettext("#Username"), validators=[Required()])
    password = PasswordField(lazy_gettext("#Password"), validators=[Required()])
