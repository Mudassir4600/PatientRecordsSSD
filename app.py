from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager, bcrypt, csrf, limiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # set up extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # add app routes (blueprints)
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.clinician import clinician_bp
    from routes.patient import patient_bp
    from routes.records import records_bp
    from routes.appointments import appointments_bp
    from routes.prescriptions import prescriptions_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(clinician_bp, url_prefix='/clinician')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(records_bp, url_prefix='/records')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(prescriptions_bp, url_prefix='/prescriptions')

    # send user to login page by default
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # add some basic security headers
    @app.after_request
    def add_security_headers(response):
        # stop clickjacking attacks
        response.headers['X-Frame-Options'] = 'DENY'
        # MIME type sniffing, stop browser guessing file types
        response.headers['X-Content-Type-Options'] = 'nosniff'
        #  use https in production
        response.headers['Strict-Transport-Security'] = \
            'max-age=31536000; includeSubDomains'
        # Control what information is sent in referrer
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # restrict what resources can load
        response.headers['Content-Security-Policy'] = \
            "default-src 'self'; " \
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net " \
            "https://cdnjs.cloudflare.com; " \
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net " \
            "https://cdnjs.cloudflare.com; " \
            "font-src 'self' https://cdnjs.cloudflare.com;"
        return response

        
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)