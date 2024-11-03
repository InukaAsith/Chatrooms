"""
Chat Rooms: A web application for creating and joining chat rooms.
==============================================================

Summary
-------

*   Flask web application
*   Uses Flask-SQLAlchemy for database operations
*   Uses Flask-Login for user authentication
*   Uses Flask-Mail to send emails
*   Uses Flask-SocketIO for real-time communication
*   Uses Flask-WTF for form validation
*   Uses WTForms for form creation
*   Uses Flask-Migrate for database migrations
*   Uses Flask-DebugToolbar for debugging
*   Uses Cloudinary for image uploads
*   Handles user authentication and profile management
*   Handles chat room creation, joining, managing
*   Handles error pages
*   Handles real-time communication
*   Handles image uploads
*   Handles database migrations
*   Handles debugging



BluePrints
----------

*   auth: Handles user authentication and profile management
*   main: Handles chat room creation, joining, managing and handles error pages

Routes
------

*   / (GET): Homepage
*   /login (GET, POST): Login page
*   /logout (POST): Logout
*   /signup (GET, POST): Signup page
*   /reset_password (GET, POST): Reset password page
*   /reset_password/<token> (POST): Reset password form
*   /dashboard (GET): Dashboard page
*   /edit_profile (GET, POST): Edit profile page
*   /delete_account (GET, POST): Delete account page
*   /chat (GET): Chat page
*   /create_room (GET, POST): Create room page
*   /join_room/<room_id> (GET, POST): Join room page
*   /messages/<room_id> (GET): Get messages for a room
*   /delete_room/<room_id> (POST): Delete a room
*   /delete_message/<message_id> (POST): Delete a message
*   /upload (POST): Upload an image

Imports
--------

*   mail function from auth.routes for sending mail
*   db from auth.models
*   Models from auth.models and models
"""


import os
from auth.routes import auth_bp, mail
from models import db, User, Room, Messages
from flask_login import current_user, LoginManager
from flask import Flask, abort, request, url_for, redirect, flash, render_template, send_from_directory, jsonify, session
from flask_login import login_required
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from forms import MessageForm, RoomEditForm, RoomForm
import cloudinary
import cloudinary.uploader
from functools import wraps 


# to set time
from sqlalchemy import func
from upload import FileUploadFailed, upload_file

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'))

"""
Summary of variables
---------------------

*   base_dir: The base directory of the project
*   app: The Flask app instance
*   app.config: The configuration of the app
*   SQLALCHEMY_DATABASE_URI: The URI of the database
*   SQLALCHEMY_TRACK_MODIFICATIONS: A boolean indicating whether to track object modifications
*   UPLOAD_LOCATION: The directory where uploaded files will be stored
*   MAX_CONTENT_LENGTH: The maximum size of the uploaded files
*   SECRET_KEY: The secret key used for session encryption
*   SESSION_COOKIE_HTTPONLY: A boolean indicating whether the session cookie should be http only
*   SESSION_COOKIE_SECURE: A boolean indicating whether the session cookie should be secure
*   MAIL_SERVER: The server used for sending emails
*   MAIL_PORT: The port used for sending emails
*   MAIL_USE_TLS: A boolean indicating whether to use TLS for sending emails
*   MAIL_USERNAME: The username used for sending emails
"""

app.config["SQLALCHEMY_DATABASE_URI"] =  os.environ.get('DATABASE_URI', "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS',False)
app.config["UPLOAD_LOCATION"] = os.environ.get('UPLOAD_LOCATION', 'uploads/')
app.config["MAX_CONTENT_LENGTH"] = os.environ.get('MAX_CONTENT_LENGTH',16*1024*1024)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', None)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

#flask security
app.config["SESSION_COOKIE_HTTPONLY"]
app.config["SESSION_COOKIE_SECURE"]

app.config["MAIL_SERVER"] = os.environ.get('MAIL_SERVER','smtp.gmail.com')
app.config["MAIL_PORT"] = os.environ.get('MAIL_PORT',587)
app.config['MAIL_USE_TLS'] =  os.environ.get('MAIL_USE_TLS',True)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', None)
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', None)
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', None)


cloudinary_name = os.environ.get('CLOUDINARY_CLOUD_NAME', None)
cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY', None)
cloudinary_secret = os.environ.get('CLOUDINARY_API_SECRET', None)

if cloudinary_name and cloudinary_api_key and cloudinary_secret:
    app.config["UPLOAD_LOCATION"] = 'cloudinary'
    cloudinary.config(
        cloud_name=cloudinary_name,
        api_key=cloudinary_api_key,
        api_secret=cloudinary_secret
    )

db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp, url_prefix='/auth')
socketio = SocketIO(app, manage_session=True)

