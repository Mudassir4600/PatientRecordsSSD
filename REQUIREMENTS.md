# Requirements Specification
**HealthSecure PRS — Patient Record Management System**  
**Module:** COM7033 Secure Software Development  
**Institution:** Leeds Trinity University  
**Author:** Mudassar Ali  
**Date:** March 2026  
**Version:** 1.0

---

## 1. Introduction

### 1.1 Purpose
This document defines the functional, non-functional, and security requirements for the HealthSecure Patient Record Management System (PRS). It serves as the foundation for all design, implementation, and testing decisions made throughout the Secure Software Development Life Cycle (SSDLC).

### 1.2 Scope
The system provides a secure, web-based platform for a private healthcare provider to manage patient health records, appointments, and prescriptions. The system must enforce strict access controls, maintain comprehensive audit trails, and protect sensitive patient data in compliance with UK GDPR and NHS data security standards.

### 1.3 Stakeholders

| Stakeholder | Role | Key Concerns |
|-------------|------|-------------|
| Admin Staff | System administration | User management, audit visibility |
| Clinicians | Healthcare delivery | Record access, prescription management |
| Patients | Healthcare recipients | Privacy, access to own records |
| Healthcare Provider | System owner | Compliance, data security |
| Information Governance Team | Compliance | GDPR, Data Protection Act 2018 |

### 1.4 Definitions

| Term | Definition |
|------|-----------|
| PRS | Patient Record System |
| RBAC | Role-Based Access Control |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege |
| PHI | Protected Health Information |
| SSDLC | Secure Software Development Life Cycle |

---

## 2. Functional Requirements

### 2.1 Authentication and User Management

| ID | Requirement | Priority |
|----|-------------|---------|
| FR-01 | The system shall allow users to register with full name, email, password, and role | Must Have |
| FR-02 | The system shall authenticate users via email and password | Must Have |
| FR-03 | The system shall redirect users to role-appropriate dashboards upon login | Must Have |
| FR-04 | The system shall allow administrators to activate and deactivate user accounts | Must Have |
| FR-05 | The system shall prevent deactivated users from logging in | Must Have |
| FR-06 | The system shall allow users to log out and terminate their session | Must Have |
| FR-07 | The system shall support three distinct user roles: Admin, Clinician, Patient | Must Have |

### 2.2 Patient Records

| ID | Requirement | Priority |
|----|-------------|---------|
| FR-08 | The system shall allow administrators and clinicians to create patient health records | Must Have |
| FR-09 | The system shall store clinical data including blood pressure, cholesterol, ECG results | Must Have |
| FR-10 | The system shall allow authorised users to view patient records | Must Have |
| FR-11 | The system shall allow authorised users to edit existing patient records | Must Have |
| FR-12 | The system shall support soft deletion (archiving) of patient records | Must Have |
| FR-13 | The system shall allow patients to view only their own records | Must Have |
| FR-14 | The system shall store patient records in MongoDB with flexible document structure | Should Have |

### 2.3 Appointments

| ID | Requirement | Priority |
|----|-------------|---------|
| FR-15 | The system shall allow patients to book appointments with clinicians | Must Have |
| FR-16 | The system shall prevent booking of appointments with past dates | Must Have |
| FR-17 | The system shall allow patients to cancel their own appointments | Must Have |
| FR-18 | The system shall allow clinicians to update appointment status | Must Have |
| FR-19 | The system shall display appointments filtered by user role | Must Have |

### 2.4 Prescriptions

| ID | Requirement | Priority |
|----|-------------|---------|
| FR-20 | The system shall allow clinicians and admins to issue prescriptions | Must Have |
| FR-21 | The system shall allow patients to view their own prescriptions | Must Have |
| FR-22 | The system shall allow clinicians to deactivate prescriptions | Must Have |
| FR-23 | The system shall record prescribing clinician and issue date | Must Have |

### 2.5 Audit Logging

| ID | Requirement | Priority |
|----|-------------|---------|
| FR-24 | The system shall log all login and logout events | Must Have |
| FR-25 | The system shall log all failed login attempts | Must Have |
| FR-26 | The system shall log all patient record access and modifications | Must Have |
| FR-27 | The system shall log all user management actions | Must Have |
| FR-28 | The system shall record timestamp and IP address for each audit event | Must Have |
| FR-29 | The system shall allow administrators to view the full audit log | Must Have |

---

## 3. Non-Functional Requirements

### 3.1 Security Requirements

| ID | Requirement | STRIDE Category |
|----|-------------|----------------|
| NFR-01 | Passwords shall be hashed using Bcrypt before storage | Spoofing |
| NFR-02 | All forms shall include CSRF tokens | Tampering |
| NFR-03 | Login endpoint shall be rate limited to 5 requests per minute per IP | Spoofing / DoS |
| NFR-04 | All user inputs shall be sanitised using Bleach before storage | Tampering |
| NFR-05 | Sensitive patient fields shall be encrypted using Fernet symmetric encryption | Information Disclosure |
| NFR-06 | All responses shall include security headers (X-Frame-Options, CSP, HSTS) | Information Disclosure |
| NFR-07 | Session cookies shall be HttpOnly and SameSite | Spoofing |
| NFR-08 | All protected routes shall require authentication | Elevation of Privilege |
| NFR-09 | All role-restricted routes shall verify user role before granting access | Elevation of Privilege |

