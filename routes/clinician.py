from flask import Blueprint, render_template
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
def appointments():
    return render_template('clinician/dashboard.html')