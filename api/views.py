from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from api.models import Booking, Room
from api.app import db
import json

views = Blueprint('views', __name__)


# Home page
@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("index.html", current_user=current_user, page="home")
    else:
        return redirect(url_for('auth.login'))


# Bookings page
@views.route('/bookings')
@login_required
def bookings():
    bookings = Booking.query.all()
    return render_template("bookings.html", current_user=current_user, page="bookings", bookings=bookings)


# New booking page
@views.route('/newbooking', methods=['GET', 'POST'])
@login_required
def newbooking():
    if request.method == 'POST':
        # Get fields from form
        name = request.form.get('name')
        room = request.form.get('room')
        phone = request.form.get('phone')
        oldcode = Booking.query.order_by(Booking.id.desc()).filter_by(room=room).first().current_code

        newcode = generate_code()

        # Creates new booking in the database
        new_booking = Booking(name=name, room=room, phone=phone, old_code=oldcode, current_code=newcode)
        db.session.add(new_booking)
        db.session.commit()
        flash('Booking created successfully.', category='success')
        return redirect(url_for('views.viewkey', bookingid=new_booking.id))

    return render_template("newbooking.html", current_user=current_user, page="newbooking")


# View key card page
@views.route('/viewkey/<bookingid>')
@login_required
def viewkey(bookingid):
    booking = Booking.query.filter_by(id=bookingid).first()
    if booking:
        return render_template("viewkey.html", current_user=current_user, booking=booking, page="viewkey")
    else:
        flash('Booking does not exist.', category='danger')
        return redirect(url_for('views.bookings'))


# Edit booking page
@views.route('/editbooking/<bookingid>', methods=['GET', 'POST'])
@login_required
def editbooking(bookingid):
    booking = Booking.query.filter_by(id=bookingid).first()
    if not booking:
        flash('Booking does not exist.', category='danger')
        return redirect(url_for('views.bookings'))

    if request.method == 'POST':
        # Get fields from form
        name = request.form.get('name')
        room = request.form.get('room')
        phone = request.form.get('phone')
        oldcode = request.form.get('oldcode')
        currcode = request.form.get('currcode')

        booking.name = name
        booking.room = room
        booking.phone = phone
        booking.old_code = oldcode
        booking.current_code = currcode

        db.session.add(booking)
        db.session.commit()
        flash('Booking updated successfully.', category='success')
        return redirect(url_for('views.bookings'))

    return render_template("editbooking.html", current_user=current_user, page="editbooking", booking=booking)


# Delete booking page
@views.route('/deletebooking/<bookingid>')
@login_required
def deletebooking(bookingid):
    booking = Booking.query.filter_by(id=bookingid).first()
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully.', category='success')
    return redirect(url_for('views.bookings'))


# Rooms page
@views.route('/rooms')
@login_required
def rooms():
    rooms = Room.query.all()
    return render_template("rooms.html", current_user=current_user, page="rooms", rooms=rooms)


# New room page
@views.route('/addroom', methods=['GET', 'POST'])
@login_required
def addroom():
    if request.method == 'POST':
        # Get fields from form
        number = request.form.get('number')
        code = generate_code()

        # Creates new room in the database
        new_room = Room(number=number, code=code)
        db.session.add(new_room)
        new_booking = Booking(name="--- NEW ROOM ---", room=number, current_code=code)
        db.session.add(new_booking)
        db.session.commit()
        flash('New room created successfully.', category='success')
        return redirect(url_for('views.rooms'))

    return render_template("addroom.html", current_user=current_user, page="newroom")


# Edit room page
@views.route('/editroom/<roomid>', methods=['GET', 'POST'])
@login_required
def editroom(roomid):
    room = Room.query.filter_by(id=roomid).first()
    if not room:
        flash('Room does not exist.', category='danger')
        return redirect(url_for('views.rooms'))

    if request.method == 'POST':
        # Get fields from form
        number = request.form.get('number')
        code = request.form.get('code')

        room.number = number
        room.code = code

        db.session.add(room)
        db.session.commit()
        flash('Room updated successfully.', category='success')
        return redirect(url_for('views.rooms'))

    return render_template("editroom.html", current_user=current_user, page="editroom", room=room)


# Delete room page
@views.route('/deleteroom/<roomid>')
@login_required
def deleteroom(roomid):
    room = Room.query.filter_by(id=roomid).first()
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully.', category='success')
    return redirect(url_for('views.rooms'))


# Replace key card page
@views.route('/replacekey', methods=['GET', 'POST'])
@login_required
def replacekey():
    if request.method == 'POST':
        room = request.form.get('room')
        booking = Booking.query.order_by(Booking.id.desc()).filter_by(room=room).first()

        if not booking:
            flash('Booking could not be found.', category='danger')
            return redirect(url_for('views.bookings'))

        name = request.form.get('name').lower()
        phone = request.form.get('phone')

        if booking.phone[-3:3] == phone and name in booking.name.lower():
            flash('Identity verified.', category='success')
            return redirect(url_for('views.viewkey', bookingid=booking.id))
        else:
            flash('Identity could not be verified.', category='danger')
            return redirect(url_for('views.replacekey'))

    return render_template("replacekey.html", current_user=current_user, page="replacekey")


# Key card reader page
@views.route('/reader', methods=['GET', 'POST'])
@login_required
def reader():
    if request.method == 'POST':
        if 'key' not in request.files:
            flash('No key uploaded.', category='danger')
            return redirect(url_for('views.reader'))
        else:
            key = request.files['key'].read()
            key = json.loads(key)
            if key['version'] == 1:
                room_number = key['room']
                code = key['code']
                oldcode = key['previous_code']
                room = Room.query.filter_by(number=room_number).first()

                if room.code == code:
                    flash(f'Valid keycard for room {room_number}.', category='success')
                    return redirect(url_for('views.reader'))
                elif room.code == oldcode:
                    flash(f'Valid keycard for room {room_number}. Code has been changed.', category='secondary')
                    room.code = code
                    db.session.add(room)
                    db.session.commit()
                    return redirect(url_for('views.reader'))
                else:
                    flash(f'Invalid keycard for room {room_number}.', category='danger')
                    return redirect(url_for('views.reader'))
            else:
                flash('Invalid key version.', category='danger')
                return redirect(url_for('views.reader'))

    return render_template("reader.html", current_user=current_user, page="reader")


def error403(e):
    return render_template('403.html', current_user=current_user), 403


def error404(e):
    return render_template('404.html', current_user=current_user), 404


def error500(e):
    return render_template('500.html', current_user=current_user), 500


def generate_code():
    code = ""
    validcodechars = "0123456789abcdef"
    import random
    for i in range(4):
        for j in range(4):
            code += random.choice(validcodechars)
        code += "-" if i != 3 else ""
    return code

# GENERAL
# redirect(url_for('views.page'))
# @login_required
# if current_user.is_authenticated:

# DATABASE
# Table.query.all()
# Table.query.filter_by( <QUERY OPTIONS> ).first()
#   <QUERY OPTIONS> id=123 name='test'
# current_user.linkedtable
# new_record = Record(field=data, field2=data2)
# db.session.add(new_record)
# db.session.commit()

# REQUESTS
# @views.route('/path', methods=['GET', 'POST'])
# if request.method == 'POST':
# request.form.get('input name')
# request.form.getlist('common input name')
