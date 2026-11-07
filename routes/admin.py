from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from extensions import db
from errors.exceptions import BadRequestError, ForbiddenError, NotFoundError
from models.employer import Organization, Parent
from models.interview import InterviewRequest
from models.review import Review, ReviewAssignment
from models.reviewer import Reviewer
from models.teacher import Teacher
from models.user import User
from models.video import VideoSubmission
from services import verification_service
from utils.auth_utils import is_admin_email, require_role

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/overview")
@require_role("admin")
def overview():
    pending_verifications = (
        Teacher.query.filter_by(id_verified=False).count()
        + Organization.query.filter_by(id_verified=False).count()
        + Parent.query.filter_by(id_verified=False).count()
    )
    week_ago = datetime.utcnow() - timedelta(days=7)

    activity = []
    for user in User.query.order_by(User.created_at.desc()).limit(8):
        activity.append({
            "occurred_at": user.created_at.isoformat() if user.created_at else None,
            "type": "Account",
            "summary": f"{user.type.title()} account created",
            "status": "verified" if user.id_verified else "unverified",
        })

    for video, teacher_name in (
        db.session.query(VideoSubmission, Teacher.full_name)
        .join(Teacher, VideoSubmission.teacher_id == Teacher.id)
        .order_by(VideoSubmission.uploaded_at.desc())
        .limit(8)
    ):
        activity.append({
            "occurred_at": video.uploaded_at.isoformat() if video.uploaded_at else None,
            "type": "Video",
            "summary": f"Teaching video submitted by {teacher_name}",
            "status": video.status,
        })

    for review in Review.query.order_by(Review.created_at.desc()).limit(8):
        activity.append({
            "occurred_at": review.created_at.isoformat() if review.created_at else None,
            "type": "Review",
            "summary": f"{review.reviewer_type.title()} review submitted",
            "status": "flagged" if review.flagged else "completed",
        })

    for interview in InterviewRequest.query.order_by(InterviewRequest.created_at.desc()).limit(8):
        activity.append({
            "occurred_at": interview.created_at.isoformat() if interview.created_at else None,
            "type": "Interview",
            "summary": f"Interview request from {interview.employer.type}",
            "status": interview.status,
        })

    activity.sort(key=lambda event: event["occurred_at"] or "", reverse=True)

    return jsonify({
        "metrics": {
            "accounts": User.query.count(),
            "disabled_accounts": User.query.filter_by(account_enabled=False).count(),
            "teachers": User.query.filter_by(type="teacher").count(),
            "employers": User.query.filter(
                User.type.in_(("organization", "parent"))
            ).count(),
            "verified_accounts": User.query.filter_by(id_verified=True).count(),
            "pending_verifications": pending_verifications,
            "video_reviews": VideoSubmission.query.filter(
                VideoSubmission.status.in_(
                    ("uploaded", "ai_reviewing", "assigned", "in_progress")
                )
            ).count(),
            "open_reviews": ReviewAssignment.query.filter(
                ReviewAssignment.status.in_(("assigned", "in_progress"))
            ).count(),
            "pending_interviews": InterviewRequest.query.filter_by(
                status="pending"
            ).count(),
            "new_accounts": User.query.filter(
                User.created_at >= week_ago
            ).count(),
        },
        "activity": activity[:12],
    })


