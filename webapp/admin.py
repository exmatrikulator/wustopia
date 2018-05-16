#!/usr/bin/python
# -*- coding: utf-8 -*-
import flask_admin as admin
from flask_admin.contrib import sqla
from flask_babel import gettext
from flask_login import current_user

from webapp import db, app
from  webapp.models import *

class WustopiaModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_admin()

class BalanceAdmin(WustopiaModelView):
    column_filters = ('resource',)

class BuiltAdmin(WustopiaModelView):
    column_filters = ('user',)

class PlaceCategoryBenefitAdmin(WustopiaModelView):
    column_filters = ('placecategory', 'resource')


admin = admin.Admin(app, name=gettext("#Wustopia Admin") , template_mode='bootstrap3')
admin.add_view(WustopiaModelView(User, db.session))
admin.add_view(BalanceAdmin(Balance, db.session))
admin.add_view(WustopiaModelView(Place, db.session))
admin.add_view(BuiltAdmin(Built, db.session))
admin.add_view(PlaceCategoryBenefitAdmin(PlaceCategoryBenefit, db.session))
