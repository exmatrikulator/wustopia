#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, request, Response

from webapp import app
from webapp.models import *
from webapp.places import getPlaces


@app.route("/")
def index():
    return render_template('index.html')

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
    return ""


@app.route("/places")
def places():
    response = Response( getPlaces(51.2579, 7.1537, 51.2618, 7.1420, "") )
    response.headers.add('Content-Type', "application/javascript")
    return response
