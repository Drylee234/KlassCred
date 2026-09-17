from flask import jsonify
from marshmallow import ValidationError

from errors.exceptions import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
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



    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
