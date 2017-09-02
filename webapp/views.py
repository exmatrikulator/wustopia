#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, request, Response, redirect
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload

from webapp import app
from webapp.models import *
from webapp.places import getPlaces, importPlaces
from webapp.forms import *
from webapp.finance import *

@app.route("/")
def index():
    return render_template('index.html', UserLoginForm=UserLoginForm(), UserCreateForm=UserCreateForm())


@app.route("/map")
@login_required
def map():
    return render_template('map.html')

@app.route("/resources")
def resources():
    html = ""
    html_visible = ""
    html_hidden = ""
    resources = getBalance(current_user.id)
    for resource in resources:
        if resource.resource and resource.resource.major:
            html_visible += '<div class="resource" title="' + str(resource.resource.name) + '"> <img src="' + str(resource.resource.image) + '" class="resource"> ' + str(resource.amount) + ' </div>';
        else:
            html_hidden += '<div class="resource_hidden" title="' + str(resource.resource.name) + '"> <img src="' + str(resource.resource.image) + '" class="resource"> ' + str(resource.amount) + ' </div>';
    html = "<div id=\"resourcebar\">" + html_visible
    html += "<div id=\"resourcebar_hidden\">" + html_hidden + "</div></div>"
    return html

@app.route("/build")
def build():
    #TODO:Do some checks!
    place = db.session.query(Place).options(joinedload(Place.placecategory)).filter_by(id = request.args.get('place')).first()
    building = db.session.query(Built).filter_by(place_id = request.args.get('place'), user_id = current_user.id).first()
    buildinglevel = building.level+1 if building else 1
    buildcost = db.session.query(BuildCost).filter_by(placecategory = place.placecategory.id, level=buildinglevel).all()

    for costs in buildcost:
        current_balance = getBalanceofResource(current_user.id, costs.resource.id)
        if current_balance.amount >= costs.amount:
            current_balance.amount -= costs.amount
            db.session.add(current_balance)
        else:
            return str(getBalanceofResource(current_user.id, costs.resource.id).amount) + " >= " + str(costs.amount)

    if building:
        building.level = building.level+1
        building.lastcollect = datetime.datetime.now()
    else:
        db.session.add(Built(place_id = request.args.get('place'), user_id = current_user.id, lastcollect = datetime.datetime.now()))
    try:
        db.session.commit()
        return "success"
    except:
        db.session.rollback()
        return "unkown Error"

@app.route("/earn")
def earn():
    something_changed=False
    building = db.session.query(Built).options(joinedload(Built.place)).filter_by(place_id = request.args.get('place'), user_id = current_user.id).first()
    buildingbenefit = db.session.query(PlaceCategoryBenefit).filter_by(placecategory_id = building.place.placecategory.id, level=building.level).all()
    for benefit in buildingbenefit:
        if datetime.timedelta(minutes=benefit.interval) <= datetime.datetime.now() - building.lastcollect:
            current_balance = getBalanceofResource(current_user.id, benefit.resource.id)
            current_balance.amount += benefit.amount
            building.lastcollect = datetime.datetime.now()
            db.session.add(current_balance)
            db.session.add(building)
            something_changed=True
    if something_changed:
        try:
            db.session.commit()
            return "success"
        except:
            db.session.rollback()
            return "unkown Error"
    return ""

@app.route("/marker")
def marker():
    categories = db.session.query(PlaceCategory)
    return render_template("marker.js", markers = categories)

@app.route("/mobile_places/<float:lat>,<float:lon>")
def mobile_places(lat,lon):
    response = Response( getPlaces(lat, lon ) )
    response.headers.add('Content-Type', "application/javascript")
    return response



@app.route("/places")
def places():
    response = Response( getPlaces() )
    response.headers.add('Content-Type', "application/javascript")
    return response

is_update_places = False
@app.route("/update_places/<float:lat1>,<float:lon1>,<float:lat2>,<float:lon2>")
def update_places(lat1,lon1,lat2,lon2):
    return importPlaces(lat1,lon1,lat2,lon2)

    global is_update_places
    if is_update_places:
        return "already running"
    is_update_places = True

    if(lon2-lon1 > 0.01 or lat2-lat1 > 0.01):
        is_update_places = False
        return "range to big"

    importPlaces(lon1,lat1,lon2,lat2)
    is_update_places = False
    return "OK"

@app.route("/is_update_places")
def is_update_places2():
    global is_update_places
    return str(is_update_places)


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
        return render_template("error.html", error = form.errors)
    except Exception as e:
        return render_template("error.html", error=e)

@app.route('/user/login', methods=['POST','GET'])
def user_login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.is_correct_password(form.password.data):
            return redirect('/')
        login_user(user)
        return redirect('/map')
    return redirect('/')

@app.route('/user/logout')
def user_logout():
    logout_user()
    return redirect('/')
