#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from distutils.util import strtobool
from flask_babel import gettext

from webapp import app, db, session_add
from webapp.models import *

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def imoprtInitData():
    """Inititalise the database"""
    import csv

    importTextToTranslate = []
    if app.debug:
        print("import PlaceCategory")
    with open('webapp/import/PlaceCategory.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            if row[1]:
                importTextToTranslate.append(row[1])
            if row[2]:
                importTextToTranslate.append(row[2])
            if len(row) == 6:
                session_add( PlaceCategory( slug=row[0], name=row[1], description=row[2], filter=row[3], markerColor=row[4], icon=row[5] ) )
            else:
                session_add( PlaceCategory( slug=row[0], name=row[1], description=row[2], filter=row[3], markerColor=row[4] ) )

    if app.debug:
        print("import Resource")
    with open('webapp/import/Resource.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            importTextToTranslate.append(row[1])
            if len(row) == 4:
                session_add( Resource( slug=row[0], name=row[1], image=row[2], major=bool(int(row[3])) ) )
            else:
                session_add( Resource( slug=row[0], name=row[1], image=row[2] ) )

    if app.debug:
        print("generate importTextToTranslate.txt")
    with open('importTextToTranslate.txt', 'w') as f:
        for text in importTextToTranslate:
            f.write("gettext(\"#%s\")\n" % text)


    if app.debug:
        print("import BuildCost")
    with open('webapp/import/BuildCost.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(BuildCost(placecategory_id=PlaceCategory().get_id(row[0]), level=row[1], time=row[2]))


    if app.debug:
        print("import BuildCostResource")
    with open('webapp/import/BuildCostResource.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(BuildCostResource(buildcost_id=BuildCost().get_id(row[0],row[1]), resource_id=Resource().get_id(row[2]), amount=row[3]))


    if app.debug:
        print("import PlaceCategoryBenefit")
    with open('webapp/import/PlaceCategoryBenefit.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(PlaceCategoryBenefit(placecategory_id=PlaceCategory().get_id(row[0]), resource_id=Resource().get_id(row[1]), level=row[2], amount=row[3], interval=row[4]))


    if app.debug:
        print("import Achievements")
    categories = db.session.query(PlaceCategory).all()
    amounts = [1,2,5,10,20,50,100,200,500,1000]
    for category in categories:
        last_amount=0
        for amount in amounts:
            if last_amount == 0:
                dependson = ""
            else:
                dependson = str(last_amount) + category.slug
            session_add(Achievement(slug=str(amount)+category.slug,
                name=str(amount)+" "+category.name,
                description=gettext("#build %s of %s" % (amount, category.name)),
                dependson=dependson,
                hidden=True,
                stars=amount))
            last_amount = amount

    with open('webapp/import/Achievements.csv', 'r') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content) # skip header
        for row in content:
            session_add(Achievement(slug=row[0], name=row[1], description=row[2], dependson=row[3], hidden=strtobool(row[4]), stars=row[5]))

    if app.debug:
        print("done")

# returns the image name with a "_32" suffix
def image_32px(image):
    filename, file_extension = os.path.splitext(image)
    return str(filename + "_32" + file_extension).replace("//","/")


def help_dependencies(format):
    from graphviz import Digraph
    dot = Digraph(engine = 'circo')
    dot.attr('node', shape='box', style='filled', fontname = "DejaVu")

    dot.attr('node', color='#ffcb92')
    for resource in db.session.query(Resource).all():
        image = image_32px("webapp/"+str(resource.image))
        if os.path.exists(image):
            dot.node("res_" + str(resource.id), image=image, label=resource.name, labelloc="t")
        else:
            dot.node("res_" + str(resource.id), label=resource.name, labelloc="t")

    dot.attr('node', color='#00d1b2')
    for place in db.session.query(PlaceCategory).all():
        dot.node("place_" + str(place.id), place.name)

    dot.attr('edge',color='#23D160')
    for benefit in db.session.query(PlaceCategoryBenefit.placecategory_id, PlaceCategoryBenefit.resource_id ).distinct():
        dot.edge("place_" + str(benefit.placecategory_id), "res_" + str(benefit.resource_id))

    dot.attr('edge',color='#FF3860')
    for cost in db.session.query(BuildCost, BuildCostResource).join(BuildCostResource).distinct(BuildCost.placecategory_id, BuildCostResource.resource_id):
        dot.edge("res_" + str(cost.BuildCostResource.resource_id), "place_" + str(cost.BuildCost.placecategory_id))


    if format == "svg":
        dot.format = "svg"
        dot.render(filename = "webapp/static/images/dependencies", cleanup=True)
    elif format == "png":
        dot.format = "png"
        dot.render(filename = "webapp/static/images/dependencies", cleanup=True)


@manager.command
def generate_asset():
    from PIL import Image
    import os
    for root, dirs, files in os.walk('webapp/static/images/resources'):
        for name in files:
            file = os.path.join(root, name)
            filename, file_extension = os.path.splitext(file)
            if file_extension != ".png" or filename.endswith("_32"):
                continue

            img = Image.open(file)
            img = img.resize((32,32))
            img.save(filename + "_32" + file_extension)
    help_dependencies("png")
    help_dependencies("svg")

@manager.command
def pybabel():
    """Generate new translations"""
    import os
    os.system('pybabel extract --sort-output -F babel.cfg -k lazy_gettext -o messages.pot .')
    os.system('pybabel update -i messages.pot -d webapp/translations')
    os.system('sed -i.bak "2,16 d" webapp/translations/*/LC_MESSAGES/messages.po') #remove annoying header
    # babel hack to commit to git and open in Qt Linguist
    localeDirs = [name for name in os.listdir("webapp/translations")]
    for locale in localeDirs:
        append_copy = open("webapp/translations/%s/LC_MESSAGES/messages.po" % locale, "r")
        original_text = append_copy.read()
        append_copy.close()

        append_copy = open("webapp/translations/%s/LC_MESSAGES/messages.po" % locale, "w")
        append_copy.write('msgid ""\n\
msgstr ""\n\
"MIME-Version: 1.0\\n"\n\
"Content-Type: text/plain; charset=UTF-8\\n"\n\
"Content-Transfer-Encoding: 8bit\\n"\n\
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n\
"X-Language: %s\\n"\n\
"X-Source-Language: en\\n"\n' % locale)
        append_copy.write(original_text)
        append_copy.close()

    pybabel_compile()

@manager.command
def pybabel_compile():
    """Compile translations"""
    import os
    from pojson import convert
    os.system('pybabel compile -f -d webapp/translations')

    if not os.path.exists("webapp/static/translations"):
        os.makedirs("webapp/static/translations")
    localeDirs = [name for name in os.listdir("webapp/translations")]
    for locale in localeDirs:
        print("gen: " + locale)
        input = convert("webapp/translations/%s/LC_MESSAGES/messages.po" % locale)
        name = "webapp/static/translations/%s.json" % locale
        with open(name, 'w') as f:
            f.write("{'wustopia': %s }" % input)

@manager.command
def bcryptbenchmark():
    """Test number of rounds"""
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
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    manager.run()
