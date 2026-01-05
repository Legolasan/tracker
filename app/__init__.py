from flask import Flask, jsonify
from flask_login import LoginManager
from app.database import db
from app.config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Health check endpoint (no auth required)
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # Register blueprints
    from app.routers.auth import auth_bp
    from app.routers.applications import applications_bp
    from app.routers.interviews import interviews_bp
    from app.routers.reminders import reminders_bp
    from app.routers.documents import documents_bp
    from app.routers.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(dashboard_bp)
    
    # User loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

