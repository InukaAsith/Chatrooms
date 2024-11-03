
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, DateField,  SelectField, TextAreaField, PasswordField, RadioField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from flask_wtf.file import FileAllowed, FileField
from models import User
from flask_login import current_user

"""Validators and forms for auth

checks if username already taken
if email taken

validity of passwords, email
upload file types and sizes
generate and validate otp and secret login key

"""

class AgeValidator:
    def __call__(self, form, field):
        age = field.data
        if not age or age<9 or age > 100:
            raise ValidationError("Enter a valid age range")
        
class PasswordValidator:
    def __call__(self, form, field):
            if not (len(field.data) >= 8 or len(field.data) <=12) or not any(char.isdigit() for char in field.data) or not any(char.isupper() for char in field.data) or not any(char.islower() for char in field.data) or not any(not char.isalnum() for char in field.data):
                raise ValidationError("Password must be 8-12 characters long and must contain at least a lowercase letter, uppercase letter, a number and a symbol")
        
class EmailValidator:
    def __call__(self, form, field):
        user = User.query.filter_by(email=field.data.lower()).first()
        try:
            if user and user.id != current_user.id:
                raise ValidationError("Email already taken")
        except AttributeError as e:
            raise ValidationError("Email already taken")


class UsernameValidator:
    def __call__(self, form, field):
        user = User.query.filter_by(username=field.data.lower()).first()
        try:
            if user and user.id != current_user.id:
                raise ValidationError("Username already taken")
        except AttributeError as e:
            raise ValidationError("Username already taken")
class PasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), PasswordValidator()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Change Password")

class DeleteForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class EditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=16)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16), UsernameValidator()])
    age = IntegerField("Age", validators=[DataRequired(), AgeValidator()])
    email = StringField("Email", validators=[DataRequired(), Email(), EmailValidator()])
    bio = TextAreaField("About Me")
    gender = SelectField("Select your Gender", choices=[
        ("male","👦🏻 Male"),
        ("female", "👧🏻 Female")
    ])
    photo = FileField("Upload Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Only Images are allowed")])
    submit = SubmitField("Save")

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=16)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16), UsernameValidator()])
    age = IntegerField("Age", validators=[DataRequired(), AgeValidator()])
    email = StringField("Email", validators=[DataRequired(), Email(), EmailValidator()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8), PasswordValidator()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    bio = TextAreaField("About Me")
    gender = RadioField("Select your Gender", choices=[
        ("male","👦🏻 Male"),
        ("female", "👧🏻 Female")
    ], validators=[DataRequired()])
    photo = FileField("Upload Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Only Images are allowed")])
    submit = SubmitField("Register")
    
class LoginForm(FlaskForm):
    username = StringField("Enter Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")

class OtpForm(FlaskForm):
    otp = StringField('Enter OTP code sent to email or use login link in email', validators=[DataRequired(), Length(min=6, max=6, message='OTP Must be 6 characters long')])
    submit = SubmitField('Check OTP')
    
class UsernameForm(FlaskForm):
    username = StringField("Enter Username", validators=[DataRequired()])
    submit = SubmitField("Send OTP")
    
class ResetForm(FlaskForm):
    new_password = PasswordField("Enter new password", validators=[DataRequired(), PasswordValidator()])
    confirm_password = PasswordField("Confirm new password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Set Password")
    