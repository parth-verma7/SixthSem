from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)

    # Load default configuration
    app.config.from_object(config_class)

    from . import routes
    app.register_blueprint(routes.api)

    return app
