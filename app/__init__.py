from flask import Flask
from app.routes import api_bp

def create_app(config_object=None):
    app = Flask(__name__)

    # Cargar la configuración de un objeto específico, si se proporciona
    if config_object:
        app.config.from_object(config_object)
            
    # Registrar los blueprints (rutas) de la API
    app.register_blueprint(api_bp)

    return app
