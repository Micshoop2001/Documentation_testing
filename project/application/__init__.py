from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.customers import customers_bp
from .blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint
from config import DevelopmentConfig, TestingConfig, prodconfig

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

SWAGGER_URL = '/api/docs' # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml' # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Your API's Name"})

def create_app(config_name):
    print(">>> create_app CALLED:", config_name)
    print(">>> __init__.py create_app reference:", create_app)

    app = Flask(__name__)
    config_map = {
    "DevelopmentConfig": DevelopmentConfig,
    "TestingConfig": TestingConfig,
    "prodconfig": prodconfig
    }
    
    app.config.from_object(config_map[config_name])
    print("Loaded config from:", app.config['SQLALCHEMY_DATABASE_URI'])
    
    #initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    #Register Blueprints
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    return app