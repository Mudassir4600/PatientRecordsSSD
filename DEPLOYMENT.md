# Deployment Guide
**HealthSecure PRS — COM7033 Secure Software Development**

## Local Development Deployment

### System Requirements
- Windows 10/11, macOS, or Linux
- Python 3.8 or higher
- MongoDB 6.0 or higher
- 2GB RAM minimum
- Internet connection (for CDN resources)

### Step-by-Step Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/Mudassir4600/PatientRecordsSSD.git
cd PatientRecordsSSD
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install all dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root directory:
```
SECRET_KEY=your-strong-secret-key-minimum-32-characters
MONGO_URI=mongodb://localhost:27017/patient_records
SQLITE_DB=instance/auth.db
ENCRYPTION_KEY=your-fernet-encryption-key
```

Generate a secure encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**5. Start MongoDB service**
```bash
net start MongoDB    # Windows
sudo systemctl start mongod    # Linux
brew services start mongodb-community    # macOS
```

**6. Run the application**
```bash
python app.py
```

Access at: `http://127.0.0.1:5000`

---

## Production Deployment Considerations

### Using Gunicorn (Linux/macOS)
For production, replace the development server with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Using Waitress (Windows)
```bash
pip install waitress
waitress-serve --port=8000 "app:create_app()"
```

### Environment Security Checklist
Before deploying to production, ensure the following:

- [ ] `debug=False` in `app.py`
- [ ] Strong `SECRET_KEY` set in `.env` (minimum 32 characters)
- [ ] Strong `ENCRYPTION_KEY` generated with Fernet
- [ ] `.env` file added to `.gitignore`
- [ ] MongoDB authentication enabled
- [ ] HTTPS configured (SSL certificate)
- [ ] Firewall rules configured
- [ ] Regular database backups scheduled

---

## Optional Docker Containerisation

Create a `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t healthsecure-prs .
docker run -p 5000:5000 healthsecure-prs
```

---

## Database Setup

### SQLite (Authentication Database)
SQLite is automatically created when the app starts for the first time. The database file is stored at `instance/auth.db`. No manual setup is required.

### MongoDB (Patient Records Database)
Collections are created automatically when the first document is inserted. The following collections are used:

| Collection | Purpose |
|-----------|---------|
| `patient_records` | Clinical patient data |
| `appointments` | Appointment bookings |
| `prescriptions` | Issued prescriptions |

---

## Security Configuration

### Session Security
The following session security settings are configured in `config.py`:
- `SESSION_COOKIE_HTTPONLY = True` — prevents JavaScript access to session cookie
- `SESSION_COOKIE_SAMESITE = 'Lax'` — prevents CSRF via cross-site requests

### Rate Limiting
Login endpoint is limited to **5 requests per minute** per IP address to prevent brute force attacks.

### Security Headers
The following headers are applied to every response:
- `X-Frame-Options: DENY` — prevents clickjacking
- `X-Content-Type-Options: nosniff` — prevents MIME sniffing
- `Strict-Transport-Security` — enforces HTTPS
- `Content-Security-Policy` — restricts resource loading

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `ModuleNotFoundError` | Run `venv\Scripts\activate` then `pip install -r requirements.txt` |
| MongoDB connection error | Run `net start MongoDB` |
| Port already in use | Change port: `app.run(port=5001)` |
| CSRF token error | Clear browser cookies and try again |
| Encryption key error | Generate new key and update `.env` |