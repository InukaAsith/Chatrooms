from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime , timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer
import random

"""Main user model

    includes:
        User Model
        Profiles Model
        FileUpload model
    
    
"""

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username=db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    email = db.Column(db.String(100), nullable=False, unique=True)
    otp = db.Column(db.String(6))
    otp_expiration = db.Column(db.DateTime)
    email_verified = db.Column(db.Boolean, default=False)
    profile = db.relationship('Profile', backref="user", uselist=False, cascade="all, delete")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'email_verified': self.email_verified,
            'profile': self.profile.to_dict(),
        }
    def set_otp(self):
        self.otp = self.generate_otp()
        self.otp_expiration = datetime.utcnow() + timedelta(minutes=10)
        
    def verify_otp(self, otp):
        if self.otp == otp and self.otp_expiration >= datetime.utcnow():
            return True
        return False
    
    def generate_otp(self):
        return str(random.randint(100000, 999999))
    
    def get_confirmation_token(self, expires_sec=1000):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.email, salt='email-confirm')    
    
    @staticmethod
    def verify_confirmation_token(token, expires_sec=1000):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(token, salt='email-confirm', max_age=expires_sec)
        except:
            return None
        return email
    
     
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
class Profile(db.Model):
    __tablename__ = 'profile'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    bio = db.Column(db.Text)
    profile_picture = db.relationship('FileUpload', backref="profile", uselist=False, cascade="all, delete")
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'bio': self.bio,
            'profile_picture': self.profile_picture.to_dict() if self.profile_picture else None,
        }
    
class FileUpload(db.Model):
    __tablename__ = 'file_upload'
    id = db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    profile_user_id = db.Column(db.Integer, db.ForeignKey('profile.user_id'))
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'profile_user_id': self.profile_user_id,
        }
