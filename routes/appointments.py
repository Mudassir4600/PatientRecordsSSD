from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import get_mongo_db
from models import AuditLog, db
from datetime import datetime
from bson import ObjectId

appointments_bp = Blueprint('appointments', __name__)


# Helps to record every appointment action in the audit trail
def log_action(action, target=None):
    entry = AuditLog(
        user_id=current_user.id,
        action=action,
        target=target,
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()


# List appointments, filtered by role
@appointments_bp.route('/')
@login_required
def list_appointments():
    mongo = get_mongo_db()

    if current_user.role == 'admin':
        # Admin sees all appointments
        appointments = list(mongo.appointments.find().sort('date', 1))

    elif current_user.role == 'clinician':
        # Clinician sees only their assigned appointments
        appointments = list(mongo.appointments.find(
            {'clinician_email': current_user.email}
        ).sort('date', 1))

    else:
        # Patient sees only their own appointments
        appointments = list(mongo.appointments.find(
            {'patient_email': current_user.email}
        ).sort('date', 1))

    return render_template('appointments/list_appointments.html',
                           appointments=appointments)


# Booking a new appointment for patients and admins
@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role == 'clinician':
        flash('Clinicians cannot book appointments.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    mongo = get_mongo_db()

    # Get list of clinicians for the dropdown
    from models import User
    clinicians = User.query.filter_by(role='clinician', is_active=True).all()

    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        clinician_email = request.form.get('clinician_email', '').strip()
        reason = request.form.get('reason', '').strip()

        # Validate all required fields are present
        if not date_str or not time_str or not clinician_email or not reason:
            flash('All fields are required.', 'danger')
            return redirect(url_for('appointments.book_appointment'))

        # Validate date is not in the past
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
            if appointment_date.date() < datetime.utcnow().date():
                flash('Appointment date cannot be in the past.', 'danger')
                return redirect(url_for('appointments.book_appointment'))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('appointments.book_appointment'))

        # Build appointment document
        appointment = {
            'patient_email': current_user.email,
            'patient_name': current_user.full_name,
            'clinician_email': clinician_email,
            'date': date_str,
            'time': time_str,
            'reason': reason,
            'status': 'scheduled',
            'created_at': datetime.utcnow(),
            'created_by': current_user.email,
            'notes': ''
        }

        mongo.appointments.insert_one(appointment)
        log_action('APPOINTMENT_BOOKED', target=f'{date_str} {time_str}')
        flash('Appointment booked successfully.', 'success')
        return redirect(url_for('appointments.list_appointments'))

    return render_template('appointments/book_appointment.html',
                       clinicians=clinicians,
                       now=datetime.utcnow().strftime('%Y-%m-%d'))


# Viewing a single appointment
@appointments_bp.route('/view/<appointment_id>')
@login_required
def view_appointment(appointment_id):
    mongo = get_mongo_db()

    try:
        appointment = mongo.appointments.find_one(
            {'_id': ObjectId(appointment_id)}
        )
    except Exception:
        flash('Invalid appointment ID.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    if not appointment:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    # Patients can only view their own appointments
    if current_user.role == 'patient':
        if appointment.get('patient_email') != current_user.email:
            flash('Access denied.', 'danger')
            return redirect(url_for('appointments.list_appointments'))

    log_action('APPOINTMENT_VIEWED', target=str(appointment_id))
    return render_template('appointments/view_appointment.html',
                           appointment=appointment)


# Update appointment status for clinician and admin only
@appointments_bp.route('/update-status/<appointment_id>', methods=['POST'])
@login_required
def update_status(appointment_id):
    if current_user.role == 'patient':
        flash('Patients cannot update appointment status.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    mongo = get_mongo_db()
    new_status = request.form.get('status', '').strip()
    notes = request.form.get('notes', '').strip()

    valid_statuses = ['scheduled', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    try:
        mongo.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {
                'status': new_status,
                'notes': notes,
                'updated_at': datetime.utcnow(),
                'updated_by': current_user.email
            }}
        )
    except Exception:
        flash('Could not update appointment.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    log_action('APPOINTMENT_STATUS_UPDATED',
               target=f'{appointment_id} -> {new_status}')
    flash('Appointment status updated.', 'success')
    return redirect(url_for('appointments.view_appointment',
                            appointment_id=appointment_id))


# Cancelling appointment which means patient can cancel their own appointments
@appointments_bp.route('/cancel/<appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    mongo = get_mongo_db()

    try:
        appointment = mongo.appointments.find_one(
            {'_id': ObjectId(appointment_id)}
        )
    except Exception:
        flash('Invalid appointment.', 'danger')
        return redirect(url_for('appointments.list_appointments'))

    # Only the patient booking it or admin can cancel appointment    if current_user.role == 'patient':
        if appointment.get('patient_email') != current_user.email:
            flash('You can only cancel your own appointments.', 'danger')
            return redirect(url_for('appointments.list_appointments'))

    mongo.appointments.update_one(
        {'_id': ObjectId(appointment_id)},
        {'$set': {
            'status': 'cancelled',
            'updated_at': datetime.utcnow(),
            'cancelled_by': current_user.email
        }}
    )

    log_action('APPOINTMENT_CANCELLED', target=str(appointment_id))
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('appointments.list_appointments'))