# Design Document
**HealthSecure PRS — Patient Record Management System**  
**Module:** COM7033 Secure Software Development  
**Institution:** Leeds Trinity University  
**Author:** Mudassar Ali  
**Date:** March 2026  
**Version:** 1.0

---

## 1. System Architecture

### 1.1 Overview
The HealthSecure PRS follows a modular Model-View-Controller (MVC) architecture implemented using Flask Blueprints. The system separates concerns across distinct layers: routing, business logic, data access, and presentation.

### 1.2 Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│                    (HTML/CSS/JavaScript)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP Requests
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                        │
│                                                               │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
│  │  auth   │  │  admin   │  │ clinician │  │  patient   │  │
│  │ routes  │  │  routes  │  │  routes   │  │  routes    │  │
│  └─────────┘  └──────────┘  └───────────┘  └────────────┘  │
│                                                               │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐                   │
│  │ records │  │appoint-  │  │prescrip-  │                   │
│  │ routes  │  │  ments   │  │  tions    │                   │
│  └─────────┘  └──────────┘  └───────────┘                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  SECURITY LAYER                         │  │
│  │  CSRF │ Rate Limiting │ Auth Required │ Role Required   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────┬────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│   SQLite Database    │    │         MongoDB Database         │
│                      │    │                                  │
│  • Users             │    │  • patient_records collection    │
│  • AuditLogs         │    │  • appointments collection       │
└──────────────────────┘    │  • prescriptions collection      │
                            └─────────────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Web Framework | Flask 3.x | Lightweight, explicit security control |
| Authentication DB | SQLite + SQLAlchemy | ACID compliance for auth data |
| Records DB | MongoDB + PyMongo | Flexible document model for clinical data |
| Password Hashing | Flask-Bcrypt | Purpose-built for password security |
| Session Management | Flask-Login | Secure session handling |
| CSRF Protection | Flask-WTF | Industry standard form protection |
| Rate Limiting | Flask-Limiter | Brute force prevention |
| Input Sanitisation | Bleach | XSS prevention |
| Field Encryption | Cryptography/Fernet | Authenticated symmetric encryption |
| Frontend | Bootstrap 5 + Jinja2 | Responsive, accessible UI |

---

## 2. Database Design

### 2.1 SQLite Schema (Authentication Database)

#### Users Table
```
┌─────────────────────────────────────────────────────────────┐
│                          USERS                               │
├──────────────┬─────────────┬──────────────────────────────  │
│ Field        │ Type        │ Description                     │
├──────────────┼─────────────┼─────────────────────────────── │
│ id           │ INTEGER PK  │ Auto-increment primary key      │
│ full_name    │ VARCHAR     │ User's full name                │
│ email        │ VARCHAR UQ  │ Unique login email              │
│ password_hash│ VARCHAR     │ Bcrypt hashed password          │
│ role         │ VARCHAR     │ admin / clinician / patient     │
│ is_active    │ BOOLEAN     │ Account active status           │
│ created_at   │ DATETIME    │ Account creation timestamp      │
│ last_login   │ DATETIME    │ Last successful login           │
└──────────────┴─────────────┴─────────────────────────────── ┘
```

#### AuditLog Table
```
┌─────────────────────────────────────────────────────────────┐
│                        AUDIT_LOG                             │
├──────────────┬─────────────┬──────────────────────────────  │
│ Field        │ Type        │ Description                     │
├──────────────┼─────────────┼─────────────────────────────── │
│ id           │ INTEGER PK  │ Auto-increment primary key      │
│ user_id      │ INTEGER FK  │ Foreign key to Users table      │
│ action       │ VARCHAR     │ Action performed (e.g. LOGIN)   │
│ target       │ VARCHAR     │ Target of action (e.g. email)   │
│ ip_address   │ VARCHAR     │ IP address of request           │
│ timestamp    │ DATETIME    │ When the action occurred        │
└──────────────┴─────────────┴─────────────────────────────── ┘
```

### 2.2 MongoDB Collections (Patient Records Database)

#### patient_records Collection
```json
{
  "_id": "ObjectId",
  "full_name": "string (encrypted)",
  "age": "integer",
  "sex": "string",
  "blood_pressure": "string",
  "cholesterol": "string",
  "fasting_blood_sugar": "string",
  "resting_ecg": "string",
  "exercise_angina": "string",
  "notes": "string",
  "created_by": "string (email)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "updated_by": "string (email)",
  "is_archived": "boolean"
}
```

#### appointments Collection
```json
{
  "_id": "ObjectId",
  "patient_email": "string",
  "patient_name": "string",
  "clinician_email": "string",
  "clinician_name": "string",
  "date": "string",
  "time": "string",
  "reason": "string",
  "status": "string (pending/confirmed/cancelled)",
  "created_at": "datetime"
}
```

#### prescriptions Collection
```json
{
  "_id": "ObjectId",
  "patient_email": "string",
  "patient_name": "string",
  "clinician_email": "string",
  "clinician_name": "string",
  "medication": "string",
  "dosage": "string",
  "frequency": "string",
  "duration": "string",
  "notes": "string",
  "issued_at": "datetime",
  "is_active": "boolean"
}
```

### 2.3 Database Design Justification

Two databases were chosen deliberately to meet different data requirements:

**SQLite** is used for authentication because user accounts and audit logs require strict relational integrity. Foreign key constraints between Users and AuditLog ensure referential integrity — an audit log entry always relates to a valid user. SQLite's ACID compliance guarantees that login events are recorded atomically.

**MongoDB** is used for patient records because clinical data is inherently variable — different patients may have different sets of clinical measurements, and the schema may evolve as new medical fields are required. The document model allows this flexibility without costly schema migrations.

