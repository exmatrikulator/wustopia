#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@db/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.from_pyfile('../config/config.py')

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "user_login"


babel = Babel(app)

@babel.localeselector
def locale_select():
    return request.accept_languages.best_match(['de', 'en'])



from  webapp.models import User
#import webapp.models
import webapp.views

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id==user_id).first()
