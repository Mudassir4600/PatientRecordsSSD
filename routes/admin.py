from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, AuditLog
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


# Restrict all admin routes to admin role only
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Gather summary stats for the dashboard
    total_users = User.query.count()
    total_patients = User.query.filter_by(role='patient').count()
    total_clinicians = User.query.filter_by(role='clinician').count()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_patients=total_patients,
                           total_clinicians=total_clinicians,
                           recent_logs=recent_logs)


@admin_bp.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/toggle-user/<int:user_id>')
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent admin from deactivating their own account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    log = AuditLog(
        user_id=current_user.id,
        action=f'USER_{status.upper()}',
        target=user.email,
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    log = AuditLog(
        user_id=current_user.id,
        action='USER_DELETED',
        target=user.email,
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.email} has been deleted.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    # Show all audit logs, most recent first
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    # Get user emails for display
    user_map = {}
    for log in logs:
        if log.user_id and log.user_id not in user_map:
            user = User.query.get(log.user_id)
            user_map[log.user_id] = user.email if user else 'Unknown'

    return render_template('admin/audit_logs.html', logs=logs, user_map=user_map)