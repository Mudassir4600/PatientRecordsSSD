from flask import Flask
from config import Config
from extensions import db, login_manager, bcrypt, csrf

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise all extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register blueprints (route groups) for each section
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

    # Creating all SQLite tables 
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)