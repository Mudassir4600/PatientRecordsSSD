from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('patient/dashboard.html')

@patient_bp.route('/my-records')
@login_required
def my_records():
    return render_template('patient/dashboard.html')

@patient_bp.route('/appointments')
@login_required
def patient_appointments():
    return render_template('patient/dashboard.html')

@patient_bp.route('/prescriptions')
@login_required
def prescriptions():
    return render_template('patient/dashboard.html')

@patient_bp.route('/appointments')
@login_required
def appointments():
    return redirect(url_for('appointments.list_appointments'))