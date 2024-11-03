"""
auth routes. Handles user authentication and profile management

Contains routes for user login, signup, password reset, otp verification,
editing profile information, deleting account, and a dashboard to view and
edit profile information.

Uses flask_login to handle user authentication and session management.

Imported from models.py, Profile model, User model, and FileUpload model are
used to interact with the database.

Custom forms are used to validate user input for login, signup, password reset,
otp verification, and editing profile information.

flask_mail is used to send emails for password reset and otp verification

"""




from flask import Blueprint, render_template, request, redirect, url_for, session, flash,current_app
from upload import FileUploadFailed
from upload import upload_file
from .models import db, User, Profile, FileUpload
import os
from .forms import PasswordForm, LoginForm, RegistrationForm, EditForm, OtpForm, UsernameForm, ResetForm, DeleteForm
from flask_login import login_user, logout_user, login_required, current_user

from flask_mail import Mail, Message
mail = Mail()

auth_bp = Blueprint('auth', __name__, template_folder="templates")

def send_email(user, verify=True):
    token = user.get_confirmation_token()
    if not current_app.config['MAIL_USERNAME'] or not current_app.config['MAIL_PASSWORD']:
        session['user_id'] = user.id
        return
    try:
        user.set_otp()
        db.session.commit()
        
        msg = Message('Verify Email',
                        recipients=[f'{user.email}'], sender=current_app.config['MAIL_USERNAME'])
        if verify:
            login_link = url_for('auth.verify_email', token=token, _external=True)
        else:
            login_link = url_for('auth.reset_pass', token=token, _external=True)
        msg.html = render_template('verification_email.html', user=user, login_link=login_link)
        with current_app.app_context():
            mail.send(msg)
        flash("Verification Email sent", 'success')
        session['user_id'] = user.id
    except:
        flash("Verification Email failed", 'failed')

    
@auth_bp.route('/check_otp', methods=["GET","POST"])
def check_otp():
    form = OtpForm()
    if not session.get('user_id'):
        flash("Enable cookies or try email link", 'failed')
        return redirect('auth.dashboard')
    user_id = session.get('user_id')
    user = User.query.filter_by(id = user_id).first()
    if request.method == "POST":
        if user.verify_otp(form.otp.data) == True:
            user.email_verified = True
            flash("Email Verified", 'success')
            db.session.commit()
            session.pop('user_id', None)
            return redirect(url_for('auth.login'))
        flash("OTP verification failed. Try using link in email", 'failed')
        return redirect(url_for('auth.login'))
    if not current_app.config['MAIL_USERNAME'] or not current_app.config['MAIL_PASSWORD']:
        user.email_verified = True
        flash("Email Auto Verified (No email authentication set by site owner)", 'success')
        db.session.commit()
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    return render_template('otp.html', form=form)
            
    
@auth_bp.route('/forgot_password', methods=["GET","POST"])
def forgot_password():

    if not session.get('step'):
        session['step'] = 1
    if session['step'] == 1:
        form = UsernameForm()
        if request.method == "POST":
            username = form.username.data
            user = User.query.filter_by(username=username.lower()).first()
            if not user:
                user = User.query.filter_by(email=username.lower()).first()
            if user:
                send_email(user, verify=False)
                session['step'] = 2
                return redirect(url_for('auth.forgot_password'))
            flash("Password Reset failed", 'failed')
            return redirect(url_for('auth.login'))
        return render_template('password_reset.html', form=form, step=session['step'])
    elif session['step'] == 2:
        if not current_app.config['MAIL_USERNAME'] or not current_app.config['MAIL_PASSWORD']:
            session['step'] = 3
            return render_template('password_reset.html', form=form, step=session['step'])
        form = OtpForm()
        if not session.get('user_id'):
            flash("Enable cookies or try email link", 'failed')
            return redirect('auth.dashboard')
        user_id = session.get('user_id')
        user = User.query.filter_by(id = user_id).first()
        if request.method == "POST":
            if user.verify_otp(form.otp.data) == True:
                session['step'] = 3
                flash("OTP Verified", 'success')
                return redirect(url_for('auth.forgot_password'))
            flash("OTP verification failed. Try using link in email", 'failed')
            return redirect(url_for('auth.login'))
        return render_template('password_reset.html', form=form, step=session['step'])
    elif session['step'] == 3:
        form = ResetForm()
        if not session.get('user_id'):
            flash("Enable cookies or try email link", 'failed')
            return redirect(url_for('auth.dashboard'))
        user_id = session.get('user_id')
        user = User.query.filter_by(id = user_id).first()
        if request.method == "POST":
            password = form.new_password.data
            user.set_password(password)
            db.session.commit()
            flash("Password changed. please login", 'success')
            session.pop('step', None)
            session.pop('user_id', None)
            return redirect(url_for('auth.login'))
        return render_template('password_reset.html', form=form, step=session['step'])     
                

