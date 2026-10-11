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

    return cloudinary_adapter.generate_upload_url(
        scenario_id=scenario_id,
        teacher_id=teacher_id,
    )


def confirm_upload(teacher_id, scenario_id, video_url):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)
    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    existing = VideoSubmission.query.filter_by(video_url=video_url).first()
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
    """Process a signed Cloudinary upload notification idempotently."""
    if not cloudinary_adapter.verify_webhook_signature(body, timestamp, signature):
        raise BadRequestError("Invalid webhook signature")

    context = (payload.get("context") or {}).get("custom") or {}
    try:
        teacher_id = int(context["teacher_id"])
        scenario_id = int(context["scenario_id"])
    except (KeyError, TypeError, ValueError):
        raise BadRequestError("Webhook payload is missing teacher/scenario context")

    video_url = payload.get("secure_url")
    if not video_url:
        raise BadRequestError("Webhook payload is missing secure_url")

    existing = VideoSubmission.query.filter_by(video_url=video_url).first()
    if existing:
        if existing.status == "uploaded":
            review_service.run_ai_review(existing.id)
        return existing

    return confirm_upload(teacher_id, scenario_id, video_url)


def get_submissions(teacher_id):
    """Return all video submissions belonging to the authenticated teacher."""
    return (
        VideoSubmission.query
        .filter_by(teacher_id=teacher_id)
        .order_by(VideoSubmission.uploaded_at.desc())
        .all()
    )
