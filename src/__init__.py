import logging

from flask import Flask
from flask_cors import CORS, cross_origin

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    # Load default configuration
    app.config.from_object(config_class)

    cors = CORS(
        app,
        origins=["*"],
        allow_headers=["Content-Type"]
    )

    logging.getLogger("flask_cors").level = logging.DEBUG

    from . import routes

    app.register_blueprint(routes.api)

    return app
