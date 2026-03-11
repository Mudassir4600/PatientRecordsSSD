# HealthSecure PRS — Patient Record Management System
**Module:** COM7033 Secure Software Development  
**Institution:** Leeds Trinity University  
**Developer:** Mudassar Ali  
**Submission Date:** 20 March 2026

---

## Project Overview

HealthSecure PRS is a web-based Patient Record Management System built for a private healthcare provider. The system enables clinicians, patients, and administrative staff to securely store, update, and retrieve patient health records while safeguarding against unauthorised access, data misuse, and regulatory violations.

The system was designed with security as a first-class concern, applying the STRIDE threat modelling framework throughout development and implementing multiple layers of protection to ensure data confidentiality, integrity, and availability.

---

## System Architecture

The application follows a modular Flask blueprint architecture with two interconnected databases:

| Database | Technology | Purpose | Justification |
|----------|-----------|---------|---------------|
| Authentication DB | SQLite + SQLAlchemy | Users, roles, audit logs | Relational structure suits structured auth data |
| Patient Records DB | MongoDB | Records, appointments, prescriptions | Flexible document model suits variable clinical data |

---

## User Roles

| Role | Permissions |
|------|------------|
| **Admin** | Full system access: manage users, create/archive records, view audit logs |
| **Clinician** | View/edit patient records, manage appointments, issue prescriptions |
| **Patient** | View own records, book appointments, view own prescriptions |

---

## Security Features

| Feature | Implementation | STRIDE Threat Addressed |
|---------|---------------|------------------------|
| Password Hashing | Flask-Bcrypt | Spoofing |
| CSRF Protection | Flask-WTF | Tampering |
| Rate Limiting | Flask-Limiter (5/min on login) | Spoofing / DoS |
| Input Sanitisation | Bleach library | Tampering / XSS |
| Field Encryption | Cryptography/Fernet | Information Disclosure |
| Audit Logging | SQLite AuditLog model | Repudiation |
| Role-Based Access | Flask-Login + decorators | Elevation of Privilege |
| Security Headers | X-Frame-Options, CSP, HSTS | Information Disclosure |
| Session Management | Flask-Login secure sessions | Spoofing |

---

## Project Structure
```
PatientRecordsSSD/
├── app.py                  # Application factory, security headers
├── config.py               # Configuration and environment variables
├── extensions.py           # Flask extensions, encryption helpers
├── models.py               # SQLite models: User, AuditLog
├── tests.py                # 18 unit tests across 4 test categories
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (not in version control)
├── routes/
│   ├── auth.py             # Registration, login, logout
│   ├── admin.py            # Admin dashboard, user management
│   ├── clinician.py        # Clinician dashboard
│   ├── patient.py          # Patient dashboard
│   ├── records.py          # Patient records CRUD
│   ├── appointments.py     # Appointment booking and management
│   └── prescriptions.py    # Prescription issuing and management
├── templates/
│   ├── shared/base.html    # Base template with sidebar navigation
│   ├── auth/               # Login and registration templates
│   ├── admin/              # Admin panel templates
│   ├── clinician/          # Clinician templates
│   ├── patient/            # Patient templates
│   ├── records/            # Patient record templates
│   ├── appointments/       # Appointment templates
│   └── prescriptions/      # Prescription templates
└── static/
    ├── css/                # Custom stylesheets
    └── js/                 # Custom JavaScript
```

---

## Installation and Setup

### Prerequisites
- Python 3.8+
- MongoDB (local installation or Atlas)
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/Mudassir4600/PatientRecordsSSD.git
cd PatientRecordsSSD
```

### Step 2 — Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/patient_records
SQLITE_DB=instance/auth.db
ENCRYPTION_KEY=your-fernet-key-here
```

Generate a Fernet encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Step 5 — Start MongoDB
```bash
net start MongoDB  # Windows
```

### Step 6 — Run the Application
```bash
python app.py
```

Visit: `http://127.0.0.1:5000`

---

## Running Tests
```bash
pytest tests.py -v
```

Expected output: **18 passed**

### Test Coverage

| Test Class | Tests | What is Verified |
|-----------|-------|-----------------|
| TestAuthentication | 7 | Registration, login, password hashing, duplicate prevention |
| TestRoleBasedAccess | 4 | Patients/clinicians cannot access admin functions |
| TestSecurity | 3 | Security headers, XSS prevention, session clearing |
| TestDataValidation | 3 | Age validation, empty fields, past date rejection |

---

## STRIDE Threat Model

| Threat | Example | Mitigation Implemented |
|--------|---------|----------------------|
| **Spoofing** | Attacker impersonates a clinician | Bcrypt password hashing, rate limiting |
| **Tampering** | Malicious input in patient records | CSRF tokens, Bleach sanitisation |
| **Repudiation** | User denies accessing a record | Full audit log with timestamps and IP |
| **Information Disclosure** | Patient data leaked | Field encryption, security headers, RBAC |
| **Denial of Service** | Login endpoint flooded | Rate limiting (5 requests/minute) |
| **Elevation of Privilege** | Patient accesses admin panel | Role decorators on every protected route |

---

## Regulatory Compliance

The system design reflects awareness of:
- **UK GDPR** — data minimisation, purpose limitation, right of access
- **Data Protection Act 2018** — lawful basis for processing health data
- **NHS Data Security Standards** — audit trails, access controls
- **Caldicott Principles** — patient confidentiality in clinical systems

---

## Default Test Accounts

After setup, register the following accounts to test all roles:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@health.com | Admin1234! |
| Clinician | clinician@health.com | Clinician1234! |
| Patient | patient@health.com | Patient1234! |

---

## AI Usage Declaration

This assignment used generative AI in the following ways:
brainstorming, planning, feedback.

---

## GitHub Repository

[https://github.com/Mudassir4600/PatientRecordsSSD](https://github.com/Mudassir4600/PatientRecordsSSD)