with app.app_context():
    db.create_all()
    
    
# check admin for room ban edit info actions Wrapper
# requires room id to be in url
def admin_required(func):
    @wraps(func)
    def decorator(room_id=None,*args, **kwargs):
        if room_id:
            room = Room.query.get(room_id)
            if not room:
                abort(401)
            if current_user not in room.admins:
                abort(401)
            return func(room_id,*args, **kwargs)
        abort(401)
    return decorator
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Set theme and load main landing page"""
    if not session.get('theme'):
        session['theme'] = 1
    rooms = Room.query.order_by(Room.last_message.desc()).all()
    return render_template("index.html", rooms=rooms)
    
    
@app.route("/students")
@login_required
def students():
    students = User.query.all()
    return render_template("students.html", students=students)



@app.route("/uploads/<filename>")
def send_file(filename):
    """Send files on uploads directory in case of  inaccessibility due to server limits"""
    return send_from_directory(app.config["UPLOAD_LOCATION"], filename)

@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    """user info page"""
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)


@app.route('/create_room', methods=["POST", "GET"])
@login_required
def create_room():
    """Room creation"""
    form = RoomForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            author = current_user
            room = Room(name=name)
            photo = form.photo.data
            room.participants.append(author)
            try:
                photo_url = upload_file(photo,filename=room.id, path="chat_pictures")
                room.profile_photo = photo_url
            except FileUploadFailed as e:
                flash(f"Room image upload failed Error:{e}")
            except Exception:
                pass
            room.author = author
            room.admins.append(author)
            room.participants.append(author)
            db.session.add(room)
            db.session.commit()
            flash("Room Created successfully", 'success')
            socketio.emit('new_room',room.to_dict(), namespace='/')
            return redirect(url_for('room', room_id=room.id))
        return redirect('/')
    return render_template('create_room.html', form = form)
        
@app.route('/edit_room/<int:room_id>', methods=["POST", "GET"])
@admin_required
def edit_room(room_id):
    """Editing room"""
    room = Room.query.get(room_id)
    form = RoomEditForm(obj=room)
    if request.method == 'POST':
        if form.validate_on_submit():
            room.name = form.name.data 
            photo = form.photo.data
            try:
                photo_url = upload_file(photo,filename=room.id, path="chat_pictures")
                room.profile_photo = photo_url
            except FileUploadFailed as e:
                flash(f"Room image upload failed Error:{e}")
            except Exception as e:
                pass
            db.session.commit()
            flash(f"Room Edit failed","success")
            return redirect(url_for('room', room_id=room_id))
            
        flash(f"Room Edit failed")
        return redirect(url_for('room', room_id=room_id))
    return render_template('edit_room.html', form=form, room=room)


@app.route('/room/<int:room_id>')
def room(room_id):
    """Load room if not user is banned"""
    form = MessageForm()
    room = Room.query.get(room_id)
    messages = Messages.query.order_by(Messages.time).filter_by(room_id=room_id).all()
    rooms = Room.query.order_by(Room.last_message.desc()).all()
    if current_user in room.banned:
            flash("You are banned from this chat", "failed")
            return redirect(request.referrer)
    return render_template('chat.html', form=form, messages=messages, curr_room=room, rooms=rooms)

@app.route('/add_admin/<int:room_id>', methods=["GET","POST"])
def add_admin(room_id):
    """Admin setup"""
    room = Room.query.get(room_id)
    if current_user != room.author:
        abort(401)
    if request.method == "POST":
        data = request.get_json()
        user  = User.query.get(data["user_id"])
        room.admins.append(user)
        try: 
            db.session.commit()
            return jsonify(success=True)
        except:
            db.session.rollback()
            return jsonify(success=False)
    return render_template('add_admin.html', room=room)
    
@app.route('/ban_user/<int:room_id>', methods=["GET","POST"])
@admin_required
def ban_user(room_id):
    room = Room.query.get(room_id)
    if request.method == "POST":
        data = request.get_json()
        user  = User.query.get(data["user_id"])
        if user in room.admins:
            abort(401)
        room.banned.append(user)
        room.participants.remove(user)
        try: 
            db.session.commit()
            return jsonify(success=True)
        except:
            db.session.rollback()
            return jsonify(success=False)
    return render_template('ban_user.html', room=room)
    
@app.route('/remove_admin/<int:room_id>', methods=["POST"])
def remove_admin(room_id):
    room = Room.query.get(room_id)
    if current_user != room.author:
        abort(401)
    data = request.get_json()
    user  = User.query.get(data["user_id"])
    if user in room.admins:
        room.admins.remove(user)
    else:
        return jsonify(success=False)
    try: 
        db.session.commit()
        return jsonify(success=True)
    except:
        db.session.rollback()
        return jsonify(success=False)

    
        
@app.route('/unban_user/<int:room_id>', methods=["GET","POST"])
@admin_required
def unban_user(room_id):
    room = Room.query.get(room_id)
    room = Room.query.get(room_id)
    data = request.get_json()
    user  = User.query.get(data["user_id"])
    if user in room.banned:
        room.banned.remove(user)
    else:
        return jsonify(success=False)
    try: 
        db.session.commit()
        return jsonify(success=True)
    except:
        db.session.rollback()
        return jsonify(success=False)


"""Socketio connection setup"""
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': "A user has joined the room"}, room=room)

@app.route('/send_message/<int:room_id>', methods=["POST"])
@login_required
def send_message(room_id):
    """Send message. uses socketio
    chat.html, rooms_sidebar.html, right_click_menu.html is associated"""
    form = MessageForm()
    if form.validate_on_submit():
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                "status":'failed',
            })
        message = Messages(content=form.message.data,author=current_user, room=room, time=func.current_timestamp())
        room.last_message = func.current_timestamp()
        room.message_count = room.message_count +1
        if not current_user in room.participants:
            room.participants.append(current_user)
        db.session.add(message)
        db.session.commit()
        socketio.emit('new_message', message.to_dict(), room=str(room_id))
        return jsonify(success=True, message=message.to_dict())
    return jsonify(success=False, errors=form.errors)

@app.route('/delete_message/<int:message_id>', methods=["POST"])
@login_required
def delete_message(message_id):
    """Deletes a message"""
    message = Messages.query.get(message_id)
    room = str(message.room_id)
    if (current_user.id == message.author.id) or ((current_user in message.room.admins)):
        if current_user != message.author and current_user != message.room.author and message.author in message.room.admins:
            abort(401) 
        message.room.message_count = message.room.message_count - 1
        db.session.delete(message)
        db.session.commit()
        socketio.emit('message_delete', {"id":message_id}, room=room)
        return jsonify({"status": "success", 
                        "id": message_id})
    return jsonify({"status": 'failed',
                    "id": message_id})

@app.route('/delete_room/<int:room_id>', methods=['POST'])
@admin_required
@login_required
def delete_room(room_id):
    room = Room.query.get(room_id)
    if not current_user.id == room.author_id:
        return jsonify({"status": 'failed',
                        "id": room_id})
    db.session.delete(room)
    db.session.commit()
    socketio.emit('room_delete', {"id":room_id}, namespace='/')
    return jsonify({"status": "success", 
                    "id": room_id})

@app.route('/get_room/<int:room_id>', methods=["POST"])
def get_room(room_id):
    room = Room.query.get(room_id)
    
    return jsonify(room.to_dict())

@app.route('/update_session', methods=["POST"])
def update_session():
    """Updates user session. send a custom key and value as json to set in user session"""
    data = request.get_json()
    for key, value in data.items():
        session[key] = value
    return jsonify({"message":"session updated"})


"""Error Handlers"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpage.html', error_code=404, error_details="Page not found", exception=str(e))

@app.errorhandler(401)
def forbidden(e):
    return render_template('errorpage.html', error_code=401, error_details="You are Not Allowed", exception=str(e))


@app.errorhandler(500)
def page_not_found(e):    
    return render_template('errorpage.html', error_code=500, error_details="It's not you. It's Us.", exception=str(e))


"""Send static files if hosting service not sharing statics publicly"""
@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(
        os.path.join(root_dir, 'static'), 
        filename
    )


if __name__ == "__main__":
    socketio.run(app)
    
