from functools import wraps

from flask import current_app, request, g

from services import auth_service
from errors.exceptions import UnauthorizedError, ForbiddenError


def is_admin_email(email):
    allowed_emails = current_app.config.get("ADMIN_EMAILS", ())
    if isinstance(allowed_emails, str):
        allowed_emails = allowed_emails.split(",")
    return email.casefold() in {
        allowed.strip().casefold()
        for allowed in allowed_emails
        if allowed.strip()
    }


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise UnauthorizedError("Missing or invalid authorization header.")

            token = auth_header.split(" ", 1)[1]

            user = auth_service.get_current_user(token)

            if user.type not in roles and not ("admin" in roles and is_admin_email(user.email)):
                raise ForbiddenError("You do not have permission to access this resource.")

            g.current_user = user

            return f(*args, **kwargs)

        return wrapper
    return decorator