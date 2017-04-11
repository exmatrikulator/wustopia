#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db
from webapp.models import Balance
from sqlalchemy.orm import joinedload

def getBalance(userid):
    amounts = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=userid).all()
    return amounts
