import unittest
import json

from flask_testing import TestCase
from datetime import datetime

from manage import imoprtInitData, image_32px, generate_asset, pybabel
from webapp import db, app
from webapp.places import *
from webapp.models import Achievement, Built, PlaceCategory, Place, User

## Template test cases for Wustopia
class WustopiaTest(TestCase):
    ## create the test app with settings
    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['SECRET_KEY'] = "testing"
        app.config['BCRYPT_LOG_ROUNDS'] = 2
        return app

    ## setup for the tests
    def setUp(self):
        db.create_all()
        imoprtInitData()
        generate_asset()

    ## remove test DB
    def tearDown(self):
        db.session.remove()
        db.drop_all()

## tast cases for a Anonymous user
class TestFromAnonymous(WustopiaTest):
    ## check possible endpoint for a valid response (HTTP Code 200)
    def test_URL200(self):
        urls = ["/","/help","/imprint","/ranking","/ranking/building/1","/ranking/building/1-Test"]
        urls.sort()
        for url in urls:
            if app.debug:
                print("check " + url)
            response = self.client.get(url)
            TestCase.assert200(self, response)

    ## check for redirects (HTTP Code 302)
    def test_URL302(self):
        response = self.client.get("/map")
        TestCase.assertRedirects(self, response, "/?next=%2Fmap")

        response = self.client.get("/api/places")
        TestCase.assertRedirects(self, response, "/?next=%2Fapi%2Fplaces")

    ## test if Admin pages are not accessible
    def test_admin(self):
        # not logged in
        response = self.client.get("/admin/")
        self.assertNotIn(b"User", response.data)

        response = self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))
        TestCase.assertEqual(self, db.session.query(User).count(), 1)

        # login as admin
        response = self.client.get("/admin/")
        self.assertIn(b"User", response.data)

        response = self.client.get("/user/logout")
        # after loggout
        response = self.client.get("/admin/")
        self.assertNotIn(b"User", response.data)

        response = self.client.post("/user/create",data=dict(username="user",password="user",email="user@localhost"))
        TestCase.assertEqual(self, db.session.query(User).count(), 2)

        # login as user
        response = self.client.get("/admin/")
        self.assertNotIn(b"User", response.data)

    ## check if image_32px() is working
    def test_image_32px(self):
        TestCase.assertEqual(self, image_32px("/foo/bar.png"), "/foo/bar_32.png")
        TestCase.assertEqual(self, image_32px("//foo//bar.png"), "/foo/bar_32.png")

    ## check if help response the information from the import file
    # using the example of a bus stop
    def test_help(self):
        response = self.client.get("/help/building/3-Bus_Stop")
        TestCase.assert200(self, response)
        self.assertIn(b"117", response.data) # time
        self.assertIn(b"15", response.data) # beer
        self.assertIn(b"61", response.data) # gold

    ## check if update_places is collecting nodes
    def test_update_places(self):
        # to big
        response = self.client.get("/update_places/51.24871384304074,7.124140262603761,51.262586217199,7.1650171279907235")
        TestCase.assert200(self, response)
        TestCase.assertGreater(self, db.session.query(Place).count(), 100)

    ## check if achievements got imported
    def test_achievements(self):
        categories = db.session.query(PlaceCategory).count()
        TestCase.assertGreater(self, db.session.query(Achievement).count(), categories * 10)

## tast cases for a Admin user
# Amdin ID = 1
class TestFromAdmin(WustopiaTest):
    ## setup for the tests
    def setUp(self):
        db.create_all()
        imoprtInitData()
        self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))

## tast cases for a regular user
# Amdin ID = 1
# User ID = 2
class TestFromUser(WustopiaTest):
    ## setup for the tests
    def setUp(self):
        db.create_all()
        imoprtInitData()
        self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))
        self.client.post("/user/create",data=dict(username="user1",password="user",email="user@localhost"))

    ## check possible endpoint for a valid response (HTTP Code 200)
    def test_URL200(self):
        urls = ["/api/resources","/api/markerIcon","/api/places","/api/version","/api/check_achievements"]
        urls.sort()
        for url in urls:
            if app.debug:
                print("check " + url)
            response = self.client.get(url)
            TestCase.assert200(self, response)

    ## check if it is possible to build places
    def test_build(self):
        db.session.add( Place( osmNodeId=1, lon=1, lat=1, placecategory_id=PlaceCategory().get_id("busstop"), name="Test" ) )

        response = self.client.get("/build?place=1")
        TestCase.assert200(self, response)

        response = self.client.get("/api/resources")
        data = json.loads(response.data)
        amount = data[0]['amount']
        TestCase.assertEqual(self, amount, 90)

        response = self.client.get("/api/places")
        data = json.loads(response.data)
        ready = data[0]['ready']
        self.assertGreater(ready, 0)

        # test achievements
        response = self.client.get("/achievements")
        self.assertIn(b"1 Bus Stop", response.data)
        self.assertNotIn(b"2 Bus Stop", response.data)

    ## check if it is possible to get your earning
    def test_earn(self):
        db.session.add( Place( osmNodeId=1, lon=1, lat=1, placecategory_id=PlaceCategory().get_id("busstop"), name="Test" ) )
        response = self.client.get("/build?place=1")
        response = self.client.get("/api/resources")
        data = json.loads(response.data)
        amount = data[0]['amount']
        TestCase.assertEqual(self, amount, 90)

        # earn without rigth time
        response = self.client.get("/earn/1")
        response = self.client.get("/api/resources")
        data = json.loads(response.data)
        amount = data[0]['amount']
        TestCase.assertEqual(self, amount, 90)

        built = db.session.query(Built).first()
        built.lastcollect = datetime(1970, 1, 1, 1, 0, 0)
        db.session.add(built)
        db.session.commit()

        response = self.client.get("/earn/1")
        response = self.client.get("/api/resources")
        data = json.loads(response.data)
        amount = data[0]['amount']
        TestCase.assertEqual(self, amount, 91)

    ## check if you are listed at the ranking
    def test_ranking(self):
        self.test_build()
        response = self.client.get("/ranking/building/3-Bus_Stop")
        TestCase.assert200(self, response)
        self.assertIn(b"user1", response.data)

    def test_getUserPlaces(self):
        self.test_build()
        TestCase.assertEqual(self, len(getUserPlaces(2)), 1)
        db.session.add( Place( osmNodeId=2, lon=2, lat=2, placecategory_id=PlaceCategory().get_id("busstop"), name="Test2" ) )
        TestCase.assertEqual(self, len(getUserPlaces(2)), 1)


## test cases which doesn't need a DB
class TestWithoutDB(TestCase):
    ## create the test app with settings
    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        return app

    ## check translation files for empty strings
    def check_file(self, file):
        empty = 0
        old = 0
        with open(file) as f:
            content = f.readlines()
            for line in content:
                if "msgstr \"\"" in line:
                    empty = empty + 1
                if "#~ msgid" in line:
                    old = old + 1
        TestCase.assertEqual(self, empty, 2)    # how many multiline text?
        TestCase.assertEqual(self, old, 0)      # no old unused translations

    ## runs pybabel to check translations
    def test_translation(self):
        pybabel()
        self.check_file("webapp/translations/en/LC_MESSAGES/messages.po")
        self.check_file("webapp/translations/de/LC_MESSAGES/messages.po")


if __name__ == '__main__':
    #app.debug = True
    unittest.main()
