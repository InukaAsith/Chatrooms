from auth.models import User, Profile, FileUpload, db
from datetime import datetime

"""Models for main app. Extends on models from auth.models"""

participants_table = db.Table('pariticipants',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)                                  
)
admins_table = db.Table('admins',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)                                  
)
banned_table = db.Table('banned',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)                                  
)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref("rooms_own", lazy=True))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_message = db.Column(db.DateTime, default=datetime.utcnow)
    participants = db.relationship('User', backref=db.backref("rooms_participant", lazy=True, cascade="all, delete"), secondary=participants_table)
    admins = db.relationship('User', backref=db.backref("rooms_admin", lazy=True, cascade="all, delete"), secondary=admins_table)
    banned = db.relationship('User', backref=db.backref("rooms_banned", lazy=True, cascade="all, delete"), secondary=banned_table)
    message_count = db.Column(db.Integer, default=0)
    profile_photo = db.Column(db.String(100), default='/static/unknown_chat.png', nullable=True, unique=False)
    def to_dict(self):
        return {
            'id': self.id,
            'profile_photo': self.profile_photo,
            'name': self.name,
            'author': self.author.to_dict(),
            'created': self.created.isoformat() if self.created else  None,
            'last_message': self.last_message.isoformat() if self.last_message else None,
            'participants': [participant.to_dict() for participant in self.participants],
            'admins': [participant.to_dict() for participant in self.admins],
            'banned': [participant.to_dict() for participant in self.banned],
            'message_count':self.message_count 
        }
    
class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref("messages", lazy=True))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref("messages", lazy=True, cascade="all, delete"))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.to_dict(),
            'room': self.room.to_dict(),
            'time': self.time.isoformat() if self.time else None
        }
