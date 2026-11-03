from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from errors.exceptions import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    AIServiceError,
)


def register_error_handlers(app):

    @app.errorhandler(BadRequestError)
    def handle_bad_request(e):
        return jsonify({"error": e.message}), 400

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(e):
        return jsonify({"error": e.message}), 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden(e):
        return jsonify({"error": e.message}), 403

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": e.message}), 404

    @app.errorhandler(ConflictError)
    def handle_conflict(e):
        return jsonify({"error": e.message}), 409

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": e.messages}), 400

    @app.errorhandler(AIServiceError)
    def handle_ai_service_error(e):
        return jsonify({"error": e.message}), 502

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception("Unhandled application error")
        return jsonify({"error": "Internal server error"}), 500
