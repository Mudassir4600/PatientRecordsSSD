# Evaluation Report
**HealthSecure PRS — COM7033 Secure Software Development**

---

## 1. Effectiveness of Security Measures

### Authentication and Authorisation
The system implements a multi-layered authentication approach. Passwords are hashed using Bcrypt with a work factor sufficient to resist brute force attacks. Flask-Login manages session state securely, ensuring that unauthenticated users are redirected to the login page. Role-based access control is enforced on every protected route through custom decorators, meaning a patient account cannot access clinician or admin functionality even if the URL is known.

Unit tests confirm that all 18 security and functional requirements pass, including tests that verify patients cannot access admin routes, invalid credentials are rejected, and session clearing occurs on logout.

### CSRF Protection
Flask-WTF provides CSRF tokens on all forms. Every POST request requires a valid token, preventing cross-site request forgery attacks. This directly mitigates the Tampering threat identified in the STRIDE analysis.

### Rate Limiting
The login endpoint is limited to 5 requests per minute per IP address. This mitigates brute force and credential stuffing attacks identified under the Spoofing category of STRIDE. In a production environment, this would be combined with account lockout policies.

### Input Sanitisation
The Bleach library sanitises all user-supplied text inputs before storage, stripping HTML tags and JavaScript. This prevents stored XSS attacks where a malicious actor might attempt to inject scripts into patient records.

### Audit Logging
Every sensitive action — login, logout, record creation, record access, user management — is recorded in the SQLite audit log with a timestamp and IP address. This directly addresses the Repudiation threat and supports regulatory compliance requirements for healthcare data audit trails.

---

## 2. Residual Risks and Trade-offs

### Residual Risks

| Risk | Likelihood | Impact | Mitigation Status |
|------|-----------|--------|------------------|
| Insider threat (authorised user misusing access) | Medium | High | Partially mitigated via audit logs |
| Session hijacking over HTTP | Low (dev only) | High | Mitigated in production via HTTPS/HSTS |
| MongoDB injection | Low | High | Mitigated via parameterised queries |
| Weak passwords chosen by users | Medium | Medium | Partially mitigated via 8-char minimum |
| Social engineering | Low | High | Outside technical scope |

### Trade-offs

**Usability vs Security**
The rate limiting on login (5 per minute) could frustrate legitimate users who mistype their password multiple times. A more user-friendly approach would implement progressive delays rather than hard blocking, but this adds implementation complexity.

**Performance vs Encryption**
Field-level encryption adds computational overhead to every database read and write. For a large-scale production system with thousands of concurrent users, this could impact response times. The trade-off is justified given the sensitivity of healthcare data.

**Flexibility vs Access Control**
Role-based access control restricts what each user can do, which may occasionally frustrate clinicians who need to perform administrative actions. A more granular permission system could address this but would significantly increase development complexity.

---

## 3. Design Decision Justifications

### Two-Database Architecture
SQLite was chosen for authentication data because user accounts and audit logs require ACID-compliant transactional integrity — critical for security operations. MongoDB was chosen for patient records because clinical data is inherently variable and document-oriented storage allows flexibility without schema migrations.

### Flask Framework
Flask was chosen over Django because its lightweight, modular nature allows security controls to be explicitly implemented and understood, rather than relying on opaque framework defaults. This aligns with the module's emphasis on demonstrating understanding of secure programming concepts.

### Bcrypt for Password Hashing
Bcrypt was chosen over MD5 or SHA-256 because it is specifically designed for password hashing, includes a salt by default, and has an adjustable work factor that can be increased as hardware improves.

### Fernet Symmetric Encryption
Fernet was chosen for field-level encryption because it provides authenticated encryption, meaning tampering with encrypted data is detectable. The encryption key is stored in environment variables rather than source code, following the principle of secrets management.

---

## 4. Ethical Reflection

### Patient Data Confidentiality
The system was designed with patient privacy as a primary concern. Patients can only view their own records, and all access to sensitive data is logged. This reflects the ethical obligation to handle healthcare data with the highest level of care.

### Transparency and Accountability
The audit log provides a complete record of who accessed what data and when. This supports organisational accountability and enables investigation of potential data breaches or misuse.

### Regulatory Alignment
The system design reflects awareness of UK GDPR, the Data Protection Act 2018, and NHS data security standards. Features such as role-based access, audit logging, and encryption directly support compliance with these regulations.

### Limitations and Honest Assessment
The system is a prototype and would require significant additional work before clinical deployment. Areas requiring further development include: multi-factor authentication, automated session timeout, formal penetration testing, and integration with existing NHS systems.

---

## 5. Summary

The HealthSecure PRS successfully demonstrates secure software development principles through practical implementation. The STRIDE framework guided security requirement derivation, and each identified threat has a corresponding mitigation implemented in code. The 18-test suite provides evidence that security controls function as intended. Residual risks have been identified and discussed honestly, and design decisions are justified through threat analysis and business impact reasoning.