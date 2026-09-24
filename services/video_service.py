# services/video_service.py

from datetime import datetime

from models.video import VideoSubmission, TeachingScenario
from services import review_service
from api import byteship as byteship_adapter
from extensions import db
from errors.exceptions import NotFoundError, BadRequestError


def request_upload_url(teacher_id, scenario_id):
    # Ownership is enforced by the route/auth layer.
    scenario = TeachingScenario.query.get(scenario_id)

    if not scenario:
        raise NotFoundError("Teaching scenario not found")

    result = byteship_adapter.generate_upload_url(
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


def handle_byteship_webhook(body, timestamp, signature, payload):
    """
    Process a verified Byteship file.uploaded notification.

    Signature verification is done here before touching any data.
    The route passes raw header values; this function is the single
    place responsible for deciding whether the webhook is authentic.
    """
    valid = byteship_adapter.verify_webhook_signature(
        body=body,
        timestamp=timestamp,
        signature=signature,
    )

    if not valid:
        raise BadRequestError("Invalid webhook signature")

    # Byteship payload shape: {"type": ..., "data": {"file": {"path": ..., "url": ...}}}
    file_data = payload.get("data", {}).get("file", {})
    path = file_data.get("path")

    if not path:
        raise BadRequestError("Webhook payload is missing required fields")

    teacher_id, scenario_id = byteship_adapter.parse_context_from_path(path)

    if not teacher_id or not scenario_id:
        raise BadRequestError("Could not recover teacher_id/scenario_id from file path")

    # The webhook payload doesn't reliably include a resolved URL —
    # fetch it explicitly.
    video_url = file_data.get("url") or byteship_adapter.resolve_file_url(path)

    if not video_url:
        raise BadRequestError("Could not resolve a URL for the uploaded file")

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
