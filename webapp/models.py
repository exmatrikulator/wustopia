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

## Stores Achievements / Tasks
class Achievement(db.Model):
    __tablename__ = 'achievement'
    ## id of the Achievement record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## a unique of a clean URL
    slug = Column(String(42), unique=True, nullable=False)
    ## a name / title of the achievement
    name = Column(String(64))
    ## a description
    description = Column(String(255))
    ## filter string to reach the achievement
    # @deprecated
    filter = Column(String(2000))
    ## slug of another achievement which must be reach first
    dependson = Column(String(42))
    ## is hidden (surprises) or shown in an list
    hidden = Column(Boolean(), default=False)
    ## how many stars do you earn after reaching this achievement
    stars = Column(Integer(), nullable=False)

    def __str__(self):
        return self.name

    ## retun the id of an achievement
    # @param slug a unique name of the achievement
    def get_id(self, slug):
        try:
            query = db.session.query(Achievement).filter_by(slug=slug)
            instance = query.first()

            if instance:
                return instance.id
            return None
        except Exception as e:
            raise e

## Stores collected Achievements
class AchievementsCollected(db.Model):
    __tablename__ = 'achievementscollected'
    ## id of the AchievementsCollected record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## User ID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ## User object
    user = db.relationship("User", foreign_keys=[user_id])
    ## Achievement ID
    achievement_id = Column(Integer, ForeignKey('achievement.id'), nullable=False)
    ## Achievement object
    achievement = db.relationship("Achievement", foreign_keys=[achievement_id])
    ## Date when achievement was reached
    reached = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'achievement_id'),)

## Stores the current balance of an user
class Balance(db.Model):
    __tablename__ = 'balance'
    ## id of the Balance record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## User ID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ## User object
    user = db.relationship("User", foreign_keys=[user_id])
    ## Resource ID
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    ## Resource object
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    ## current amount of the resource
    amount = Column(Integer(), nullable=False)

## Stores the buildings of the user
class Built(db.Model):
    __tablename__ = 'built'
    ## id of the Built record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## Place ID
    place_id = Column(Integer, ForeignKey('place.id'), nullable=False)
    ## Place object
    place = db.relationship("Place", foreign_keys=[place_id])
    ## User ID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ## User object
    user = db.relationship("User", foreign_keys=[user_id])
    ## level of the built place
    level = Column(Integer(), default=1, nullable=False )
    ## last time the user has collected the benefit
    lastcollect = Column(DateTime, default=datetime.utcnow, nullable=False)
    ## time when place is ready built
    ready = Column(DateTime, nullable=False)

## Stores the time to build a place (level)
class BuildCost(db.Model):
    __tablename__ = 'buildcost'
    ## id of the BuildCost record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## placecategory ID
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    ## PlaceCategory object
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id])
    ## level of the Place
    level = Column(Integer(), nullable=False)
    ## built time of the Place in this level
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

## Stores the prices of resources to build a place (level)
class BuildCostResource(db.Model):
    __tablename__ = 'buildcostresource'
    ## id of the BuildCostResource record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## BuildCost ID
    buildcost_id = Column(Integer, ForeignKey('buildcost.id'), nullable=False)
    ## BuildCost object
    buildcost = db.relationship("BuildCost", foreign_keys=[buildcost_id])
    ## Resource ID
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    ## Resource object
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    ## amount of resource
    amount = Column(Integer(), nullable=False)
    __table_args__ = (UniqueConstraint('buildcost_id', 'resource_id'),)

## Stores the places (nodes) from OSM
class Place(db.Model):
    __tablename__ = 'place'
    ## id of the Place record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## OpenStreetMap Node ID
    osmNodeId = Column(BigInteger(), unique=True, nullable=False)
    ## latitude of the node
    lat = Column(Float(), nullable=False)
    ## longitude of the node
    lon = Column(Float(), nullable=False)
    ## (display) name of the node
    name = Column(String(255))
    ## PlaceCategory ID
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    ## PlaceCategory object
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id])
    ## last time when updated via overpass API
    lastupdate = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return self.name

## Stores the category of a place. E.g. Bus Stop, Restaurant
class PlaceCategory(db.Model):
    __tablename__ = 'placecategory'
    ## id of the PlaceCategory record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## name of the category
    name = Column(String(255), unique=True, nullable=False)
    ## a unique of a clean URL
    slug = Column(String(48), unique=True, nullable=False)
    ## description of the category
    description = Column(Text())
    ## query for the OpenStreetMap Overpass API
    filter = Column(String(255))
    ## Place object
    places = relationship('Place', backref='category')
    ## AwesomeMarkers Icon name
    icon = Column(String(255))
    ## color of teh Icon
    markerColor = Column(String(255))
    ## PlaceCategoryBenefit object
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

## Stores the information how much you earn
class PlaceCategoryBenefit(db.Model):
    __tablename__ = 'placecategorybenefit'
    ## id of the PlaceCategoryBenefit record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## PlaceCategory ID
    placecategory_id = Column(Integer, ForeignKey('placecategory.id'), nullable=False)
    ## PlaceCategory object
    placecategory = db.relationship("PlaceCategory", foreign_keys=[placecategory_id], back_populates="benefit")
    ## level of the benefit
    level = Column(Integer(), nullable=False)
    ## Resource ID
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    ## Resource object
    resource = db.relationship("Resource", foreign_keys=[resource_id])
    ## amount to earn
    amount = Column(Integer(), nullable=False)
    ## interval in minutes when item is collectable
    interval = Column(Integer(), nullable=False)
    __table_args__ = (UniqueConstraint('placecategory_id', 'level', 'resource_id'),)

## Stores the possible Resourceses witch User can earn/trade
class Resource(db.Model):
    __tablename__ = 'resource'
    ## id of the Resource record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## name of the resource
    name = Column(String(255), unique=True, nullable=False)
    ## a unique of a clean URL
    slug = Column(String(50), unique=True, nullable=False)
    ## realtive link to resource image
    image = Column(String(255))
    ## major resource are shown allways on status bar
    major = Column(Boolean())

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

## Stores the user information
class User(db.Model):
    __tablename__ = 'users'
    ## id of the User record
    id = Column(Integer(), primary_key=True, nullable=False)
    ## the user name
    username = Column(String(32), unique=True, nullable=False)
    ## internal field of the passord. use "passord" for get/set
    _password = Column(Binary(60), nullable=False)
    ## email address of the user
    email = Column(String(255))
    ## date when the user was created
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
