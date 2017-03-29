#!/usr/bin/python
# -*- coding: utf-8 -*-
import overpy
from webapp import db
from webapp.models import Built, Place, PlaceCategory
from flask_login import current_user

api = overpy.Overpass()

def importPlaces(lon1,lat1,lon2,lat2):
    categories = db.session.query(PlaceCategory)
    for category in categories:
        print(category.name)
        while True:     #try as long you got an answer
            try:
                result = api.query("node("+str(lon1)+","+str(lat1)+","+str(lon2)+","+str(lat2)+")"+str(category.filter)+";out;")
            except overpy.exception.OverpassTooManyRequests:
                print("Too many requests")
                import time
                sleep(60)
                continue
            break
        for node in result.nodes:
            if node.tags.get("name") is None:   #nodes without name can't be shown
                continue
            try:
                db.session.add( Place( osmNodeId=node.id, lon=node.lon, lat = node.lat, placecategory=category.id, name=node.tags.get("name") ) )
                db.session.commit()
            except:
                db.session.rollback()

def getPlaces(lon1,lat1,lon2,lat2,filter):
    js = "var ckeckItem = function () {"
    nodes = db.session.query(Place)
    for node in nodes:
        building = db.session.query(Built).filter_by(place=node.id, user=current_user.id).first()
        if building:
            js += "addItem("+str(node.lat)+", "+str(node.lon)+", \""+str(node.name)+"\", \""+str(building.level)+"\", \""+str(node.id)+"\", \""+str(node.category.name)+"\");"
        else:
            js += "addItem("+str(node.lat)+", "+str(node.lon)+", \""+str(node.name)+"\", \"0\", \""+str(node.id)+"\", \""+str(node.category.name)+"\");"
    return js + "}"
