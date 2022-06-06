from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from api.models import User
from api.app import db

auth = Blueprint('auth', __name__)


# Login page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        if request.method == 'POST':
            # Get fields from form
            email = request.form.get('email')
            password = request.form.get('password')

            # Checks for the user in the database
            user = User.query.filter_by(email=email).first()
            if user:
                # Checks user password
                if check_password_hash(user.password, password):
                    # Logs in user and redirects to the home page
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password.', category='danger')
            else:
                flash('Email does not exist.', category='danger')

        return render_template("login.html", current_user=current_user, page="login")
    else:
        flash('You are already logged in.', category='secondary')
        return redirect(url_for('views.home'))


# Logout page
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Users page
@auth.route('/users')
@login_required
def users():
    if current_user.admin:
        users = User.query.all()
        return render_template("users.html", current_user=current_user, page="users", users=users)
    else:
        abort(403)


# Add user page
@auth.route('/adduser', methods=['GET', 'POST'])
@login_required
def adduser():
    if current_user.admin:
        if request.method == 'POST':
            # Get fields from form
            email = request.form.get('email')
            name = request.form.get('name')
            admin = request.form.get('admin') == "on"
            password = request.form.get('password')
            password2 = request.form.get('password2')

            # Validate user information
            user = User.query.filter_by(email=email).first()
            if user:
                flash('This email already exists.', category='danger')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='danger')
            elif len(password) < 7:
                flash('Password must be at least 7 characters.', category='danger')
            elif password != password2:
                flash('Passwords do not match.', category='danger')
            else:
                # Creates new user in the database, and redirects to the admin page
                new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
                new_user.admin = admin
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully.', category='success')
                return redirect(url_for('auth.users'))

        return render_template("adduser.html", current_user=current_user, page="adduser")
    else:
        abort(403)


# Edit user page
@auth.route('/edituser/<userid>', methods=['GET', 'POST'])
@login_required
def edituser(userid):
    if current_user.admin:
        user = User.query.filter_by(id=userid).first()
        if not user:
            flash('User does not exist.', category='danger')
            return redirect(url_for('auth.users'))

        if request.method == 'POST':
            # Get fields from form
            email = request.form.get('email')
            name = request.form.get('name')
            admin = request.form.get('admin') == "on"
            password = request.form.get('password')
            password2 = request.form.get('password2')

            # Validate user information
            if len(email) < 4:
                flash('Email must be greater than 3 characters.', category='danger')
            elif password and len(password) < 7:
                flash('Password must be at least 7 characters.', category='danger')
            elif password != password2:
                flash('Passwords do not match.', category='danger')
            else:
                user.email = email
                user.name = name
                user.admin = admin
                if password:
                    user.password = generate_password_hash(password, method='sha256')
                db.session.add(user)
                db.session.commit()
                flash('User updated successfully.', category='success')
                return redirect(url_for('auth.users'))

        return render_template("edituser.html", current_user=current_user, page="edituser", user=user)
    else:
        abort(403)


# Delete user page
@auth.route('/deleteuser/<userid>')
@login_required
def deleteuser(userid):
    if current_user.admin:
        user = User.query.filter_by(id=userid).first()
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', category='success')
        return redirect(url_for('auth.users'))
    else:
        abort(403)
