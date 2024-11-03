import unittest
from app import app, db
from models import User, Rooms, Messages, Profile
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user,current_user

class FlaskTestRoomCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(use_cookies=True)
        self.app.testing = True
        self.app_context = app.app_context()
        testuser = User(name="testuser", username="testuser", password_hash=generate_password_hash("testpassword"), age=20, gender="male", email="tester@test.com", email_verified=1)
        testuser.profile = Profile(bio="test")
        db.session.add(testuser)
        db.session.commit()
        login_user(testuser, remember=True)
        
    def tearDown(self):
        db.session.delete()
        db.drop_all()
        
    def test_room(self):
        self.app.post('/create_room')