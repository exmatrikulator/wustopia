#!/usr/bin/python
# -*- coding: utf-8 -*-
import flask_admin as admin
from flask_admin.base import MenuLink
from flask_admin.contrib import sqla
from flask_babel import gettext
from flask_login import current_user

from webapp import db, app
from  webapp.models import *

class WustopiaModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_admin()

class UserAdmin(WustopiaModelView):
    column_searchable_list = ['id','username','email']
    form_columns = column_searchable_list
    column_display_pk = True

class BalanceAdmin(WustopiaModelView):
    column_filters = ['resource','user']

class PlaceAdmin(WustopiaModelView):
    column_filters = ['placecategory']
    column_searchable_list = ['name','osmNodeId']
    column_display_pk = True

class BuiltAdmin(WustopiaModelView):
    column_filters = ['user','place']
    column_display_pk = True

class BuildCostResourceAdmin(WustopiaModelView):
    column_filters = ['buildcost', 'resource']

class PlaceCategoryBenefitAdmin(WustopiaModelView):
    column_filters = ['placecategory', 'resource']


admin = admin.Admin(app, name=gettext("#Wustopia Admin") ,template_mode='bootstrap3')
admin.add_link(MenuLink(name=gettext('#Back to Map'), url='/map'))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(BalanceAdmin(Balance, db.session))
admin.add_view(PlaceAdmin(Place, db.session))
admin.add_view(BuiltAdmin(Built, db.session))
admin.add_view(BuildCostResourceAdmin(BuildCostResource, db.session))
admin.add_view(PlaceCategoryBenefitAdmin(PlaceCategoryBenefit, db.session))
