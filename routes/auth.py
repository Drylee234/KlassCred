from flask import Blueprint, request, g

from schemas.user import UserSchema
from services import auth_service
from utils.auth_utils import require_role

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/register")
def register():
    data = request.get_json()

    user = auth_service.register(
        email=data["email"],
        password=data["password"],
        type=data["type"],
        **data["kwargs"]
    )

    return UserSchema().dump(user), 201


@bp.post("/login")
def login():
    data = request.get_json()

    token = auth_service.login(
        email=data["email"],
        password=data["password"],
    )

    return {"token": token}, 200


@bp.post("/change-password")
@require_role("teacher", "organization", "parent", "reviewer")
def change_password():
    data = request.get_json()

    auth_service.change_password(
        user=g.current_user,
        old_password=data["old_password"],
        new_password=data["new_password"],
    )

    return {"message": "Password updated successfully."}, 200