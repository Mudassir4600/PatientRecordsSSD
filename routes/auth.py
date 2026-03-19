from extensions import db, bcrypt, limiter
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User, AuditLog
from datetime import datetime

# Auth blueprint used to handle login, register, logout
auth_bp = Blueprint('auth', __name__)


# Helper function is uded to log important actions for audit trail
def log_action(user_id, action, target=None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        target=target,
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'patient')

        # Basic input validation
        if not full_name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.register'))

        # Used to Check if email already exists or not
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # "never" store plain text, Hash password before storing 
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_pw,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        log_action(new_user.id, 'USER_REGISTERED', target=email)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")  # limit number of login attempts to prevent brute force
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        # to v erify user already exists and password is matcjhed
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'danger')
            log_action(None, 'FAILED_LOGIN_ATTEMPT', target=email)
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()

        log_action(user.id, 'USER_LOGIN', target=email)

        # Redirect to correct dashboard based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'clinician':
            return redirect(url_for('clinician.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'USER_LOGOUT', target=current_user.email)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    # Redirect to role based specific dashboard
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'clinician':
        return redirect(url_for('clinician.dashboard'))
    else:
        return redirect(url_for('patient.dashboard'))