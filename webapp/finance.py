#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db
from webapp.models import Balance, Built ,Place, PlaceCategory, PlaceCategoryBenefit
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
import datetime as datetime

def getBalance(userid):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=userid).order_by(Balance.id).all()
    return amounts

def getBalanceofResource(userid, resource):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=userid, resource_id=resource).first()
    return amounts
