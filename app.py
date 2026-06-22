from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config
from models import db, Teacher, SystemSettings
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    frontend_url = app.config.get('FRONTEND_URL', 'http://localhost:3000')
    CORS(app, supports_credentials=True, origins=[
        'http://localhost:3000',
        'http://10.115.117.13:3000',
        frontend_url
    ], allow_headers=['Content-Type', 'Authorization'])
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Teacher.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return {'error': 'Please log in first'}, 401
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.elections import elections_bp
    from routes.classes import classes_bp
    from routes.streams import streams_bp
    from routes.positions import positions_bp
    from routes.candidates import candidates_bp
    from routes.teachers import teachers_bp
    from routes.votes import votes_bp
    from routes.results import results_bp
    from routes.notifications import notifications_bp
    from routes.settings import settings_bp
    from routes.public import public_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(elections_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(streams_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(profile_bp)
    
    # Create tables and default data
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        admin = Teacher.query.filter_by(username='admin').first()
        if not admin:
            admin = Teacher(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Default admin created: admin / admin123')
        
        # Create default settings if not exists
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings(voting_open=False)
            db.session.add(settings)
            db.session.commit()
            print('Default settings created')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)