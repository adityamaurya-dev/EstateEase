import os
os.environ['DISABLE_SQLALCHEMY_CEXT'] = '1'

from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.property_routes import property_bp
from routes.dashboard_routes import dashboard_bp
from routes.api_routes import api_bp
from seed_data import seed_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Jinja context processors & filters
    @app.template_filter('currency')
    def format_currency(value, purpose='buy'):
        try:
            val = float(value)
            if purpose == 'rent':
                return f"${val:,.0f}/mo"
            return f"${val:,.0f}"
        except (ValueError, TypeError):
            return "$0"

    @app.template_filter('number')
    def format_number(value):
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Initialize Database & Seed
    with app.app_context():
        db.create_all()
        seed_database()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
