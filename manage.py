#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from webapp import app, db
from webapp.models import *

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

def session_add(model):
    try:
        db.session.add(model)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        if app.debug:
            print(e)

@manager.command
def imoprtInitData():
    "Inititalise the database"
    import csv

    print("import PlaceCategory")
    with open('webapp/import/PlaceCategory.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            if len(row) == 4:
                session_add( PlaceCategory( name=row[0], filter=row[1], markerColor=row[2], icon=row[3] ) )
            else:
                session_add( PlaceCategory( name=row[0], filter=row[1], markerColor=row[2] ) )

    print("import Resource")
    with open('webapp/import/Resource.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            if len(row) == 3:
                session_add( Resource( name=row[0], image=row[1], major=bool(row[2]) ) )
            else:
                session_add( Resource( name=row[0], image=row[1] ) )

    print("import BuildCost")
    with open('webapp/import/BuildCost.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(BuildCost(placecategory_id=PlaceCategory().get_id(row[0]), level=row[1], time=row[2]))

    print("import BuildCostResource")
    with open('webapp/import/BuildCostResource.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(BuildCostResource(buildcost_id=BuildCost().get_id(row[0],row[1]), resource_id=Resource().get_id(row[2]), amount=row[3]))

    print("import PlaceCategoryBenefit")
    with open('webapp/import/PlaceCategoryBenefit.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(PlaceCategoryBenefit(placecategory_id=PlaceCategory().get_id(row[0]), resource_id=Resource().get_id(row[1]), level=row[2], amount=row[3], interval=row[4]))

    print("done")

@manager.command
def pybabel():
    "Generate new translations"
    import os
    os.system('pybabel extract -F babel.cfg -o messages.pot .')
    os.system('pybabel update -i messages.pot -d webapp/translations')
    os.system('pybabel compile -d webapp/translations')


@manager.command
def bcryptbenchmark():
    "Test number of rounds"
    # Chance the number of rounds (second argument) until it takes between
    # 0.25 and 0.5 seconds to run.
    from flask.ext.bcrypt import generate_password_hash
    import time
    duration = 0
    i=4
    while duration < 0.25:
        start = time.time()
        generate_password_hash('password1', i)
        end = time.time()
        duration = end - start
        i += 1
    print( "(" + str(duration) + " secounds)")
    print( "please copy the next line into config.py")
    print( "")
    print( "BCRYPT_LOG_ROUNDS=" + str(i))

if __name__ == "__main__":
    app.debug = True
    manager.run()
