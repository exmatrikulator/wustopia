#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import joinedload
from webapp import db
from webapp.models import Balance

def getBalance(userid):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user_id=userid).order_by(Balance.id).all()
    return amounts

def getBalanceofResource(userid, resource):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user_id=userid, resource_id=resource).first()
    return amounts
