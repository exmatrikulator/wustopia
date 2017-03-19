#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, Float, BigInteger, String, Boolean, Binary, ForeignKey
from sqlalchemy.orm import relationship

from webapp import db

bcrypt = Bcrypt()

class Place(db.Model):
    __tablename__ = 'place'
    id = Column(Integer(), primary_key=True)
    osmNodeId = Column(BigInteger(), unique=True)
    lat = Column(Float())
    lon = Column(Float())
    name = Column(String(255))
    placecategory = Column(Integer, ForeignKey('placecategory.id'))

class PlaceCategory(db.Model):
    __tablename__ = 'placecategory'
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), unique=True)
    filter = Column(String(255))
    places = relationship('Place', backref='category')


class PlaceCategoryBenefit(db.Model):
    __tablename__ = 'placecategorybenefit'
    id = Column(Integer(), primary_key=True)
    placecategory = Column(Integer, ForeignKey('placecategory.id'))

class Resource(db.Model):
    __tablename__ = 'resource'
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), unique=True)
    image = Column(String(255))
    major = Column(Boolean())  #is a major resource to show in status bar?


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    username = Column(String(32), unique=True)
    _password = Column(Binary(60), nullable=False)
    email = Column(String(255))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def is_active():
        return True
