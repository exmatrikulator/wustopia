#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, request, Response, redirect, abort
from flask_babel import gettext
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta

import json

from webapp import app
from webapp.models import *
from webapp.places import getPlaces, importPlaces
from webapp.forms import *
from webapp.finance import *

def wustopia_render_template(template, **kwargs):
    if not 'UserLoginForm' in kwargs:
        kwargs['UserLoginForm']=UserLoginForm()
    if not 'UserCreateForm' in kwargs:
        kwargs['UserCreateForm']=UserCreateForm()
    return render_template(template, **kwargs)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect('/map')
    return wustopia_render_template('index.html')


@app.route("/map")
@login_required
def map():
    return wustopia_render_template('map.html')

@app.route("/ranking")
def ranking():
    return wustopia_render_template('ranking.html', PlaceCategory = db.session.query(PlaceCategory).all())


@app.route("/api/resources")
@login_required
def api_resources():
    output = []
    resources = getBalance(current_user.id)
    for resource in resources:
        item = {}
        item['id'] = resource.resource.id
        item['name'] = gettext("#%s" % resource.resource.name)
        item['image'] = resource.resource.image
        item['major'] = resource.resource.major
        item['amount'] = resource.amount
        output.append(item)

    response = Response( json.dumps(output) )
    response.headers.add('Content-Type', "application/json")
    return response

@app.route("/build")
def build():
    #TODO:Do some checks!
    place = db.session.query(Place).options(joinedload(Place.placecategory)).filter_by(id = request.args.get('place')).first()
    building = db.session.query(Built).filter_by(place_id = request.args.get('place'), user_id = current_user.id).first()
    buildinglevel = building.level+1 if building else 1
    buildcost = db.session.query(BuildCostResource).options(joinedload(BuildCostResource.buildcost)).filter(BuildCost.placecategory_id == place.placecategory.id, BuildCost.level==buildinglevel, BuildCostResource.buildcost_id==BuildCost.id).all()

    #if there aren't buildcost defined, return
    if not buildcost:
        abort(404)

    for costs in buildcost:
        current_balance = getBalanceofResource(current_user.id, costs.resource.id)
        if current_balance.amount >= costs.amount:
            current_balance.amount -= costs.amount
            db.session.add(current_balance)
        else:
            #return str(getBalanceofResource(current_user.id, costs.resource.id).amount) + " >= " + str(costs.amount)
            return gettext('#not enough: %(a)s >= %(b)s', a=getBalanceofResource(current_user.id, costs.resource.id).amount, b=costs.amount ), 500

    buildtime = db.session.query(BuildCost).filter(BuildCost.placecategory_id == place.placecategory.id, BuildCost.level==buildinglevel).first().time
    ready = datetime.now() + timedelta(seconds = buildtime)
    if building:
        building.level = building.level+1
        building.ready = ready
        building.lastcollect = datetime.now()
    else:
        db.session.add(Built(place_id = request.args.get('place'), user_id = current_user.id, lastcollect = datetime.now(), ready=ready))
    try:
        db.session.commit()
        return gettext('#success')
    except Exception as e:
        db.session.rollback()
        if app.debug:
            print(e)
        return gettext('#unkown Error: %(e)s', e=e), 500

@app.route("/earn")
def earn():
    something_changed=False
    building = db.session.query(Built).options(joinedload(Built.place)).filter_by(place_id = request.args.get('place'), user_id = current_user.id).first()
    buildingbenefit = db.session.query(PlaceCategoryBenefit).filter_by(placecategory_id = building.place.placecategory.id, level=building.level).all()
    for benefit in buildingbenefit:
        if timedelta(minutes=benefit.interval) <= datetime.now() - building.lastcollect:
            current_balance = db.session.query(Balance).options(joinedload(Balance.resource)).filter_by(user=current_user.id, resource_id=benefit.resource.id).first()
            current_balance.amount = Balance.amount + benefit.amount
            building.lastcollect = datetime.now()
            db.session.add(current_balance)
            db.session.add(building)
            something_changed=True
    if something_changed:
        try:
            db.session.commit()
            return gettext('#success')
        except Exception as e:
            db.session.rollback()
            if app.debug:
                print(e)
            return gettext('#unkown Error: %(e)s', e=e), 500
    return ""

