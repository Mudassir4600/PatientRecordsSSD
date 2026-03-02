from flask import Blueprint, render_template
from flask_login import login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage-users')
@login_required
def manage_users():
    return render_template('admin/dashboard.html')

@admin_bp.route('/audit-logs')
@login_required
def audit_logs():
    return render_template('admin/dashboard.html')