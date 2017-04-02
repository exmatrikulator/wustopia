#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp import db
from webapp.models import Balance

def getBalance(userid):
    amounts = db.session.query(Balance).filter_by(user=userid).all()
    return amounts
