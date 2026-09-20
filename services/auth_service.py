

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
    validated = schema_class(exclude=exclude).load(extra)

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = model_class(
        email=email,
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

    return user


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

    db.session.commit()

    return user
