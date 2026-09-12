from flask import Blueprint, request
from services import video_service

bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")

@bp.post("/cloudinary")
def cloudinary_webhook():
    payload = request.get_json()
    video_service.handle_cloudinary_webhook(payload)
    return {}, 200