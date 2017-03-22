from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import Required

class UserCreateForm(FlaskForm):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
    email = StringField('EMail', validators=[Required()])

class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
