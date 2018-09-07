#!/usr/bin/python
# -*- coding: utf-8 -*-
import overpy
from webapp import app, db
from webapp.models import Built, BuildCost, BuildCostResource, Place, PlaceCategory, PlaceCategoryBenefit
from flask_babel import gettext
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

api = overpy.Overpass()

def importPlaces(lat1,lon1,lat2,lon2):
    if(lon2-lon1 > 0.01 or lat2-lat1 > 0.01):
        return gettext("#range to big")
    #only if last update is longer than a week ago
    lastupdate = db.session.query(Place.lastupdate).filter(Place.lat.between(lat1,lat2)).filter(Place.lon.between(lon1,lon2)).order_by(desc(Place.lastupdate)).first()
    if lastupdate is not None and lastupdate[0] is not None and (datetime.now() - lastupdate[0]) < timedelta(days = 7):
        return gettext("#not necessary")

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

            except Exception as e:
                db.session.rollback()
                if app.debug:
                    print(e)
    return "OK"

def getPlaces(lat = None ,lon = None):
    #Defines the allowed distance
    diff=0.005
    output = []
    #TODO: Filter duplicate
    nodes = db.session.query(Place).filter( Place.lat.between(lat-diff, lat+diff)).filter( Place.lon.between(lon-diff, lon+diff)).all()
    nodes += db.session.query(Place).join(Built.place).filter(Built.user_id==current_user.id).all()
    for node in nodes:
        ready = 0
        buildingcost=[]
        collectablein = "-1"

        building = db.session.query(Built).filter(Built.place_id==node.id, Built.user_id==current_user.id).first()
        if building:
            ready = int(building.ready.timestamp())
            if building.ready < datetime.now():
                buildinglevel = int(building.level)
            else:
                buildinglevel = int(building.level) -1
        else:
            buildinglevel = 0
        #buildingcosts = db.session.query(BuildCost).options(joinedload(BuildCost.resource)).filter_by(placecategory=node.category.id, level=buildinglevel+1).all()
        buildingcosts = db.session.query(BuildCostResource).options(joinedload(BuildCostResource.buildcost)).options(joinedload(BuildCostResource.resource)).filter(BuildCost.placecategory_id==node.category.id, BuildCost.level==buildinglevel+1, BuildCostResource.buildcost_id==BuildCost.id).all()
        for cost in buildingcosts:
            item = {}
            item['name'] = gettext("#%s" % cost.resource.name)
            item['amount'] = cost.amount
            item['image'] = cost.resource.image
            buildingcost.append( item )
        buildcost = db.session.query(BuildCost).filter_by(placecategory_id=node.category.id, level=buildinglevel+1,).first()
        if buildcost:
            buildtime = buildcost.time
        else:
            buildtime = None

        benefit = db.session.query(PlaceCategoryBenefit).filter_by(placecategory_id = node.category.id, level=buildinglevel).first()
        if benefit:
            collectablein = timedelta(minutes=benefit.interval) + building.lastcollect - datetime.now()
            collectablein = round(collectablein.total_seconds() ) if collectablein.total_seconds() > 0 else 0

        item = {}
        item['id'] = node.id
        item['lat'] = node.lat
        item['lon'] = node.lon
        item['name'] = node.name
        item['level'] = str(buildinglevel)
        item['category'] = gettext("#%s" % node.category.name)
        item['categoryid'] = node.category.id
        item['costs'] = buildingcost
        item['buildtime'] = buildtime
        item['collectablein'] = collectablein
        item['ready'] = ready

        output.append(item)
    return output
