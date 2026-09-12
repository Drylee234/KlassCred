# services/video_service.py

from datetime import datetime

from models.video import VideoSubmission, TeachingScenario
from services import review_service
from api import cloudinary as cloudinary_adapter
from extensions import db
from errors.exceptions import NotFoundError, BadRequestError


def request_upload_url(teacher_id, scenario_id):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    result = cloudinary_adapter.generate_upload_url(
        scenario_id=scenario_id,
        teacher_id=teacher_id,
    )

    return result


def confirm_upload(teacher_id, scenario_id, video_url):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    existing = (
        VideoSubmission.query
        .filter_by(video_url=video_url)
        .first()
    )

    if existing:
        return existing

    submission = VideoSubmission(
        teacher_id=teacher_id,
        scenario_id=scenario_id,
        video_url=video_url,
        status="uploaded",
        uploaded_at=datetime.utcnow(),
    )

    db.session.add(submission)
    db.session.commit()

    review_service.run_ai_review(submission.id)

    return submission


def handle_cloudinary_webhook(body, timestamp, signature, payload):
    """
    Process a verified Cloudinary upload notification.

    Signature verification is done here before touching any data.
    The route passes raw header values; this function is the single
    place responsible for deciding whether the webhook is authentic.
    """
    valid = cloudinary_adapter.verify_webhook_signature(
        body=body,
        timestamp=timestamp,
        signature=signature,
    )

    if not valid:
        raise BadRequestError("Invalid webhook signature")

    # Cloudinary echoes context as a dict: {"teacher_id": "...", "scenario_id": "..."}
    context = payload.get("context", {})

    video_url = payload.get("secure_url") or payload.get("url")
    teacher_id = context.get("teacher_id")
    scenario_id = context.get("scenario_id")

    if not video_url or not teacher_id or not scenario_id:
        raise BadRequestError("Webhook payload is missing required fields")

    try:
        teacher_id = int(teacher_id)
        scenario_id = int(scenario_id)
    except (ValueError, TypeError):
        raise BadRequestError("Invalid teacher_id or scenario_id in webhook context")

    existing = (
        VideoSubmission.query
        .filter_by(video_url=video_url)
        .first()
    )

    if existing:
        # Idempotent: if it arrived via confirm_upload already, just
        # make sure AI review runs if it somehow didn't.
        if existing.status == "uploaded":
            review_service.run_ai_review(existing.id)

        return existing

    return confirm_upload(
        teacher_id,
        scenario_id,
        video_url,
    )
