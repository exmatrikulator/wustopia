#!/usr/bin/python
# -*- coding: utf-8 -*-
import overpy
from webapp import db
from webapp.models import Built, BuildCost, Place, PlaceCategory, PlaceCategoryBenefit
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

api = overpy.Overpass()

def importPlaces(lat1,lon1,lat2,lon2):
    #only if last update is longer than a week ago
    lastupdate = db.session.query(Place.lastupdate).filter(Place.lat.between(lat1,lat2)).filter(Place.lon.between(lon1,lon2)).order_by(desc(Place.lastupdate)).first()
    if lastupdate is not None and lastupdate[0] is not None and (datetime.now() - lastupdate[0]) < timedelta(days = 7):
        return "not necessary"

    categories = db.session.query(PlaceCategory)
    for category in categories:
        #print(category.name)
        try:
            result = api.query("[timeout:5];node("+str(lat1)+","+str(lon1)+","+str(lat2)+","+str(lon2)+")"+str(category.filter)+";out;")
        except overpy.exception.OverpassTooManyRequests:
            #Too many requests
            return
        for node in result.nodes:
            if node.tags.get("name") is None:   #nodes without name can't be shown
                continue
            try:
                db.session.add( Place( osmNodeId=node.id, lon=node.lon, lat = node.lat, placecategory_id=category.id, name=node.tags.get("name") ) )
                db.session.commit()
            except:
                db.session.rollback()
    return "import"

def getPlaces(lat = None ,lon = None):
    js = "wustopia.user.built=["
    ## Defines the allowed distance
    diff=0.001
    nodes = db.session.query(Place).filter( Place.lat.between(lat-diff, lat+diff)).filter( Place.lon.between(lon-diff, lon+diff)).all()
    nodes += db.session.query(Place).join(Built.place).filter(Built.user_id==current_user.id).all()
    for node in nodes:
        building = db.session.query(Built).filter_by(place_id=node.id, user_id=current_user.id).first()
        buildinglevel = int(building.level) if building else 0
        buildingcosts = db.session.query(BuildCost).options(joinedload(BuildCost.resource)).filter_by(placecategory=node.category.id, level=buildinglevel+1).all()
        buildingcost=""
        for cost in buildingcosts:
            buildingcost += str(cost.amount) + " " + str(cost.resource.name) + " "

        benefit = db.session.query(PlaceCategoryBenefit).filter_by(placecategory_id = node.category.id, level=buildinglevel).first()
        collectable = "-1"
        if benefit:
            collectable = timedelta(minutes=benefit.interval) + building.lastcollect - datetime.now()
            collectable = round(collectable.total_seconds() ) if collectable.total_seconds() > 0 else 0

        js += "{"
        js += "id:" + str(node.id) + ",lat:" + str(node.lat) + ",lon:" + str(node.lon) + ",name:\"" + str(node.name) + "\",level:\"" + str(buildinglevel) + "\",category:\"" + str(node.category.name) + "\",categoryid:" + str(node.category.id) + ",costs:\"" + buildingcost + "\",collectable:" + str(collectable) + ""
        js += "},"
    return js + "];"