@bp.get("/accounts")
@require_role("admin")
def accounts():
    query = (request.args.get("q") or "").strip()
    users = User.query
    if query:
        pattern = f"%{query}%"
        users = users.filter(
            db.or_(
                User.email.ilike(pattern),
                User.id.in_(
                    db.select(Teacher.id).where(Teacher.full_name.ilike(pattern))
                ),
                User.id.in_(
                    db.select(Organization.id).where(
                        Organization.org_name.ilike(pattern)
                    )
                ),
                User.id.in_(
                    db.select(Parent.id).where(Parent.name.ilike(pattern))
                ),
                User.id.in_(
                    db.select(Reviewer.id).where(Reviewer.full_name.ilike(pattern))
                ),
            )
        )

    results = []
    for user in users.order_by(User.created_at.desc()).limit(50):
        display_name = (
            getattr(user, "full_name", None)
            or getattr(user, "org_name", None)
            or getattr(user, "name", None)
            or ""
        )
        results.append({
            "id": user.id,
            "name": display_name,
            "email": user.email,
            "type": user.type,
            "account_enabled": user.account_enabled,
            "id_verified": user.id_verified,
            "can_verify": user.type in ("teacher", "organization", "parent"),
            "is_admin": is_admin_email(user.email),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    return jsonify(results)


@bp.patch("/accounts/<int:user_id>/status")
@require_role("admin")
def update_account_status(user_id):
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled")
    if not isinstance(enabled, bool):
        raise BadRequestError("enabled must be a boolean")

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("Account not found")
    if not enabled and is_admin_email(user.email):
        raise ForbiddenError(
            "Remove this address from ADMIN_EMAILS to revoke admin access."
        )

    if user.account_enabled != enabled:
        user.account_enabled = enabled
        user.token_version = User.token_version + 1
        db.session.commit()
    return jsonify({
        "id": user.id,
        "account_enabled": user.account_enabled,
    })


@bp.patch("/accounts/<int:user_id>/verification")
@require_role("admin")
def update_account_verification(user_id):
    data = request.get_json(silent=True) or {}
    verified = data.get("verified")
    if not isinstance(verified, bool):
        raise BadRequestError("verified must be a boolean")

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("Account not found")

    if verified:
        verifiers = {
            "teacher": verification_service.verify_teacher,
            "organization": verification_service.verify_organization,
            "parent": verification_service.verify_parent,
        }
        verifier = verifiers.get(user.type)
        if verifier is None:
            raise BadRequestError("This account type cannot be verified.")
        verifier(user_id)
    elif user.id_verified:
        user.id_verified = False
        db.session.commit()

    return jsonify({
        "id": user.id,
        "id_verified": user.id_verified,
    })


@bp.get("/reviewers")
@require_role("admin")
def reviewers():
    active_reviewers = (
        Reviewer.query
        .join(User, Reviewer.id == User.id)
        .filter(User.account_enabled.is_(True))
        .order_by(Reviewer.full_name)
        .all()
    )
    return jsonify([
        {"id": reviewer.id, "name": reviewer.full_name}
        for reviewer in active_reviewers
    ])


@bp.get("/review-assignments")
@require_role("admin")
def review_assignments():
    assignments = (
        ReviewAssignment.query
        .filter(ReviewAssignment.status.in_(("assigned", "in_progress")))
        .order_by(ReviewAssignment.assigned_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([
        {
            "id": assignment.id,
            "video_id": assignment.video_id,
            "teacher": assignment.video.teacher.full_name,
            "reviewer_id": assignment.reviewer_id,
            "reviewer": assignment.reviewer.full_name,
            "status": assignment.status,
            "assigned_at": (
                assignment.assigned_at.isoformat()
                if assignment.assigned_at else None
            ),
        }
        for assignment in assignments
    ])


@bp.patch("/review-assignments/<int:assignment_id>/reviewer")
@require_role("admin")
def reassign_review(assignment_id):
    data = request.get_json(silent=True) or {}
    reviewer_id = data.get("reviewer_id")
    if not isinstance(reviewer_id, int) or isinstance(reviewer_id, bool):
        raise BadRequestError("reviewer_id must be an integer")

    assignment = ReviewAssignment.query.get(assignment_id)
    if not assignment:
        raise NotFoundError("Review assignment not found")
    if assignment.status not in ("assigned", "in_progress"):
        raise BadRequestError("Only open review assignments can be reassigned")

    reviewer = Reviewer.query.get(reviewer_id)
    if not reviewer or not reviewer.account_enabled:
        raise NotFoundError("Active reviewer not found")

    assignment.reviewer_id = reviewer.id
    assignment.status = "assigned"
    assignment.assigned_at = datetime.utcnow()
    assignment.video.status = "assigned"
    db.session.commit()
    return jsonify({"id": assignment.id, "reviewer_id": reviewer.id})


@bp.post("/review-assignments/<int:assignment_id>/cancel")
@require_role("admin")
def cancel_review_assignment(assignment_id):
    assignment = ReviewAssignment.query.get(assignment_id)
    if not assignment:
        raise NotFoundError("Review assignment not found")
    if assignment.status not in ("assigned", "in_progress"):
        raise BadRequestError("Only open review assignments can be cancelled")

    assignment.status = "cancelled"
    assignment.video.status = "ai_reviewed"
    db.session.commit()
    return jsonify({"id": assignment.id, "status": assignment.status})
