from urllib.parse import quote

from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, g, redirect, request, url_for

from schemas.user import UserSchema
from errors.exceptions import BadRequestError, UnauthorizedError
from extensions import oauth
from services import auth_service
from utils.auth_utils import require_role

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _login_redirect(fragment):
    return redirect(f"{url_for('login_page')}#{fragment}")


@bp.get("/google")
def google_login():
    if not (
        current_app.config["GOOGLE_CLIENT_ID"]
        and current_app.config["GOOGLE_CLIENT_SECRET"]
    ):
        return _login_redirect("kc_oauth_error=google_not_configured")

    google = oauth.create_client("google")
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"] or url_for(
        "auth.google_callback", _external=True
    )
    return google.authorize_redirect(redirect_uri)


@bp.get("/google/callback")
def google_callback():
    try:
        token = oauth.create_client("google").authorize_access_token()
    except OAuthError:
        return _login_redirect("kc_oauth_error=google_signin_failed")

    user_info = token.get("userinfo")
    if not user_info:
        return _login_redirect("kc_oauth_error=google_signin_failed")
    try:
        result = auth_service.google_user_or_onboarding(user_info)
    except UnauthorizedError:
        return _login_redirect("kc_oauth_error=google_email_unverified")

    response_value = result.get("token") or result["onboarding_token"]
    return _login_redirect(
        f"kc_google_token={quote(response_value, safe='')}"
    )


@bp.post("/google/complete")
def complete_google_registration():
    data = request.get_json()
    if not isinstance(data, dict):
        raise BadRequestError("A JSON request body is required.")
    token = auth_service.complete_google_registration(
        onboarding_token=data.get("onboarding_token"),
        type=data.get("type"),
        extra={
            key: value
            for key, value in data.items()
            if key not in {"onboarding_token", "type"}
        },
    )
    return {"token": token}, 201


@bp.post("/register")
def register():
    data = request.get_json()
    known = {"email", "password", "type"}
    extra = {k: v for k, v in data.items() if k not in known}

    user = auth_service.register(
        email=data["email"],
        password=data["password"],
        type=data["type"],
        extra=extra
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


@bp.post("/logout")
@require_role("teacher", "organization", "parent", "reviewer", "admin")
def logout():
    auth_service.revoke_tokens(g.current_user)

    return {"message": "Logged out."}, 200


@bp.post("/change-password")
@require_role("teacher", "organization", "parent", "reviewer", "admin")
def change_password():
    data = request.get_json()

    auth_service.change_password(
        user=g.current_user,
        old_password=data["old_password"],
        new_password=data["new_password"],
    )

    return {"message": "Password updated successfully."}, 200