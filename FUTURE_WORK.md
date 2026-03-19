# Future Work
**HealthSecure PRS — Patient Record Management System**  
**Module:** Secure Software Development  
**Institution:** Leeds Trinity University  
**Author:** Mudassar Ali  
**Date:** March 2026

---

## Overview

The current implementation of HealthSecure PRS successfully demonstrates 
secure software development principles as a prototype system. However, 
before clinical deployment in a real healthcare environment, significant 
additional work would be required. This document outlines planned 
enhancements across security, functionality, compliance, and scalability.

---

## 1. Security Enhancements

### 1.1 Multi-Factor Authentication (MFA)
The current system uses single-factor authentication (email + password). 
A production healthcare system should implement MFA using TOTP (Time-based 
One-Time Passwords) via an authenticator app such as Google Authenticator. 
This would significantly reduce the risk of account compromise even if 
credentials are stolen.

**Implementation:** Flask-TOTP or PyOTP library  
**Priority:** High  
**STRIDE:** Spoofing

### 1.2 Automated Session Timeout
Currently sessions persist until the user logs out. A production system 
should automatically terminate sessions after a period of inactivity 
(e.g. 15 minutes) to prevent unauthorised access from unattended terminals a critical requirement in clinical environments.

**Implementation:** Flask-Login session timeout configuration  
**Priority:** High  
**STRIDE:** Spoofing / Elevation of Privilege

### 1.3 Account Lockout Policy
The current rate limiting (5 requests/minute) prevents brute force attacks 
but does not permanently lock accounts after repeated failures. A production 
system should implement progressive lockout, temporary lock after 5 failed 
attempts, permanent lock after 10, requiring admin intervention.

**Implementation:** Custom lockout counter in SQLite Users table  
**Priority:** High  
**STRIDE:** Spoofing

### 1.4 Full Database Encryption at Rest
Currently only individual sensitive fields are encrypted using Fernet. A 
production system should implement full database encryption at rest for both 
SQLite and MongoDB, ensuring data is protected even if the storage medium 
is physically compromised.

**Implementation:** MongoDB Encrypted Storage Engine, SQLCipher for SQLite  
**Priority:** High  
**STRIDE:** Information Disclosure

### 1.5 Formal Penetration Testing
The current system has been tested with automated unit, integration, and 
end-to-end tests. A production deployment would require formal penetration 
testing by a qualified security professional to identify vulnerabilities 
that automated tests may miss.

**Priority:** High before any production deployment

---

## 2. Functionality Enhancements

### 2.1 Patient-Clinician Assignment
Currently any clinician can view any patient record. A production system 
should implement explicit patient-clinician assignment, where clinicians 
can only access records of patients assigned to them, further limiting 
data exposure.

### 2.2 File Attachments
Clinical records often include supporting documents such as scan results, 
lab reports, and referral letters. Future work would add secure file upload 
functionality with virus scanning and encrypted storage.

### 2.3 Email Notifications
Patients should receive email notifications when appointments are confirmed 
or prescriptions are issued. This would use Flask-Mail with NHS-compliant 
email encryption.

### 2.4 Search and Filtering
The current records list shows all records without search or filtering. 
A production system would need robust search functionality for clinicians 
managing large patient lists.

### 2.5 Password Reset Flow
Currently there is no self-service password reset. Users who forget their 
password must contact an admin. A secure email-based password reset flow 
would significantly improve usability.

---

## 3. Compliance Enhancements

### 3.1 Data Retention Policies
UK GDPR requires that personal data is not retained longer than necessary. 
Future work would implement automated data retention policies — flagging 
records for review after a defined period and providing tools for 
compliant data deletion.

### 3.2 Subject Access Request (SAR) Tool
UK GDPR gives individuals the right to request all data held about them. 
Future work would implement a SAR tool allowing patients to download all 
their data in a structured, machine-readable format.

### 3.3 Consent Management
A production system should record explicit patient consent for data 
processing, with the ability to withdraw consent, in line with UK GDPR 
Article 7.

### 3.4 NHS Login Integration
A production NHS system would integrate with NHS Login for identity 
verification, ensuring patients are who they claim to be using 
government-verified credentials.

---

## 4. Scalability and Infrastructure

### 4.1 Production Web Server
The current system runs on Flask's development server. A production 
deployment would use Gunicorn or uWSGI behind an Nginx reverse proxy 
for performance, reliability, and SSL termination.

### 4.2 HTTPS / SSL Certificate
The current development deployment uses HTTP. All production traffic 
must be encrypted using HTTPS with a valid SSL certificate (e.g. Let's 
Encrypt) to protect data in transit.

### 4.3 Database Backups
A production system would require automated daily database backups with 
offsite storage and tested recovery procedures to ensure business 
continuity and data availability.

### 4.4 Containerisation
Future work would containerise the application using Docker and 
orchestrate it with Kubernetes, enabling consistent deployment, 
horizontal scaling, and simplified environment management.

### 4.5 Monitoring and Alerting
A production system would integrate with monitoring tools such as 
Prometheus and Grafana to track system health, detect anomalies, 
and alert administrators to potential security incidents in real time.

---

## 5. Summary Priority Table

| Enhancement | Priority | Category |
|-------------|---------|---------|
| Multi-Factor Authentication | High | Security |
| Session Timeout | High | Security |
| Account Lockout | High | Security |
| HTTPS / SSL | High | Infrastructure |
| Penetration Testing | High | Security |
| Patient-Clinician Assignment | Medium | Functionality |
| Email Notifications | Medium | Functionality |
| Password Reset | Medium | Functionality |
| Data Retention Policies | Medium | Compliance |
| SAR Tool | Medium | Compliance |
| Full DB Encryption at Rest | High | Security |
| Docker Containerisation | Low | Infrastructure |
| Monitoring and Alerting | Medium | Infrastructure |