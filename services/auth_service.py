

from datetime import datetime, timedelta, timezone

import jwt

from extensions import db, bcrypt
from models.user import User
from models.teacher import Teacher
from models.employer import Organization, Parent
from models.reviewer import Reviewer
from schemas.teacher import TeacherSchema
from schemas.employer import OrganizationSchema, ParentSchema
from schemas.reviewer import ReviewerSchema


from flask import current_app

from errors.exceptions import BadRequestError, ConflictError, UnauthorizedError


def register(email, password, type, extra=None):

    extra = extra or {}

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        raise ConflictError("An account with this email already exists.")

    user_classes = {
        "teacher": Teacher,
        "organization": Organization,
        "parent": Parent,
        "reviewer": Reviewer,
    }

    schema_classes = {
        "teacher": TeacherSchema,
        "organization": OrganizationSchema,
        "parent": ParentSchema,
        "reviewer": ReviewerSchema,
    }

    schema_exclusions = {
        "teacher": ("work_history", "references"),
    }

    model_class = user_classes.get(type)

    if model_class is None:
        raise BadRequestError("Invalid user type.")

    schema_class = schema_classes[type]
    exclude = schema_exclusions.get(type, ())
    payload = {"email": email, **extra}
    validated = schema_class(exclude=exclude).load(payload)

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = model_class(
        password_hash=password_hash,
        type=type,
        **validated)
    db.session.add(user)
    db.session.commit()

    return user

def login(email, password):

    user = User.query.filter_by(email=email).first()

    if (
        user is None
        or not bcrypt.check_password_hash(user.password_hash, password)
    ):
        raise UnauthorizedError("Invalid email or password.")

    now = datetime.now(timezone.utc)
    expiry = current_app.config["JWT_EXPIRY"]

    payload = {
        "user_id": user.id,
        "type": user.type,
        "admin": user.email.casefold() in current_app.config.get("ADMIN_EMAILS", ()),
        "tv": user.token_version,
        "exp": now + expiry,
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    return token


def get_current_user(token):

    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Invalid or expired token.")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid or expired token.")

    user_id = payload.get("user_id")

    if user_id is None:
        raise UnauthorizedError("Invalid token.")

    user = User.query.get(user_id)

    if user is None:
        raise UnauthorizedError("Invalid token.")

    # Tokens without a version (issued before this check existed) or with a stale one are rejected
    tv = payload.get("tv")

    if tv is None or tv != user.token_version:
        raise UnauthorizedError("Invalid token.")

    return user


def revoke_tokens(user):
    """Invalidate every token issued to this user (logout everywhere)."""

    # Increment in SQL, not Python, so two concurrent bumps can't overwrite each other
    user.token_version = User.token_version + 1

    db.session.commit()


def change_password(user, old_password, new_password):

    if not bcrypt.check_password_hash(
        user.password_hash,
        old_password,
    ):
        raise BadRequestError("Current password is incorrect.")

    user.password_hash = (
        bcrypt.generate_password_hash(new_password)
        .decode("utf-8")
    )

    # Also kills every existing token, including the caller's current one (commits both changes)
    revoke_tokens(user)

    return user
