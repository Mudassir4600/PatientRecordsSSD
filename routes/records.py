import bleach
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import get_mongo_db
from models import AuditLog, db
from datetime import datetime
from bson import ObjectId

records_bp = Blueprint('records', __name__)


# Used as Helper to log actions into SQLite audit trail
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


# All patient records can be viewed only by admin and clinician
@records_bp.route('/')
@login_required
def list_records():
    if current_user.role not in ['admin', 'clinician']:
        flash('You do not have permission to view all records.', 'danger')
        return redirect(url_for('auth.dashboard'))

    mongo = get_mongo_db()
    # Only show active/non archived records
    records = list(mongo.patient_records.find({'status': {'$ne': 'archived'}}))
    return render_template('records/list_records.html', records=records)


# Add a new patient record access only to admins
@records_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if current_user.role != 'admin':
        flash('Only administrators can add patient records.', 'danger')
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        # Collect and sanitise all form fields
        # Sanitise inputs to prevent XSS attacks e.g (STRIDE: Tampering)
        full_name = bleach.clean(request.form.get('full_name', '').strip())
        age = request.form.get('age', '').strip()
        sex = request.form.get('sex', '').strip()
        blood_pressure = request.form.get('blood_pressure', '').strip()
        cholesterol = request.form.get('cholesterol', '').strip()
        fasting_blood_sugar = request.form.get('fasting_blood_sugar', '').strip()
        resting_ecg = request.form.get('resting_ecg', '').strip()
        exercise_angina = request.form.get('exercise_angina', '').strip()
        # Sanitise inputs to prevent XSS attacks (STRIDE: Tampering)
        notes = bleach.clean(request.form.get('notes', '').strip())

        # Basic validation - required fields must not be empty
        if not full_name or not age or not sex:
            flash('Full name, age, and sex are required fields.', 'danger')
            return redirect(url_for('records.add_record'))

        # Validating to see if age is a sensible number
        try:
            age = int(age)
            if age < 0 or age > 120:
                raise ValueError
        except ValueError:
            flash('Please enter a valid age between 0 and 120.', 'danger')
            return redirect(url_for('records.add_record'))

        # Build the patient record document for MongoDB
        record = {
            'full_name': full_name,
            'age': age,
            'sex': sex,
            'blood_pressure': blood_pressure,
            'cholesterol': cholesterol,
            'fasting_blood_sugar': fasting_blood_sugar,
            'resting_ecg': resting_ecg,
            'exercise_angina': exercise_angina,
            'notes': notes,
            'status': 'active',
            'created_by': current_user.email,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        mongo = get_mongo_db()
        result = mongo.patient_records.insert_one(record)

        log_action('RECORD_CREATED', target=full_name)
        flash(f'Patient record for {full_name} created successfully.', 'success')
        return redirect(url_for('records.list_records'))

    return render_template('records/add_record.html')


# View a single patient record
@records_bp.route('/view/<record_id>')
@login_required
def view_record(record_id):
    mongo = get_mongo_db()

    try:
        record = mongo.patient_records.find_one({'_id': ObjectId(record_id)})
    except Exception:
        flash('Invalid record ID.', 'danger')
        return redirect(url_for('auth.dashboard'))

    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('auth.dashboard'))

    # Patients can only view their own record
    if current_user.role == 'patient':
        if record.get('email') != current_user.email:
            flash('You can only view your own records.', 'danger')
            return redirect(url_for('patient.dashboard'))

    log_action('RECORD_VIEWED', target=str(record_id))
    return render_template('records/view_record.html', record=record)


# Admin and clinician can aedit a patient record
@records_bp.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    if current_user.role not in ['admin', 'clinician']:
        flash('You do not have permission to edit records.', 'danger')
        return redirect(url_for('auth.dashboard'))

    mongo = get_mongo_db()

    try:
        record = mongo.patient_records.find_one({'_id': ObjectId(record_id)})
    except Exception:
        flash('Invalid record ID.', 'danger')
        return redirect(url_for('records.list_records'))

    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('records.list_records'))

    if request.method == 'POST':
        # Build update document with sanitised inputs
        # Sanitise notes input to prevent XSS attacks
        notes = bleach.clean(request.form.get('notes', '').strip())

        # Building updated document with sanitised inputs
        updated_data = {
            'blood_pressure': request.form.get('blood_pressure', '').strip(),
            'cholesterol': request.form.get('cholesterol', '').strip(),
            'fasting_blood_sugar': request.form.get('fasting_blood_sugar', '').strip(),
            'resting_ecg': request.form.get('resting_ecg', '').strip(),
            'exercise_angina': request.form.get('exercise_angina', '').strip(),
            'notes': notes,
            'updated_at': datetime.utcnow(),
            'updated_by': current_user.email
        }

        mongo.patient_records.update_one(
            {'_id': ObjectId(record_id)},
            {'$set': updated_data}
        )

        log_action('RECORD_UPDATED', target=str(record_id))
        flash('Patient record updated successfully.', 'success')
        return redirect(url_for('records.view_record', record_id=record_id))

    return render_template('records/edit_record.html', record=record)


# Archive a record, admin access only, soft delete i-e data is preserved
@records_bp.route('/archive/<record_id>')
@login_required
def archive_record(record_id):
    if current_user.role != 'admin':
        flash('Only administrators can archive records.', 'danger')
        return redirect(url_for('auth.dashboard'))

    mongo = get_mongo_db()

    try:
        mongo.patient_records.update_one(
            {'_id': ObjectId(record_id)},
            {'$set': {'status': 'archived', 'archived_at': datetime.utcnow(),
                      'archived_by': current_user.email}}
        )
    except Exception:
        flash('Could not archive record.', 'danger')
        return redirect(url_for('records.list_records'))

    log_action('RECORD_ARCHIVED', target=str(record_id))
    flash('Record archived successfully.', 'success')
    return redirect(url_for('records.list_records'))