---

## 3. Security Architecture

### 3.1 Authentication Flow
```
User submits login form
        │
        ▼
Rate limiter checks IP (5/min limit)
        │
        ├── Limit exceeded → 429 Too Many Requests
        │
        ▼
CSRF token validated
        │
        ├── Invalid token → 400 Bad Request
        │
        ▼
Email looked up in SQLite Users table
        │
        ├── Not found → "Invalid email or password"
        │
        ▼
Account active status checked
        │
        ├── Inactive → "Account deactivated"
        │
        ▼
Bcrypt password verification
        │
        ├── Wrong password → Audit log FAILED_LOGIN, redirect
        │
        ▼
Flask-Login session created
        │
        ▼
Audit log USER_LOGIN recorded
        │
        ▼
Role-based redirect (admin/clinician/patient dashboard)
```

### 3.2 Request Authorization Flow
```
Incoming HTTP request
        │
        ▼
@login_required decorator
        │
        ├── Not authenticated → redirect to /auth/login
        │
        ▼
@role_required decorator (where applicable)
        │
        ├── Wrong role → flash error, redirect to own dashboard
        │
        ▼
Route handler executes
        │
        ▼
Action recorded in audit log
        │
        ▼
Response with security headers added
```

### 3.3 Data Protection Design

| Data Category | Protection Method | Justification |
|--------------|------------------|---------------|
| Passwords | Bcrypt hashing | One-way hash prevents recovery |
| Patient names | Fernet encryption | Reversible for display, encrypted at rest |
| Session data | Flask-Login secure cookies | HttpOnly, SameSite flags |
| Form submissions | CSRF tokens | Prevents cross-site request forgery |
| User inputs | Bleach sanitisation | Prevents XSS attacks |
| HTTP responses | Security headers | Prevents clickjacking, MIME sniffing |

---

## 4. Role-Based Access Control Design

### 4.1 Permission Matrix

| Feature | Admin | Clinician | Patient |
|---------|-------|-----------|---------|
| Admin Dashboard | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ |
| Create Patient Records | ✅ | ✅ | ❌ |
| View All Records | ✅ | ✅ | ❌ |
| View Own Record | ✅ | ✅ | ✅ |
| Edit Records | ✅ | ✅ | ❌ |
| Archive Records | ✅ | ❌ | ❌ |
| Book Appointments | ❌ | ❌ | ✅ |
| View All Appointments | ✅ | ✅ | ❌ |
| View Own Appointments | ✅ | ✅ | ✅ |
| Cancel Appointments | ✅ | ❌ | ✅ |
| Issue Prescriptions | ✅ | ✅ | ❌ |
| View All Prescriptions | ✅ | ✅ | ❌ |
| View Own Prescriptions | ✅ | ✅ | ✅ |

### 4.2 Role Decorator Implementation
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

---

## 5. Module Design

### 5.1 Blueprint Structure

| Blueprint | Prefix | Responsibility |
|-----------|--------|---------------|
| auth_bp | /auth | Registration, login, logout |
| admin_bp | /admin | Dashboard, user management, audit logs |
| clinician_bp | /clinician | Clinician dashboard |
| patient_bp | /patient | Patient dashboard |
| records_bp | /records | Patient records CRUD |
| appointments_bp | /appointments | Appointment management |
| prescriptions_bp | /prescriptions | Prescription management |

### 5.2 Key Design Patterns

**Application Factory Pattern**
The `create_app()` function in `app.py` creates and configures the Flask application. This pattern enables testing with different configurations (e.g. in-memory database for tests) without modifying production code.

**Repository Pattern (via Extensions)**
`get_mongo_db()` in `extensions.py` abstracts MongoDB connection management. All routes access MongoDB through this function, making it straightforward to change the connection configuration without modifying route code.

**Decorator Pattern (Security)**
Authentication and authorisation are implemented as Python decorators (`@login_required`, `@admin_required`). This cleanly separates security concerns from business logic and ensures protection cannot be accidentally omitted.

---

## 6. Interface Design

### 6.1 Navigation Structure
```
/ (root)
└── /auth/login
    ├── /auth/register
    ├── /admin/dashboard (admin only)
    │   ├── /admin/manage-users
    │   └── /admin/audit-logs
    ├── /clinician/dashboard (clinician only)
    ├── /patient/dashboard (patient only)
    ├── /records/ (admin + clinician)
    │   ├── /records/add
    │   ├── /records/view/<id>
    │   └── /records/edit/<id>
    ├── /appointments/
    │   ├── /appointments/book
    │   └── /appointments/view/<id>
    └── /prescriptions/
        ├── /prescriptions/add
        └── /prescriptions/view/<id>
```

### 6.2 UI Design Principles
- **Consistency:** All pages use the shared `base.html` template with role-appropriate sidebar navigation
- **Feedback:** Flash messages confirm successful actions and communicate errors clearly
- **Accessibility:** Bootstrap 5 ensures responsive layout across device sizes
- **Security UX:** Error messages never reveal whether an email exists in the system

---

## 7. Deployment Architecture
```
┌─────────────────────────────────────────┐
│           DEVELOPMENT MACHINE            │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │      Python Virtual Environment   │   │
│  │                                   │   │
│  │  Flask App (port 5000)            │   │
│  │  MongoDB Service (port 27017)     │   │
│  │  SQLite File (instance/auth.db)   │   │
│  └──────────────────────────────────┘   │
│                                          │
│  Environment Variables (.env)            │
│  • SECRET_KEY                            │
│  • MONGO_URI                             │
│  • ENCRYPTION_KEY                        │
└─────────────────────────────────────────┘
```