### 3.2 Performance Requirements

| ID | Requirement |
|----|-------------|
| NFR-10 | Page load time shall not exceed 3 seconds under normal conditions |
| NFR-11 | The system shall support at least 50 concurrent users |
| NFR-12 | Database queries shall complete within 500ms |

### 3.3 Usability Requirements

| ID | Requirement |
|----|-------------|
| NFR-13 | The system shall provide clear error messages for invalid inputs |
| NFR-14 | The system shall provide role-appropriate navigation menus |
| NFR-15 | The system shall display confirmation messages for successful actions |

### 3.4 Reliability Requirements

| ID | Requirement |
|----|-------------|
| NFR-16 | The system shall use local MongoDB to ensure database availability |
| NFR-17 | The system shall gracefully handle database connection errors |
| NFR-18 | The system shall preserve data integrity through atomic transactions |

### 3.5 Compliance Requirements

| ID | Requirement | Regulation |
|----|-------------|-----------|
| NFR-19 | The system shall implement access controls aligned with data minimisation | UK GDPR Article 5 |
| NFR-20 | The system shall maintain audit logs for accountability | UK GDPR Article 5(f) |
| NFR-21 | Patient data shall be encrypted at rest | NHS Data Security Standard |
| NFR-22 | Users shall only access data necessary for their role | Caldicott Principle 3 |

---

## 4. Security Requirements (STRIDE Analysis)

### 4.1 Threat Identification and Mitigations

#### Spoofing
- **Threat:** An attacker impersonates a legitimate clinician to access patient records
- **Mitigation:** Bcrypt password hashing, rate limiting on login, session management via Flask-Login
- **Implemented:**  FR-02, NFR-01, NFR-03

#### Tampering
- **Threat:** An attacker modifies patient records or intercepts form submissions
- **Mitigation:** CSRF tokens on all forms, Bleach input sanitisation, MongoDB parameterised queries
- **Implemented:**  NFR-02, NFR-04

#### Repudiation
- **Threat:** A user denies accessing or modifying a patient record
- **Mitigation:** Comprehensive audit logging with timestamps, user ID, and IP address
- **Implemented:**  FR-24 through FR-29

#### Information Disclosure
- **Threat:** Patient data is exposed through database breach or response headers
- **Mitigation:** Fernet field encryption, security headers, role-based access control
- **Implemented:**  NFR-05, NFR-06, NFR-09

#### Denial of Service
- **Threat:** Login endpoint is flooded with requests to lock out legitimate users
- **Mitigation:** Rate limiting (5 requests per minute per IP) via Flask-Limiter
- **Implemented:**  NFR-03

#### Elevation of Privilege
- **Threat:** A patient account accesses admin or clinician functionality
- **Mitigation:** Role decorators on every protected route, login required on all non-public routes
- **Implemented:**  NFR-08, NFR-09

---

## 5. Constraints and Assumptions

### 5.1 Technical Constraints
- The system is developed using Python 3.8+ and Flask framework
- SQLite is used for authentication data; MongoDB for patient records
- The system runs on Windows, macOS, or Linux
- Internet access is required for CDN-hosted frontend libraries

### 5.2 Business Constraints
- The system must comply with UK GDPR and Data Protection Act 2018
- Patient data must never be shared with unauthorised parties
- All access to patient records must be logged

### 5.3 Assumptions
- Users have access to a modern web browser
- The healthcare provider maintains secure physical access to the server
- Network communication will be secured via HTTPS in production
- MongoDB is installed and running on the deployment machine

---

## 6. Requirements Traceability Matrix

| Requirement ID | Feature | Implementation File | Test |
|---------------|---------|-------------------|------|
| FR-01, FR-02 | Registration/Login | routes/auth.py | test_successful_registration, test_successful_login |
| FR-03 | Role redirect | routes/auth.py | test_role_redirect_flow |
| FR-04, FR-05 | User management | routes/admin.py | test_user_management_flow |
| FR-07 | RBAC | All route files | test_patient_cannot_access_admin |
| FR-08 to FR-14 | Patient records | routes/records.py | test_admin_create_and_view_record_flow |
| FR-15 to FR-19 | Appointments | routes/appointments.py | test_past_appointment_rejected |
| FR-20 to FR-23 | Prescriptions | routes/prescriptions.py | test_complete_patient_journey |
| FR-24 to FR-29 | Audit logging | models.py, all routes | test_audit_log_created_on_login |
| NFR-01 | Password hashing | extensions.py | test_password_is_hashed |
| NFR-02 | CSRF | extensions.py | N/A (disabled in tests) |
| NFR-03 | Rate limiting | routes/auth.py | N/A (disabled in tests) |
| NFR-04 | Input sanitisation | routes/records.py | test_xss_input_sanitised |
| NFR-06 | Security headers | app.py | test_security_headers_present |
| NFR-08, NFR-09 | Auth/role checks | All route files | test_unauthenticated_user_redirected |