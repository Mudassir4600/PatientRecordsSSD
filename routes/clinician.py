from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

clinician_bp = Blueprint('clinician', __name__)

@clinician_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('clinician/dashboard.html')

@clinician_bp.route('/patients')
@login_required
def patients():
    return render_template('clinician/dashboard.html')

@clinician_bp.route('/appointments')
@login_required
def clinician_appointments():
    return redirect(url_for('appointments.list_appointments'))