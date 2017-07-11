#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db
from webapp.models import Balance, Built ,Place, PlaceCategory, PlaceCategoryBenefit
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
import datetime as datetime

def getBalance(userid):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=userid).all()
    return amounts

def getBalanceofResource(userid, resource):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=userid, resource_id=resource).first()
    return amounts

#calculate the current balance. should be run befor every build
def newBalance(userid):
    for resource in getBalance(userid):
        delta = datetime.datetime.now() - resource.lastupdate
        deltadays = delta.total_seconds() / 60 / 60 / 24
        diff = 0

        buildings = db.session.query(Built, PlaceCategoryBenefit) \
        .filter_by(user_id=userid) \
        .join(Place, Built.place_id == Place.id) \
        .join(PlaceCategory, Place.placecategory_id == PlaceCategory.id) \
        .join(PlaceCategoryBenefit, and_(PlaceCategoryBenefit.placecategory_id == PlaceCategory.id,  PlaceCategoryBenefit.level == Built.level, PlaceCategoryBenefit.resource_id == resource.id ) ) \
        .all()
        for building in buildings:
            diff += deltadays * building.PlaceCategoryBenefit.amount
        #TODO avoid rounding error
        #leftover = diff % 1
        #resource.amount += diff - diff % 1
        resource.lastupdate = datetime.datetime.now()
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "unkown Error"
    return ""