@app.route("/api/markerIcon")
def markerIcon():
    output = []
    categories = db.session.query(PlaceCategory)
    for marker in categories:
        item = {}
        item['id'] = marker.id
        item['name'] = gettext("#%s" % marker.name)
        item['icon'] = marker.icon
        item['markerColor'] = marker.markerColor
        item['prefix'] = 'fa'
        output.append(item)

    response = Response( json.dumps( output ) )
    response.headers.add('Content-Type', "application/json")
    return response

@app.route("/api/places")
def api_places():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    response = Response( json.dumps(getPlaces(lat, lon ) ) )
    response.headers.add('Content-Type', "application/json")
    return response

@app.route("/api/version")
def api_version():
    with open("version.txt") as f:
        content = f.read()
    response = Response( content )
    response.headers.add('Content-Type', "application/json")
    return response

is_update_places = False
@app.route("/update_places/<float:lat1>,<float:lon1>,<float:lat2>,<float:lon2>")
def update_places(lat1,lon1,lat2,lon2):
    return importPlaces(lat1,lon1,lat2,lon2)

    global is_update_places
    if is_update_places:
        return gettext("#already running")
    is_update_places = True

    if(lon2-lon1 > 0.01 or lat2-lat1 > 0.01):
        is_update_places = False
        return gettext("#range to big")

    importPlaces(lon1,lat1,lon2,lat2)
    is_update_places = False
    return gettext("#OK")

@app.route("/is_update_places")
def is_update_places2():
    global is_update_places
    return str(is_update_places)


@app.route("/help/building/<slug>")
def help_building(slug):
    costs = db.session.query(BuildCost,BuildCostResource, Resource) \
        .join(BuildCostResource) \
        .join(Resource) \
        .filter(BuildCost.placecategory_id == PlaceCategory().get_id(slug)) \
        .order_by(db.asc('level')) \
        .all()

    benefit = db.session.query(PlaceCategoryBenefit, Resource) \
        .join(Resource) \
        .filter(PlaceCategoryBenefit.placecategory_id == PlaceCategory().get_id(slug)) \
        .order_by(db.asc('level')) \
        .all()

    placecategory = db.session.query(PlaceCategory) \
        .filter(PlaceCategory.name == slug) \
        .first()

    if not placecategory:
        abort(404)
    return wustopia_render_template('help_building.html', costs=costs, benefit=benefit, placecategory=placecategory, slug=slug)

@app.route("/ranking/building/<slug>")
def ranking_building(slug):
    ranking = db.session.query(func.count(Built.id).label('count'), User) \
        .join(User) \
        .join(Place) \
        .filter(Place.placecategory_id == PlaceCategory().get_id(slug)) \
        .group_by(User.id) \
        .order_by(db.desc('count')) \
        .limit(50) \
        .all()

    #if there aren't any rankings, return
    if not ranking:
        abort(404)
    return wustopia_render_template('ranking_building.html', ranking=ranking, slug=slug)


@app.route('/user/create', methods=['POST'])
def user_create():
    try:
        form = UserCreateForm()
        if form.validate_on_submit():
            user = User(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.add(user)
            db.session.flush()

            db.session.add(Balance(user=user.id, resource_id=Resource().get_id("Gold"), amount=100))
            db.session.add(Balance(user=user.id, resource_id=Resource().get_id("Nahrung"), amount=100))
            db.session.add(Balance(user=user.id, resource_id=Resource().get_id("Baumaterial"), amount=100))
            db.session.add(Balance(user=user.id, resource_id=Resource().get_id("Kultur"), amount=100))
            db.session.commit()
            #subject = "Confirm your email"
            #token = ts.dumps(form.email.data, salt='email-confirm-key')
            #confirm_url = url_for(
            #    'user_confirm',
            #    token=token,
            #    _external=True)
            #html = render_template(
            #    'email/confirm.html',
            #    confirm_url=confirm_url)
            # We'll assume that send_email has been defined in myapp/util.py
            #return html
            login_user(user)
            return redirect('/map')
        return wustopia_render_template("error.html", error = form.errors)
    except Exception as e:
        return wustopia_render_template("error.html", error=e)

@app.route('/user/login', methods=['POST','GET'])
def user_login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.is_correct_password(form.password.data):
            return wustopia_render_template("error.html", error=gettext("#wrong User / Password"))
        login_user(user)
        return redirect('/map')
    return wustopia_render_template("error.html",error=gettext("#Did you fill all fields?"))

@app.route('/user/logout')
def user_logout():
    logout_user()
    return redirect('/')
