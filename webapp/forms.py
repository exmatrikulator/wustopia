from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired

class UserCreateForm(FlaskForm):
    username = StringField(lazy_gettext("#Username"), validators=[DataRequired()])
    password = PasswordField(lazy_gettext("#Password"), validators=[DataRequired()])
    email = StringField(lazy_gettext("#EMail"), validators=[DataRequired()])

class UserLoginForm(FlaskForm):
    username = StringField(lazy_gettext("#Username"), validators=[DataRequired()])
    password = PasswordField(lazy_gettext("#Password"), validators=[DataRequired()])
