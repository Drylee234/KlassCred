# routes/webhooks.py
#
# Unauthenticated webhook receiver.
# Signature verification is delegated to the service layer —
# the route only handles HTTP parsing and response shaping.

from flask import Blueprint, request, jsonify

from services import video_service
from errors.exceptions import BadRequestError

bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")


@bp.post("/cloudinary")
def cloudinary_webhook():
    # Cloudinary sends JSON but we need the raw body string for
    # signature verification before we parse anything.
    body = request.get_data(as_text=True)

    timestamp = request.headers.get("X-Cld-Timestamp")
    signature = request.headers.get("X-Cld-Signature")

    if not timestamp or not signature:
        return jsonify({"error": "Missing Cloudinary signature headers"}), 400

    payload = request.get_json(silent=True) or {}

    # Only process completed uploads; ignore other notification types
    # (e.g. eager transformations, moderation results).
    if payload.get("notification_type") != "upload":
        return jsonify({"status": "ignored"}), 200

    submission = video_service.handle_cloudinary_webhook(
        body=body,
        timestamp=timestamp,
        signature=signature,
        payload=payload,
    )

    return jsonify({"status": "ok", "submission_id": submission.id}), 200
