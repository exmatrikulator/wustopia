#!/usr/bin/python
# -*- coding: utf-8 -*-
import overpy
from webapp import db
from webapp.models import Place, PlaceCategory

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
    js = ""
    nodes = db.session.query(Place)
    for node in nodes:
        js += "addItem("+str(node.lat)+", "+str(node.lon)+", \""+str(node.name)+"\", \"unset\", \""+str(node.id)+"\", \""+str(node.category.name)+"\");"
    return js
