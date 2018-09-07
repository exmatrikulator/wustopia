import unittest
from flask_testing import TestCase
from manage import imoprtInitData

from webapp import db, app


class WustopiaTest(TestCase):

    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['SECRET_KEY'] = "testing"
        app.config['BCRYPT_LOG_ROUNDS'] = 2
        return app

    def setUp(self):
        db.create_all()
        imoprtInitData()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestFromAnonymous(WustopiaTest):

    def test_URL200(self):
        urls = ["/","/help","/help/dependencies.svg","/help/dependencies.png","/imprint","/ranking","/ranking/building/1","/ranking/building/1-Test"]
        urls.sort()
        for url in urls:
            print("check " + url)
            response = self.client.get(url)
            TestCase.assert200(self,response)


    def test_URL302(self):
        response = self.client.get("/map")
        TestCase.assertRedirects(self,response,"/?next=%2Fmap")

        response = self.client.get("/api/places")
        TestCase.assertRedirects(self,response,"/?next=%2Fapi%2Fplaces")


    def test_admin(self):
        from  webapp.models import User

        #not logged in
        response = self.client.get("/admin/")
        assert b"User" not in response.data

        response = self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))
        TestCase.assertEqual(self, db.session.query(User).count(), 1)

        #login as admin
        response = self.client.get("/admin/")
        assert b"User" in response.data

        response = self.client.get("/user/logout")
        #after loggout
        response = self.client.get("/admin/")
        assert b"User" not in response.data

        response = self.client.post("/user/create",data=dict(username="user",password="user",email="user@localhost"))
        TestCase.assertEqual(self, db.session.query(User).count(), 2)

        #login as user
        response = self.client.get("/admin/")
        assert b"User" not in response.data

class TestFromAdmin(WustopiaTest):
    def setUp(self):
        db.create_all()
        imoprtInitData()
        self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))

class TestFromUser(WustopiaTest):
    def setUp(self):
        db.create_all()
        imoprtInitData()
        self.client.post("/user/create",data=dict(username="admin",password="admin",email="admin@localhost"))
        self.client.post("/user/create",data=dict(username="user",password="user",email="user@localhost"))

    def test_build(self):
        from  webapp.models import Place
        import json
        db.session.add( Place( osmNodeId=1, lon=1, lat=1, placecategory_id=1, name="Test" ) )

        response = self.client.get("/build?place=1")
        TestCase.assert200(self,response)

        response = self.client.get("/api/resources")
        data = json.loads(response.data)
        amount = data[0]['amount']
        TestCase.assertEqual(self, amount, 90)

        response = self.client.get("/api/places")
        data = json.loads(response.data)
        ready = data[0]['ready']
        assert ready > 0


if __name__ == '__main__':
    unittest.main()
