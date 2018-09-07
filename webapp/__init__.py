#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
import rq_dashboard


app = Flask(__name__)
app.config.from_object(rq_dashboard.default_settings)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@db/postgres?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['REDIS_URI'] = "redis://redis:6379"
app.config['REDIS_HOST'] = "redis"
try:
    app.config.from_pyfile('../config/config.py')
except Exception:
    pass

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "index"

babel = Babel(app)

@babel.localeselector
def locale_select():
    lang = request.accept_languages.best_match(['de', 'en'])
    if lang:
        return lang
    else:
        return "en"
#make it callable from jinja2
app.jinja_env.globals.update(locale_select=locale_select)


from  webapp.models import User
#import webapp.models
import webapp.views
import webapp.admin

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id==user_id).first()
