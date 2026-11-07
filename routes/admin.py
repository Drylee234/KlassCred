from datetime import datetime, timedelta

from flask import Blueprint, jsonify

from extensions import db
from models.employer import Organization, Parent
from models.interview import InterviewRequest
from models.review import Review, ReviewAssignment
from models.teacher import Teacher
from models.user import User
from models.video import VideoSubmission
from utils.auth_utils import require_role

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
