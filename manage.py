#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from webapp import app, db
from webapp.models import *

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

def session_add(model):
    try:
        db.session.add(model)
        db.session.commit()
    except:
        db.session.rollback()

@manager.command
def imoprtInitData():
    "Inititalise the database"
    #transport
    session_add( PlaceCategory( filter="[highway=bus_stop]", name="Bushaltestelle", icon="bus", markerColor="darkgreen" ) )
    session_add( PlaceCategory( filter="[railway=station]", name="Bahnhof", icon="train", markerColor="darkgreen" ) )
    session_add( PlaceCategory( filter="[highway=steps]", name="Treppe", icon="signal", markerColor="gray") )
    #shops
    session_add( PlaceCategory( filter="[shop=bakery]", name="Bäcker", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[shop=butcher]", name="Metzger", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[shop=kiosk]", name="Kiosk", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[shop=doityourself]", name="Baumarkt", markerColor="purple" ) )
    #amenity
    session_add( PlaceCategory( filter="[amenity=restaurant]", name="Restaurant", icon="cutlery", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[amenity=pub]", name="Kneipe", icon="coffee", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[amenity=post_office]", name="Post", icon="envelope", markerColor="purple" ) )
    session_add( PlaceCategory( filter="[amenity=fast_food]", name="Fast Food", icon="cutlery", markerColor="beige" ) )
    session_add( PlaceCategory( filter="[amenity=ice_cream]", name="Eisdiele", markerColor="orange" ) )
    session_add( PlaceCategory( filter="[amenity=theatre]", name="Theater", markerColor="red" ) )
    session_add( PlaceCategory( filter="[amenity=place_of_worship]", name="Religion", markerColor="cadetblue" ) )
    #leisure
    session_add( PlaceCategory( filter="[leisure=hackerspace]", name="Hackerspace", icon="gamepad", markerColor="white" ) )


    session_add( Resource( name="Gold", major=True, image="http://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Gold_coin_icon.png/32px-Gold_coin_icon.png" ) )
    session_add( Resource( name="Nahrung", major=True, image="http://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Food-Jelly.svg/48px-Food-Jelly.svg.png" ) )
    session_add( Resource( name="Baumaterial",major=True, image="http://upload.wikimedia.org/wikipedia/commons/6/68/Nuvola_apps_package_development.png" ) )
    session_add( Resource( name="Kultur", image="http://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Crystal_Clear_app_krita.png/64px-Crystal_Clear_app_krita.png" ) )
    session_add( Resource( name="Gebäude", image="http://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Go-home.svg/50px-Go-home.svg.png" ) )

    session_add(BuildCost(placecategory=PlaceCategory().get_id("Bushaltestelle"), resource_id=Resource().get_id("Gold"), level=1, amount=10))
    session_add(BuildCost(placecategory=PlaceCategory().get_id("Bushaltestelle"), resource_id=Resource().get_id("Gold"), level=2, amount=14))
    session_add(BuildCost(placecategory=PlaceCategory().get_id("Bushaltestelle"), resource_id=Resource().get_id("Gold"), level=3, amount=19))
    session_add(BuildCost(placecategory=PlaceCategory().get_id("Bushaltestelle"), resource_id=Resource().get_id("Baumaterial"), level=3, amount=10))

    print("done")

@manager.command
def bcryptbenchmark():
    "Test number of rounds"
    # Chance the number of rounds (second argument) until it takes between
    # 0.25 and 0.5 seconds to run.
    from flask.ext.bcrypt import generate_password_hash
    import time
    duration = 0
    i=4
    while duration < 0.25:
        start = time.time()
        generate_password_hash('password1', i)
        end = time.time()
        duration = end - start
        i += 1
    print( "(" + str(duration) + " secounds)")
    print( "please copy the next line into config.py")
    print( "")
    print( "BCRYPT_LOG_ROUNDS=" + str(i))

if __name__ == "__main__":
    app.debug = True
    manager.run()
