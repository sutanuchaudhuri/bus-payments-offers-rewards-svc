from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from datetime import datetime, timezone
import os
import logging
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_swagger_spec(host='localhost', port=5001):
    """Create swagger specification with dynamic server URL"""
    # Read the base swagger.yaml file
    swagger_file_path = os.path.join(os.path.dirname(__file__), 'static', 'swagger.yaml')
    with open(swagger_file_path, 'r') as file:
        swagger_spec = yaml.safe_load(file)

    # Update the server URL dynamically
    swagger_spec['servers'] = [
        {
            'url': f'http://{host}:{port}',
            'description': 'Local development server'
        }
    ]

    return swagger_spec

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Configure logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

    # Create logger for the app
    app.logger.setLevel(getattr(logging, log_level))
    app.logger.info(f"Application starting with log level: {log_level}")

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///credit_card_system.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Enable CORS for API endpoints - allow access from all origins for development
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],  # Allow all origins for development
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }, supports_credentials=True)

    # Import and initialize db from models
    from app.models import db
    db.init_app(app)

    # Import routes
    from app.routes.customers import customer_bp
    from app.routes.payments import payment_bp
    from app.routes.offers import offer_bp
    from app.routes.rewards import reward_bp
    from app.routes.merchants import merchant_bp
    from app.routes.profile_history import profile_history_bp
    from app.routes.integration import integration_bp
    from app.routes.booking_management import booking_bp
    from app.routes.refund_system import refund_bp
    from app.routes.card_tokens import token_bp

    # Dynamic swagger endpoint
    @app.route('/api/swagger.json')
    def swagger_spec():
        """Dynamic swagger specification endpoint"""
        # Get the host and port from the request
        host = request.host.split(':')[0] if ':' in request.host else request.host
        port_str = request.host.split(':')[1] if ':' in request.host else '80'
        port = int(port_str)

        # Create and return the dynamic swagger spec
        spec = create_swagger_spec(host, port)
        return spec

    # Swagger UI configuration with dynamic endpoint
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'  # Use dynamic endpoint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Credit Card Payment System API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Register API blueprints
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(offer_bp, url_prefix='/api/offers')
    app.register_blueprint(reward_bp, url_prefix='/api/rewards')
    app.register_blueprint(merchant_bp, url_prefix='/api/merchants')
    app.register_blueprint(profile_history_bp, url_prefix='/api/profile-history')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')
    app.register_blueprint(booking_bp)
    app.register_blueprint(refund_bp)
    app.register_blueprint(token_bp)

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()}

    @app.route('/')
    def home():
        return {
            'message': 'Credit Card Payment System API',
            'version': '1.0.0',
            'docs': '/api/docs',
            'health': '/api/health'
        }

    return app
