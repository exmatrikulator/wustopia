#!/usr/bin/python
# -*- coding: utf-8 -*-
import overpy
from webapp import db
from webapp.models import Built, BuildCost, Place, PlaceCategory
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
    js = "var ckeckItem = function () {"
    if lat and lon:
        diff=0.005
        nodes = db.session.query(Place).filter( Place.lat.between(lat-diff, lat+diff)).filter( Place.lon.between(lon-diff, lon+diff))
    else:
        nodes = db.session.query(Place)
    for node in nodes:
        building = db.session.query(Built).filter_by(place_id=node.id, user_id=current_user.id).first()
        buildinglevel = int(building.level) if building else 0
        buildingcosts = db.session.query(BuildCost).options(joinedload(BuildCost.resource)).filter_by(placecategory=node.category.id, level=buildinglevel+1).all()
        buildingcost=""
        for cost in buildingcosts:
            buildingcost += str(cost.amount) + " " + str(cost.resource.name) + " "
        js += "addItem("+str(node.lat)+", "+str(node.lon)+", \""+str(node.name)+"\", \""+str(buildinglevel)+"\", \""+str(node.id)+"\", \""+str(node.category.name)+"\", \""+str(node.category.id)+"\",\""+buildingcost+"\");"
    return js + "}"
