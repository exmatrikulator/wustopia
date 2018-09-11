#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, DateTime, Integer, Float, BigInteger, String, Boolean, Binary, ForeignKey, UniqueConstraint, Text, Table, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from datetime import datetime
import random

from webapp import db

bcrypt = Bcrypt()


class Achievement(db.Model):
    """Stores Achievements / Tasks"""
    __tablename__ = 'achievement'
    id = Column(Integer(), primary_key=True, nullable=False)
    slug = Column(String(42), unique=True, nullable=False)
    name = Column(String(64))
    description = Column(String(255))
    filter = Column(String(2000))
    dependson = Column(String(42))
    hidden = Column(Boolean(), default=False)
    stars = Column(Integer(), nullable=False)

    def __str__(self):
        return self.name

    def get_id(self, slug):
        try:
            query = db.session.query(Achievement).filter_by(slug=slug)
            instance = query.first()

            if instance:
                return instance.id
            return None
        except Exception as e:
            raise e

class AchievementsCollected(db.Model):
    """Stores collected Achievements"""
    __tablename__ = 'achievementscollected'
    id = Column(Integer(), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])
    achievement_id = Column(Integer, ForeignKey('achievement.id'), nullable=False)
    achievement = db.relationship("Achievement", foreign_keys=[achievement_id])
    reached = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'achievement_id'),)

class Balance(db.Model):
    """Stores the current balance of an user"""
    __tablename__ = 'balance'
    id = Column(Integer(), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    amount = Column(Integer(), nullable=False)

class Built(db.Model):
    """Stores the buildings of the user"""
    __tablename__ = 'built'
    id = Column(Integer(), primary_key=True, nullable=False)
    place_id = Column(Integer, ForeignKey('place.id'), nullable=False)
    place = db.relationship("Place", foreign_keys=[place_id])
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])
    level = Column(Integer(), default=1, nullable=False )
    lastcollect = Column(DateTime, default=datetime.utcnow, nullable=False)
    ready = Column(DateTime, nullable=False)

class BuildCost(db.Model):
    """Stores the time to build a place (level)"""
    __tablename__ = 'buildcost'
    id = Column(Integer(), primary_key=True, nullable=False)
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id])
    level = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)    #time in secounds
    __table_args__ = (UniqueConstraint('placecategory_id', 'level'),)

    def get_id(self, placecategory, level):
        try:
            query = db.session.query(BuildCost).filter_by(placecategory_id=PlaceCategory().get_id(placecategory), level=level)
            instance = query.first()

            if instance:
                return instance.id
            return None
        except Exception as e:
            raise e

class BuildCostResource(db.Model):
    """Stores the prices of resources to build a place (level)"""
    __tablename__ = 'buildcostresource'
    id = Column(Integer(), primary_key=True, nullable=False)
    buildcost_id = Column(Integer, ForeignKey('buildcost.id'), nullable=False)
    buildcost = db.relationship("BuildCost", foreign_keys=[buildcost_id])
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    amount = Column(Integer(), nullable=False)
    __table_args__ = (UniqueConstraint('buildcost_id', 'resource_id'),)

class Place(db.Model):
    """Stores the places (nodes) from OSM"""
    __tablename__ = 'place'
    id = Column(Integer(), primary_key=True, nullable=False)
    osmNodeId = Column(BigInteger(), unique=True, nullable=False)
    lat = Column(Float(), nullable=False)
    lon = Column(Float(), nullable=False)
    name = Column(String(255))
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id])
    lastupdate = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return self.name

class PlaceCategory(db.Model):
    """Stores the category of a place. E.g. Bus Stop, Restaurant"""
    __tablename__ = 'placecategory'
    id = Column(Integer(), primary_key=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(48), unique=True, nullable=False)
    description = Column(Text())
    filter = Column(String(255))
    places = relationship('Place', backref='category')
    icon = Column(String(255), default="home")
    markerColor = Column(String(255), default="blue")
    benefit = db.relationship("PlaceCategoryBenefit", back_populates="placecategory")

    def __str__(self):
        return self.name

    def get_id(self, slug):
        try:
            query = db.session.query(PlaceCategory).filter_by(slug=slug)
            instance = query.first()

            if instance:
                return instance.id
            return None
        except Exception as e:
            raise e

class PlaceCategoryBenefit(db.Model):
    """Stores the information how much you earn"""
    __tablename__ = 'placecategorybenefit'
    id = Column(Integer(), primary_key=True, nullable=False)
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id], back_populates="benefit")
    level = Column(Integer(), nullable=False)
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    amount = Column(Integer(), nullable=False)
    interval = Column(Integer(), nullable=False) # in minutes
    __table_args__ = (UniqueConstraint('placecategory_id', 'level', 'resource_id'),)


class Resource(db.Model):
    """Stores the possible Resourceses witch User can earn/trade"""
    __tablename__ = 'resource'
    id = Column(Integer(), primary_key=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    image = Column(String(255))
    major = Column(Boolean())  #is a major resource to show in status bar?

    def __str__(self):
        return self.name

    def get_id(self, slug):
        try:
            query = db.session.query(Resource).filter_by(slug=slug)
            instance = query.first()

            if instance:
                return instance.id
            return None
        except Exception as e:
            raise e

class User(db.Model):
    """Stores the User information"""
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True, nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    _password = Column(Binary(60), nullable=False)
    email = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return self.username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def get_id(self):
        return str(self.id)

    def is_active():
        return True

    def is_authenticated(self):
        return True

    def is_admin(self):
        return self.id == 1

    def new_user(username=None, password=None, email=None):
        if not username:
            username = "User" + str( random.randint(1, 10000) )
        if not password:
            password = str( random.random() )
        user = User(
            username = username,
            password = password,
            email = email
        )
        db.session.add(user)
        db.session.commit()
        db.session.add(Balance(user_id=user.id, resource_id=Resource().get_id("gold"), amount=100))
        db.session.commit()
        return user
