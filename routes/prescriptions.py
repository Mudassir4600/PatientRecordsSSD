from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import get_mongo_db
from models import AuditLog, User, db
from datetime import datetime
from bson import ObjectId

prescriptions_bp = Blueprint('prescriptions', __name__)


# Helper to record every prescription action in the audit trail
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


# List prescriptions filtered by role
@prescriptions_bp.route('/')
@login_required
def list_prescriptions():
    mongo = get_mongo_db()

    if current_user.role == 'admin':
        # Admin sees all prescriptions
        prescriptions = list(mongo.prescriptions.find().sort('issued_date', -1))

    elif current_user.role == 'clinician':
        # Clinician sees only prescriptions they issued
        prescriptions = list(mongo.prescriptions.find(
            {'clinician_email': current_user.email}
        ).sort('issued_date', -1))

    else:
        # Patient sees only their own prescriptions
        prescriptions = list(mongo.prescriptions.find(
            {'patient_email': current_user.email}
        ).sort('issued_date', -1))

    return render_template('prescriptions/list_prescriptions.html',
                           prescriptions=prescriptions)


# Issue a new prescription — clinicians only
@prescriptions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_prescription():
    if current_user.role not in ['admin', 'clinician']:
        flash('Only clinicians can issue prescriptions.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    # Get list of patients for the dropdown
    patients = User.query.filter_by(role='patient', is_active=True).all()

    if request.method == 'POST':
        patient_email = request.form.get('patient_email', '').strip()
        medication = request.form.get('medication', '').strip()
        dosage = request.form.get('dosage', '').strip()
        frequency = request.form.get('frequency', '').strip()
        duration = request.form.get('duration', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate required fields
        if not patient_email or not medication or not dosage or not frequency:
            flash('Patient, medication, dosage and frequency are required.', 'danger')
            return redirect(url_for('prescriptions.add_prescription'))

        # Get patient name for the record
        patient = User.query.filter_by(email=patient_email).first()
        patient_name = patient.full_name if patient else patient_email

        # Build prescription document for MongoDB
        prescription = {
            'patient_email': patient_email,
            'patient_name': patient_name,
            'clinician_email': current_user.email,
            'clinician_name': current_user.full_name,
            'medication': medication,
            'dosage': dosage,
            'frequency': frequency,
            'duration': duration,
            'notes': notes,
            'status': 'active',
            'issued_date': datetime.utcnow(),
            'created_by': current_user.email
        }

        mongo = get_mongo_db()
        mongo.prescriptions.insert_one(prescription)

        log_action('PRESCRIPTION_ISSUED',
                   target=f'{medication} for {patient_name}')
        flash(f'Prescription for {patient_name} issued successfully.', 'success')
        return redirect(url_for('prescriptions.list_prescriptions'))

    return render_template('prescriptions/add_prescription.html',
                           patients=patients)


# View a single prescription
@prescriptions_bp.route('/view/<prescription_id>')
@login_required
def view_prescription(prescription_id):
    mongo = get_mongo_db()

    try:
        prescription = mongo.prescriptions.find_one(
            {'_id': ObjectId(prescription_id)}
        )
    except Exception:
        flash('Invalid prescription ID.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    if not prescription:
        flash('Prescription not found.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    # Patients can only view their own prescriptions
    if current_user.role == 'patient':
        if prescription.get('patient_email') != current_user.email:
            flash('Access denied.', 'danger')
            return redirect(url_for('prescriptions.list_prescriptions'))

    log_action('PRESCRIPTION_VIEWED', target=str(prescription_id))
    return render_template('prescriptions/view_prescription.html',
                           prescription=prescription)


# Mark prescription as inactive — clinician or admin only
@prescriptions_bp.route('/deactivate/<prescription_id>')
@login_required
def deactivate_prescription(prescription_id):
    if current_user.role not in ['admin', 'clinician']:
        flash('Access denied.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    mongo = get_mongo_db()

    try:
        mongo.prescriptions.update_one(
            {'_id': ObjectId(prescription_id)},
            {'$set': {
                'status': 'inactive',
                'deactivated_at': datetime.utcnow(),
                'deactivated_by': current_user.email
            }}
        )
    except Exception:
        flash('Could not update prescription.', 'danger')
        return redirect(url_for('prescriptions.list_prescriptions'))

    log_action('PRESCRIPTION_DEACTIVATED', target=str(prescription_id))
    flash('Prescription marked as inactive.', 'success')
    return redirect(url_for('prescriptions.list_prescriptions'))