@auth_bp.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    try:
        if current_user.id:
            return redirect(url_for('auth.dashboard'))
    except Exception as e:
        pass
    session.pop('step', None)
    session.pop('user_id', None)
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data
            user = User.query.filter_by(username=username.lower()).first()
            if not user:
                user = User.query.filter_by(email=username.lower()).first()
            if user and user.check_password(password):
                if not user.email_verified:
                    form.password.errors.append("Please verify your email before signing in")
                    flash("Please Verify your email", 'warning')
                    send_email(user)
                    return redirect(url_for('auth.check_otp'))
                login_user(user, remember=remember)
                flash('Logged in successfully', category='success')
                return redirect(url_for('index'))
            form.password.errors.append("Username or password error")
            flash("Login failed",'failed')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if request.method=="POST":
        
        if form.validate_on_submit():
            name = form.name.data
            username = form.username.data.lower()
            password = form.password.data
            age = form.age.data
            email = form.email.data.lower()
            bio = form.bio.data
            gender = form.gender.data
            photo = form.photo.data #file object
            new_user = User(name=name, username=username, age=age, email=email, gender=gender)
            new_user.set_password(password)
            new_user.profile = Profile(bio=bio)
            try:
                photo_url = upload_file(file=photo, filename=username)
                new_user.profile.profile_picture = FileUpload(filename=photo_url)
            except FileUploadFailed as e:
                flash(f'Account creation Image upload failed error:{e}','failed')
            except Exception:
                pass
            db.session.add(new_user)
            try:
                db.session.commit()
                flash(f'Account created for {form.username.data}',category='success')
                send_email(user=new_user)
                return redirect(url_for('auth.check_otp'))
            except Exception as e:
                db.session.rollback()
                flash(f'Account creation failed','failed')
                return redirect(url_for('auth.register'))
    return render_template("register.html", form=form)
    

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('step', None)
    session.pop("user_id", None)
    flash("Logged out", category='success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/edit_profile', methods=["POST", "GET"])
@login_required
def edit_profile():
    user = current_user
    if user.profile.bio:
        user.bio = user.profile.bio
    form = EditForm(obj=user)
    if request.method == 'POST':            
        if form.validate_on_submit():
            user.name = form.name.data
            user.username = form.username.data.lower()
            user.age = form.age.data
            user.email = form.email.data.lower()
            user.profile.bio = form.bio.data if form.bio.data else ""
            user.gender = form.gender.data
            photo = form.photo.data
            try:
                photo_url = upload_file(file=photo, filename=user.username)
                user.profile.profile_picture = FileUpload(filename=photo_url)
            except FileUploadFailed as e:
                flash(f'Account creation Image upload failed error:{e}','failed')
            except Exception:
                pass
            try:
                db.session.commit()
                flash('Account details changed',category='success')
            except Exception as e:
                db.session.rollback()
                flash('Error occurred while editing data','failed')
            return redirect(url_for('auth.dashboard'))
        return render_template("edit_user.html", form=form)
    return render_template("edit_user.html", form=form)

@auth_bp.route('/reset_password', methods=["POST","GET"])
@login_required
def reset_password():
    form = PasswordForm()
    user = current_user
    if request.method == "POST":
        if not user: 
            flash('Not authorized','failed')
            return redirect('auth.dashboard')
        if form.validate_on_submit():
            if user.check_password(form.current_password.data):
                user.set_password(form.new_password.data)
                try:
                    db.session.commit()
                    flash('Password changed successfully. Please login', category='success')
                    return redirect(url_for('auth.logout'))
                except Exception as e:
                    db.session.rollback()
                    flash('Password changing failed', 'failed')
            form.current_password.errors.append("Password incorrect")
            flash('Password reset failed','failed')
    return render_template('reset_password.html', form=form) 
                    
            
@auth_bp.route('verify_email/<token>')
def verify_email(token):
    if token:
        email = User.verify_confirmation_token(token)
        if email:
            user = User.query.filter_by(email=email).first()
            user.email_verified = True
            db.session.commit()
            flash('Email verification successful, Please login', 'success')
            return redirect(url_for('auth.login'))
    flash('Invalid token','failed')
    return redirect('/')
    
@auth_bp.route('reset_pass/<token>')
def reset_pass(token):
    if token:
        email = User.verify_confirmation_token(token)
        if email:
            user = User.query.filter_by(email=email).first()
            session['user_id'] = user.id
            session['step'] = 3
            return redirect(url_for('auth.forget_password'))
    flash('Invalid token','failed')
    return redirect('/')
    

@auth_bp.route('/account_delete', methods=["GET", "POST"])
@login_required
def account_delete():
    form = DeleteForm()
    if request.method == "POST":
        user = current_user
        if user.check_password(form.password.data):
            try:
                db.session.delete(user)
                db.session.commit()
                logout_user()
                session.clear()
                flash("User deleted successfully", 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
        form.password.errors.append("Password incorrect")
        flash("Account deletion failed", 'failed')
        return redirect(url_for('auth.login')) 
    return render_template('account_delete.html', form=form)               


@auth_bp.route('/')
def index():
    return redirect(url_for('auth.dashboard'))