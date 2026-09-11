# services/exam_service.py

from datetime import datetime

from extensions import db
from models.exam import Exam, ExamAttempt

from .exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
)
from . import rating_service


def get_available_exams(teacher_id):
    exams = Exam.query.all()

    return [
        {
            "exam": exam,
            "attempts_left": exam.attempts_left(teacher_id),
        }
        for exam in exams
    ]


def start_exam(teacher_id, exam_id):
    exam = Exam.query.filter_by(id=exam_id).first()

    if not exam:
        raise NotFoundError("Exam not found.")

    attempts_left = exam.attempts_left(teacher_id)

    if attempts_left == 0:
        raise ForbiddenError("No attempts remaining.")

    current_attempt = ExamAttempt.query.filter_by(
        teacher_id=teacher_id,
        exam_id=exam_id,
        completed=False,
    ).first()

    if current_attempt:
        raise ConflictError(
            "You already have an active attempt for this exam."
        )

    attempt = ExamAttempt(
        teacher_id=teacher_id,
        exam_id=exam_id,
        started_at=datetime.utcnow(),
        completed=False,
    )

    db.session.add(attempt)
    db.session.commit()

    return attempt, exam.questions


def submit_exam(teacher_id, attempt_id, answers):
    attempt = ExamAttempt.query.filter_by(id=attempt_id).first()

    if not attempt:
        raise NotFoundError("Exam attempt not found.")

    if attempt.teacher_id != teacher_id:
        raise ForbiddenError("You do not own this exam attempt.")

    if attempt.completed:
        raise ConflictError("This exam attempt is already completed.")

    exam = Exam.query.filter_by(id=attempt.exam_id).first()

    if not exam:
        raise NotFoundError("Exam not found.")

    elapsed_minutes = (
        datetime.utcnow() - attempt.started_at
    ).total_seconds() / 60

    if elapsed_minutes > exam.time_limit:
        attempt.completed = True
        db.session.commit()

        raise BadRequestError(
            "Exam time limit exceeded. Attempt has been consumed."
        )

    questions = exam.questions or []
    correct = 0

    for index, question in enumerate(questions, start=1):
        if answers.get(str(index)) == question["correct_answer"]:
            correct += 1

    score = (
        (correct / len(questions)) * 100
        if questions
        else 0
    )

    attempt.score = score
    attempt.submitted_at = datetime.utcnow()
    attempt.answers = answers
    attempt.completed = True

    db.session.commit()

    rating_service.recompute(teacher_id)

    return attempt