#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db, session_add
from flask_babel import gettext
from webapp.models import *
from sqlalchemy.orm import joinedload


def check_achievements(userid):

    categories = db.session.query(PlaceCategory).all()
    amounts = [1,2,5,10,20,50,100,200,500,1000]
    for category in categories:
        count = db.session.query(Place).join(Built.place).filter(Built.user_id==userid).filter(Place.placecategory_id==category.id).count()
        for amount in amounts:
            if count >= amount:
                session_add(AchievementsCollected(achievement_id=Achievement().get_id(str(amount)+category.slug),user_id=userid))
    return "OK"
