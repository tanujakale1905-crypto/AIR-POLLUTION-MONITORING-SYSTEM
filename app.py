"""
Main Application Entry Point
Air Pollution Monitoring System
"""
import os
from flask import Flask, jsonify, render_template
from config import config_by_name
from models import db, AirQualityReading
from simulator import simulator
from routes import main_bp, api_bp

def create_app(config_name=None):
    """
    Application Factory: Creates and configures the Flask application.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure database directory exists
    db_path = app.config.get('DB_PATH')
    if db_path:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Initialize Simulator
    simulator.init_app(app)

    # Database setup and initial seeding on startup
    with app.app_context():
        db.create_all()
        # Seed realistic initial data if database is brand new and not in testing mode
        if not app.config.get('TESTING', False) and AirQualityReading.query.count() == 0:
            print("[Startup] Initializing empty database with realistic sensor history...")
            simulator.seed_historical_data(count=40)

        # Start background simulator thread if enabled and not in testing mode
        if app.config.get('SIMULATION_AUTO_START', True) and not app.config.get('TESTING', False):
            simulator.start()

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

    return app

# Expose app object for WSGI servers & CLI
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("=" * 65)
    print("  AIR POLLUTION MONITORING SYSTEM - INTERNSHIP PROJECT")
    print(f"  Web Server running at: http://127.0.0.1:{port}")
    print(f"  Dashboard:             http://127.0.0.1:{port}/")
    print(f"  Historical Analysis:   http://127.0.0.1:{port}/history")
    print(f"  Statistical Analytics: http://127.0.0.1:{port}/analytics")
    print(f"  REST API Explorer:     http://127.0.0.1:{port}/api-docs")
    print("=" * 65)
    # Note: use_reloader=False prevents duplicate background simulator threads in debug mode
    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=False)
