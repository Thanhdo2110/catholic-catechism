from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from backend.api import create_api_blueprint
from backend.api.middleware.language import register_language_middleware
from backend.config import Config
from backend.models import db
from backend.repositories import register_repositories
from backend.services import register_services


def create_app(config: type[Config] | Config = Config()) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    register_language_middleware(app)
    register_repositories(app)
    register_services(app)
    app.register_blueprint(create_api_blueprint(), url_prefix="/api")
    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(LookupError)
    def handle_lookup_error(error: LookupError) -> tuple[dict[str, str], int]:
        return {"message": str(error)}, 404

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError) -> tuple[dict[str, str], int]:
        return {"message": str(error)}, 400

    @app.errorhandler(KeyError)
    def handle_key_error(error: KeyError) -> tuple[dict[str, str], int]:
        return {"message": f"Missing required field: {error.args[0]}"}, 400


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
