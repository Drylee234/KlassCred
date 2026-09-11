from flask import Blueprint, request, g

from schemas.teacher import TeacherSchema, WorkHistorySchema, ReferenceSchema
from schemas.exam import ExamSchema, ExamAttemptSchema, ExamStartSchema, ExamSubmitSchema
from schemas.video import TeachingScenarioSchema, VideoSubmissionSchema
from schemas.interview import InterviewRequestSchema

from services import (
    teacher_service,
    exam_service,
    scenario_service,
    video_service,
    interview_service,
)

from utils.auth_utils import require_role

bp = Blueprint("teacher", __name__, url_prefix="/teachers")


# ─── Profile ───────────────────────────────────────────────

@bp.post("/profile")
@require_role("teacher")
def create_profile():
    data = request.get_json()

    teacher = teacher_service.create_profile(
        user_id=g.current_user.id,
        data=data,
    )

    return TeacherSchema().dump(teacher), 201


@bp.put("/profile")
@require_role("teacher")
def update_profile():
    data = request.get_json()

    teacher = teacher_service.update_profile(
        user_id=g.current_user.id,
        data=data,
    )

    return TeacherSchema().dump(teacher), 200


# ─── Work History ───────────────────────────────────────────

@bp.post("/profile/work-history")
@require_role("teacher")
def add_work_history():
    data = WorkHistorySchema().load(request.get_json())

    record = teacher_service.add_work_history(
        user_id=g.current_user.id,
        data=data,
    )

    return WorkHistorySchema().dump(record), 201


@bp.delete("/profile/work-history/<int:work_history_id>")
@require_role("teacher")
def delete_work_history(work_history_id):
    teacher_service.delete_work_history(
        user_id=g.current_user.id,
        work_history_id=work_history_id,
    )

    return {}, 204


# ─── References ─────────────────────────────────────────────

@bp.post("/profile/references")
@require_role("teacher")
def add_reference():
    data = ReferenceSchema().load(request.get_json())

    record = teacher_service.add_reference(
        user_id=g.current_user.id,
        data=data,
    )

    return ReferenceSchema().dump(record), 201


@bp.delete("/profile/references/<int:reference_id>")
@require_role("teacher")
def delete_reference(reference_id):
    teacher_service.delete_reference(
        user_id=g.current_user.id,
        reference_id=reference_id,
    )

    return {}, 204


# ─── Exams ──────────────────────────────────────────────────

@bp.get("/exams")
@require_role("teacher")
def get_available_exams():
    result = exam_service.get_available_exams(
        teacher_id=g.current_user.id,
    )

    return [
        {
            "exam": ExamSchema().dump(item["exam"]),
            "attempts_left": item["attempts_left"],
        }
        for item in result
    ], 200


@bp.post("/exams/start")
@require_role("teacher")
def start_exam():
    data = ExamStartSchema().load(request.get_json())

    attempt, questions = exam_service.start_exam(
        teacher_id=g.current_user.id,
        exam_id=data["exam_id"],
    )

    return {
        "attempt": ExamAttemptSchema().dump(attempt),
        "questions": questions,
    }, 201


@bp.post("/exams/submit")
@require_role("teacher")
def submit_exam():
    data = ExamSubmitSchema().load(request.get_json())

    attempt = exam_service.submit_exam(
        teacher_id=g.current_user.id,
        attempt_id=data["attempt_id"],
        answers=data["answers"],
    )

    return ExamAttemptSchema().dump(attempt), 200


# ─── Scenario ───────────────────────────────────────────────

@bp.get("/scenario")
@require_role("teacher")
def get_scenario():
    scenario = scenario_service.get_scenario_for_teacher(
        teacher=g.current_user,
    )

    return TeachingScenarioSchema().dump(scenario), 200


# ─── Video ──────────────────────────────────────────────────

@bp.post("/video/upload-url")
@require_role("teacher")
def request_upload_url():
    data = request.get_json()

    result = video_service.request_upload_url(
        teacher_id=g.current_user.id,
        scenario_id=data["scenario_id"],
    )

    return result, 200


@bp.post("/video/confirm")
@require_role("teacher")
def confirm_upload():
    data = request.get_json()

    submission = video_service.confirm_upload(
        teacher_id=g.current_user.id,
        scenario_id=data["scenario_id"],
        video_url=data["video_url"],
    )

    return VideoSubmissionSchema().dump(submission), 201


# ─── Interviews ─────────────────────────────────────────────

@bp.get("/interviews")
@require_role("teacher")
def get_interview_requests():
    status_filter = request.args.get("status")

    requests = interview_service.get_requests(
        user_id=g.current_user.id,
        role="teacher",
        status_filter=status_filter,
    )

    return InterviewRequestSchema(many=True).dump(requests), 200


@bp.post("/interviews/<int:request_id>/respond")
@require_role("teacher")
def respond_to_interview(request_id):
    data = request.get_json()

    result = interview_service.respond_to_request(
        teacher_id=g.current_user.id,
        request_id=request_id,
        action=data["action"],
    )

    return InterviewRequestSchema().dump(result), 200