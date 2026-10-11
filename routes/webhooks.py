# Unauthenticated webhook receiver; authenticity is verified by the service layer.
from flask import Blueprint, request, jsonify

from services import video_service

bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")


@bp.post("/cloudinary")
def cloudinary_webhook():
    body = request.get_data(as_text=True)
    timestamp = request.headers.get("X-Cld-Timestamp")
    signature = request.headers.get("X-Cld-Signature")

    if not timestamp or not signature:
        return jsonify({"error": "Missing Cloudinary signature headers"}), 400

    payload = request.get_json(silent=True) or {}
    # Ignore non-upload notifications; the browser confirmation flow remains primary.
    if payload.get("notification_type") not in (None, "upload"):
        return jsonify({"status": "ignored"}), 200

    submission = video_service.handle_cloudinary_webhook(
        body=body,
        timestamp=timestamp,
        signature=signature,
        payload=payload,
    )
    return jsonify({"status": "ok", "submission_id": submission.id}), 200
