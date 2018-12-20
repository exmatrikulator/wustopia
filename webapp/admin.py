#!/usr/bin/python
# -*- coding: utf-8 -*-
import flask
import flask_admin as admin
from flask_admin.base import MenuLink
from flask_admin.contrib import sqla
from flask_babel import lazy_gettext
from flask_login import current_user
import rq_dashboard

from webapp import db, app
from  webapp.models import *

## Template View for Wustopia
class WustopiaModelView(sqla.ModelView):
    ## defines the number of rows per page
    page_size = 100
    ## check for admin rights
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin()

## Amdin View for Users
class UserAdmin(WustopiaModelView):
    ## defines which fields should be search able with the search field
    column_searchable_list = ['id','username','email']
    ## defines the fields which are shown at the edit dialog
    form_columns = column_searchable_list
    ## show primary key
    column_display_pk = True

## Amdin View for Balance
class BalanceAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['resource','user']

## Amdin View for Place
class PlaceAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['placecategory']
    ## defines which fields should be search able with the search field
    column_searchable_list = ['name','osmNodeId']
    ## show primary key
    column_display_pk = True

## Amdin View for Built
class BuiltAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['user','place']
    ## show primary key
    column_display_pk = True

## Amdin View for BuildCostResource
class BuildCostResourceAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['buildcost', 'resource']

## Amdin View for PlaceCategoryBenefit
class PlaceCategoryBenefitAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['placecategory', 'resource']

## Amdin View for AchievementsCollected
class AchievementsCollectedAdmin(WustopiaModelView):
    ## defines which filter can be added to the view
    column_filters = ['achievement', 'user']
    ## show primary key
    column_display_pk = True

## Amdin View for PlaceCategory
class PlaceCategoryAdmin(WustopiaModelView):
    ## formatter for icons
    # @param view
    # @param context
    # @param model model of an icon
    # @param name
    # @return HTML to render the icon
    def icon_formatter(view, context, model, name):
        return flask.Markup('<div class="awesome-marker-icon- awesome-marker awesome-marker-icon-{}" style="position:relative;"><i class="fa fa-{}  icon-white"></i></div>'.format(model.markerColor, model.icon))
    ## defines the fields which are shown at the edit dialog
    form_columns = ["name","description","filter","icon","markerColor"]
    ## show primary key
    column_display_pk = True
    ## override the formatter for columns
    column_formatters = { 'id': icon_formatter }
    ## template for the list/grid
    list_template = "admin/placecategory.html"

admin = admin.Admin(app, name=lazy_gettext("#Wustopia Admin") ,template_mode='bootstrap3')
admin.add_link(MenuLink(name=lazy_gettext('#RQ'), url='/admin/rq'))
admin.add_link(MenuLink(name=lazy_gettext('#Back to Map'), url='/map'))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(BalanceAdmin(Balance, db.session))
admin.add_view(PlaceAdmin(Place, db.session))
admin.add_view(BuiltAdmin(Built, db.session))
admin.add_view(PlaceCategoryAdmin(PlaceCategory, db.session))
admin.add_view(BuildCostResourceAdmin(BuildCostResource, db.session))
admin.add_view(PlaceCategoryBenefitAdmin(PlaceCategoryBenefit, db.session))
admin.add_view(WustopiaModelView(Achievement, db.session))
admin.add_view(AchievementsCollectedAdmin(AchievementsCollected, db.session))

#rq (Redis Queue)
@rq_dashboard.blueprint.before_request
def is_accessible():
    if not current_user.is_authenticated:
        return "",403
    if not current_user.is_admin():
        return "",403
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/admin/rq")
