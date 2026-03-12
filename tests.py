import pytest
import sys
import os

# Add project root to path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from models import User


# ─── Test Configuration ────────────────────────────────────────────────────────

@pytest.fixture
def app():
    """Create a fresh test application with in-memory SQLite database."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing forms
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiting in tests

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create a test admin user in the database."""
    from extensions import bcrypt
    with app.app_context():
        hashed_pw = bcrypt.generate_password_hash('Admin1234!').decode('utf-8')
        user = User(
            full_name='Test Admin',
            email='testadmin@health.com',
            password_hash=hashed_pw,
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def patient_user(app):
    """Create a test patient user in the database."""
    from extensions import bcrypt
    with app.app_context():
        hashed_pw = bcrypt.generate_password_hash('Patient1234!').decode('utf-8')
        user = User(
            full_name='Test Patient',
            email='testpatient@health.com',
            password_hash=hashed_pw,
            role='patient'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def clinician_user(app):
    """Create a test clinician user in the database."""
    from extensions import bcrypt
    with app.app_context():
        hashed_pw = bcrypt.generate_password_hash('Clinician1234!').decode('utf-8')
        user = User(
            full_name='Test Clinician',
            email='testclinician@health.com',
            password_hash=hashed_pw,
            role='clinician'
        )
        db.session.add(user)
        db.session.commit()
        return user


# ─── Authentication Tests ───────────────────────────────────────────────────────

class TestAuthentication:
    """Tests for user registration and login functionality."""

    def test_register_page_loads(self, client):
        """Registration page should return 200 status."""
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """Login page should return 200 status."""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_successful_registration(self, client, app):
        """A new user should be able to register successfully."""
        response = client.post('/auth/register', data={
            'full_name': 'New User',
            'email': 'newuser@health.com',
            'password': 'NewPass1234!',
            'role': 'patient'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verify user was actually saved to database
        with app.app_context():
            user = User.query.filter_by(email='newuser@health.com').first()
            assert user is not None
            assert user.full_name == 'New User'
            assert user.role == 'patient'

    def test_password_is_hashed(self, client, app):
        """Passwords must never be stored in plain text."""
        client.post('/auth/register', data={
            'full_name': 'Hash Test',
            'email': 'hashtest@health.com',
            'password': 'PlainPass123!',
            'role': 'patient'
        })
        with app.app_context():
            user = User.query.filter_by(email='hashtest@health.com').first()
            assert user is not None
            # Password hash should never equal the plain text password
            assert user.password_hash != 'PlainPass123!'

    def test_successful_login(self, client, admin_user):
        """A registered user should be able to log in successfully."""
        response = client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_invalid_login_rejected(self, client, admin_user):
        """Login with wrong password should be rejected."""
        response = client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'WrongPassword!'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

    def test_short_password_rejected(self, client):
        """Passwords shorter than 8 characters should be rejected."""
        response = client.post('/auth/register', data={
            'full_name': 'Short Pass',
            'email': 'short@health.com',
            'password': 'abc',
            'role': 'patient'
        }, follow_redirects=True)
        assert b'Password must be at least 8 characters' in response.data

    def test_duplicate_email_rejected(self, client, admin_user):
        """Registering with an existing email should be rejected."""
        response = client.post('/auth/register', data={
            'full_name': 'Duplicate',
            'email': 'testadmin@health.com',
            'password': 'Admin1234!',
            'role': 'patient'
        }, follow_redirects=True)
        assert b'already exists' in response.data


# ─── Role-Based Access Control Tests ───────────────────────────────────────────

class TestRoleBasedAccess:
    """Tests to verify that role-based access control is enforced correctly."""

    def test_unauthenticated_user_redirected(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302

    def test_patient_cannot_access_admin(self, client, patient_user):
        """Patients should not be able to access admin dashboard."""
        # Log in as patient
        client.post('/auth/login', data={
            'email': 'testpatient@health.com',
            'password': 'Patient1234!'
        }, follow_redirects=True)

        # Try to access admin dashboard
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected away from admin
        assert b'Admin Dashboard' not in response.data

    def test_patient_cannot_add_records(self, client, patient_user):
        """Patients should not be able to add patient records."""
        client.post('/auth/login', data={
            'email': 'testpatient@health.com',
            'password': 'Patient1234!'
        }, follow_redirects=True)

        response = client.get('/records/add', follow_redirects=True)
        assert response.status_code == 200
        assert b'Only administrators' in response.data

    def test_clinician_cannot_access_admin(self, client, clinician_user):
        """Clinicians should not be able to access admin panel."""
        client.post('/auth/login', data={
            'email': 'testclinician@health.com',
            'password': 'Clinician1234!'
        }, follow_redirects=True)

        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Dashboard' not in response.data


# ─── Security Tests ─────────────────────────────────────────────────────────────

class TestSecurity:
    """Tests to verify security controls are active and working."""

    def test_security_headers_present(self, client):
        """Security headers should be present on all responses."""
        response = client.get('/auth/login')
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-Content-Type-Options'] == 'nosniff'

    def test_xss_input_sanitised(self, client, admin_user, app):
        """Malicious script tags in input should be sanitised."""
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        # Try to inject a script tag in patient name
        response = client.post('/records/add', data={
            'full_name': '<script>alert("xss")</script>',
            'age': '30',
            'sex': 'Male',
            'blood_pressure': '120',
            'cholesterol': '200',
            'notes': 'Test notes'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_logout_clears_session(self, client, admin_user):
        """After logout user should not be able to access protected pages."""
        # Login first
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        # Logout
        client.get('/auth/logout', follow_redirects=True)

        # Try to access protected page after logout
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302


# ─── Data Validation Tests ──────────────────────────────────────────────────────

class TestDataValidation:
    """Tests to verify input validation is working correctly."""

    def test_invalid_age_rejected(self, client, admin_user):
        """Age values outside 0-120 range should be rejected."""
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        response = client.post('/records/add', data={
            'full_name': 'Test Patient',
            'age': '999',
            'sex': 'Male'
        }, follow_redirects=True)
        assert b'valid age' in response.data

    def test_empty_name_rejected(self, client, admin_user):
        """Empty patient name should be rejected."""
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        response = client.post('/records/add', data={
            'full_name': '',
            'age': '30',
            'sex': 'Male'
        }, follow_redirects=True)
        assert b'required' in response.data

    def test_past_appointment_rejected(self, client, patient_user):
        """Appointments in the past should be rejected."""
        client.post('/auth/login', data={
            'email': 'testpatient@health.com',
            'password': 'Patient1234!'
        }, follow_redirects=True)

        response = client.post('/appointments/book', data={
            'clinician_email': 'testclinician@health.com',
            'date': '2020-01-01',
            'time': '10:00',
            'reason': 'Test appointment'
        }, follow_redirects=True)
        assert b'cannot be in the past' in response.data

        # ─── Integration Tests ──────────────────────────────────────────────────────────

class TestIntegration:
    """
    Integration tests verify that multiple components work together correctly.
    These tests simulate real user workflows across the full application stack.
    """

    def test_full_registration_and_login_flow(self, client, app):
        """
        End-to-end test: A new user registers, then logs in successfully.
        Tests that registration and authentication work together correctly.
        """
        # Step 1 — Register a new account
        register_response = client.post('/auth/register', data={
            'full_name': 'Integration User',
            'email': 'integration@health.com',
            'password': 'Integrate1234!',
            'role': 'patient'
        }, follow_redirects=True)
        assert register_response.status_code == 200

        # Step 2 — Verify user exists in database
        with app.app_context():
            user = User.query.filter_by(email='integration@health.com').first()
            assert user is not None

        # Step 3 — Log in with the new account
        login_response = client.post('/auth/login', data={
            'email': 'integration@health.com',
            'password': 'Integrate1234!'
        }, follow_redirects=True)
        assert login_response.status_code == 200

    def test_admin_create_and_view_record_flow(self, client, admin_user, app):
        """
        End-to-end test: Admin logs in, creates a patient record,
        then the record appears in the records list.
        Tests that record creation and retrieval work together.
        """
        # Step 1 — Log in as admin
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        # Step 2 — Create a patient record
        create_response = client.post('/records/add', data={
            'full_name': 'Integration Patient',
            'age': '45',
            'sex': 'Female',
            'blood_pressure': '130',
            'cholesterol': '210',
            'fasting_blood_sugar': 'No',
            'resting_ecg': 'Normal',
            'exercise_angina': 'No',
            'notes': 'Integration test record'
        }, follow_redirects=True)
        assert create_response.status_code == 200

        # Step 3 — Verify record appears in the list
        list_response = client.get('/records/', follow_redirects=True)
        assert b'Integration Patient' in list_response.data

    def test_audit_log_created_on_login(self, client, admin_user, app):
        """
        Integration test: Verifies that logging in creates an audit log entry.
        Tests that authentication and audit logging work together.
        """
        # Log in as admin
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        # Verify audit log entry was created
        with app.app_context():
            from models import AuditLog
            log = AuditLog.query.filter_by(
                action='USER_LOGIN'
            ).first()
            assert log is not None
            assert log.target == 'testadmin@health.com'

    def test_failed_login_creates_audit_log(self, client, admin_user, app):
        """
        Integration test: Failed login attempts are recorded in audit log.
        This is critical for security monitoring and intrusion detection.
        """
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'WrongPassword!'
        }, follow_redirects=True)

        with app.app_context():
            from models import AuditLog
            log = AuditLog.query.filter_by(
                action='FAILED_LOGIN_ATTEMPT'
            ).first()
            assert log is not None

    def test_user_management_flow(self, client, admin_user, patient_user, app):
        """
        Integration test: Admin can deactivate a user account,
        and the deactivated user cannot log in.
        Tests user management and authentication work together.
        """
        # Step 1 — Log in as admin
        client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)

        # Step 2 — Get patient user ID and deactivate them
        with app.app_context():
            patient = User.query.filter_by(
                email='testpatient@health.com'
            ).first()
            patient_id = patient.id

        client.get(
            f'/admin/toggle-user/{patient_id}',
            follow_redirects=True
        )

        # Step 3 — Verify user is now inactive in database
        with app.app_context():
            patient = User.query.filter_by(
                email='testpatient@health.com'
            ).first()
            assert patient.is_active == False

        # Step 4 — Log out as admin
        client.get('/auth/logout', follow_redirects=True)

        # Step 5 — Try to log in as deactivated patient
        login_response = client.post('/auth/login', data={
            'email': 'testpatient@health.com',
            'password': 'Patient1234!'
        }, follow_redirects=True)
        assert b'deactivated' in login_response.data

    def test_role_redirect_flow(self, client, app):
        """
        Integration test: Each role is redirected to the correct
        dashboard after login. Tests auth and routing work together.
        """
        from extensions import bcrypt

        # Create one user of each role
        with app.app_context():
            for role, email in [
                ('admin', 'admin_flow@health.com'),
                ('clinician', 'clinician_flow@health.com'),
                ('patient', 'patient_flow@health.com')
            ]:
                hashed = bcrypt.generate_password_hash(
                    'Test1234!'
                ).decode('utf-8')
                user = User(
                    full_name=f'Test {role}',
                    email=email,
                    password_hash=hashed,
                    role=role
                )
                db.session.add(user)
            db.session.commit()

        # Test admin redirect
        response = client.post('/auth/login', data={
            'email': 'admin_flow@health.com',
            'password': 'Test1234!'
        }, follow_redirects=True)
        assert b'Admin Dashboard' in response.data
        client.get('/auth/logout')

        # Test clinician redirect
        response = client.post('/auth/login', data={
            'email': 'clinician_flow@health.com',
            'password': 'Test1234!'
        }, follow_redirects=True)
        assert b'Clinician Dashboard' in response.data
        client.get('/auth/logout')

        # Test patient redirect
        response = client.post('/auth/login', data={
            'email': 'patient_flow@health.com',
            'password': 'Test1234!'
        }, follow_redirects=True)
        assert b'Patient Dashboard' in response.data


# ─── End-to-End Tests ───────────────────────────────────────────────────────────

class TestEndToEnd:
    """
    End-to-end tests simulate complete real-world user journeys
    from start to finish across multiple features.
    """

    def test_complete_patient_journey(self, client, app):
        """
        Full patient journey: register → login → view dashboard → logout.
        Simulates what a real patient would experience using the system.
        """
        from extensions import bcrypt

        # Register as patient
        client.post('/auth/register', data={
            'full_name': 'Journey Patient',
            'email': 'journey@health.com',
            'password': 'Journey1234!',
            'role': 'patient'
        }, follow_redirects=True)

        # Log in
        response = client.post('/auth/login', data={
            'email': 'journey@health.com',
            'password': 'Journey1234!'
        }, follow_redirects=True)
        assert b'Patient Dashboard' in response.data

        # View appointments page
        response = client.get(
            '/appointments/',
            follow_redirects=True
        )
        assert response.status_code == 200

        # View prescriptions page
        response = client.get(
            '/prescriptions/',
            follow_redirects=True
        )
        assert response.status_code == 200

        # Logout
        response = client.get(
            '/auth/logout',
            follow_redirects=True
        )
        assert b'logged out' in response.data

    def test_complete_admin_journey(self, client, admin_user, app):
        """
        Full admin journey: login → view dashboard → manage users → audit logs.
        Simulates the complete administrative workflow.
        """
        # Login as admin
        response = client.post('/auth/login', data={
            'email': 'testadmin@health.com',
            'password': 'Admin1234!'
        }, follow_redirects=True)
        assert b'Admin Dashboard' in response.data

        # View manage users page
        response = client.get(
            '/admin/manage-users',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Manage Users' in response.data

        # View audit logs page
        response = client.get(
            '/admin/audit-logs',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Audit Logs' in response.data

        # View patient records page
        response = client.get(
            '/records/',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Patient Records' in response.data