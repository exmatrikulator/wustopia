#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db
from flask_babel import gettext
from webapp.models import *
from sqlalchemy.orm import joinedload


def newAchievement(name,description,reached,amount):
    achievement = {}
    achievement['name']=name
    achievement['description']=description
    achievement['reached']=reached
    achievement['amount']=amount

    return achievement


def getAchievements(userid):
    achievements = []

    #busstop
    busstops = db.session.query(Place).join(Built.place).filter(Built.user_id==userid).filter(Place.placecategory_id==PlaceCategory().get_id("Bushaltestelle")).count()
    achievements.append(newAchievement(gettext("#10 Bushaltestellen"),"",busstops > 10,busstops))
    if busstops>10: achievements.append(newAchievement(gettext("#100 Bushaltestellen"),"",busstops > 100,busstops))
    if busstops>100: achievements.append(newAchievement(gettext("#1000 Bushaltestellen"),"",busstops > 1000,busstops))

    busstops = db.session.query(Place).join(Built.place).filter(Built.user_id==userid).filter(Built.level>=3).filter(Place.placecategory_id==PlaceCategory().get_id("Bushaltestelle")).count()
    achievements.append(newAchievement(gettext("#10 Bushaltestellen Level 3"),"",busstops > 10,busstops))
    if busstops>10: achievements.append(newAchievement(gettext("#1000 Bushaltestellen Level 3"),"",busstops > 1000,busstops))
    if busstops>100: achievements.append(newAchievement(gettext("#100 Bushaltestellen Level 3"),"",busstops > 100,busstops))


    #restaurant
    restaurant = db.session.query(Place).join(Built.place).filter(Built.user_id==userid).filter(Place.placecategory_id==PlaceCategory().get_id("Restaurant")).count()
    achievements.append(newAchievement(gettext("#10 Restaurants"),"",restaurant > 10,restaurant))
    if restaurant>10: achievements.append(newAchievement(gettext("#100 Restaurants"),"",restaurant > 100,restaurant))
    if restaurant>100: achievements.append(newAchievement(gettext("#1000 Restaurants"),"",restaurant > 1000,restaurant))


    return achievements
