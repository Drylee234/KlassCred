# utils/auth_utils.py

from functools import wraps

from flask import request, g

from services import auth_service
from errors.exceptions import UnauthorizedError, ForbiddenError


def require_role(*roles):
    """
    Decorator that enforces JWT authentication and role-based access.

    Usage:
        @require_role("teacher")
        @require_role("organization", "parent")
        @require_role("reviewer")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise UnauthorizedError("Missing or invalid authorization header.")

            token = auth_header.split(" ", 1)[1]

            user = auth_service.get_current_user(token)

            if user.type not in roles:
                raise ForbiddenError("You do not have permission to access this resource.")

            g.current_user = user

            return f(*args, **kwargs)

        return wrapper
    return decorator