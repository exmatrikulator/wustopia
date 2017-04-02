#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, request, Response, redirect
from flask_login import login_user, logout_user, login_required, current_user

from webapp import app
from webapp.models import *
from webapp.places import getPlaces
from webapp.forms import *
from webapp.finance import getBalance

@app.route("/")
def index():
    return render_template('index.html', UserLoginForm=UserLoginForm(), UserCreateForm=UserCreateForm())


@app.route("/balance")
@login_required
def balance():
    output = ""
    for amount in getBalance(current_user.id):
        output += amount.amount
    return output

@app.route("/map")
@login_required
def map():
    return render_template('map.html')

@app.route("/resources")
def resources():
    html = ""
    html_visible = ""
    html_hidden = ""
    resources = db.session.query(Resource).order_by(Resource.major)
    for resource in resources:
        if resource.major:
            html_visible += '<div class="resource" title="' + str(resource.name) + '"> <img src="' + str(resource.image) + '" class="resource"> 100 </div>';
        else:
            html_hidden += '<div class="resource_hidden" title="' + str(resource.name) + '"> <img src="' + str(resource.image) + '" class="resource"> 100 </div>';
    html = "<div id=\"resourcebar\">" + html_visible
    html += "<div id=\"resourcebar_hidden\">" + html_hidden + "</div></div>"
    return html

@app.route("/build")
def build():
    #TODO:Do some checks!
    building = db.session.query(Built).filter_by(place = request.args.get('place'), user = current_user.id).first()
    if building:
        building.level = building.level+1
    else:
        db.session.add(Built(place = request.args.get('place'), user = current_user.id))
    try:
        db.session.commit()
        return "success"
    except:
        db.session.rollback()
        return "unkown Error"


@app.route("/places")
def places():
    response = Response( getPlaces(51.2579, 7.1537, 51.2618, 7.1420, "") )
    response.headers.add('Content-Type', "application/javascript")
    return response


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
    except:
        return render_template("error.html")

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
