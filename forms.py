import flask_mail
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, DateField,  SelectField, TextAreaField, PasswordField, RadioField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from flask_wtf.file import FileAllowed, FileField
from models import User
from flask_login import current_user

"""Main forms handler
Uses forms.py from auth to handle authentication related forms
"""

class RoomForm(FlaskForm):
    name = StringField("Room Name:", validators=[DataRequired()])
    photo = FileField("Upload Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Only Images are allowed")])
    submit = SubmitField("Create Room")

class MessageForm(FlaskForm):
    message = StringField("Enter a message", validators=[DataRequired()])
    submit = SubmitField("Send")
    
class RoomEditForm(FlaskForm):
    name = StringField("Room Name:", validators=[DataRequired()])
    photo = FileField("Upload Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Only Images are allowed")])
    submit = SubmitField("Edit Room")