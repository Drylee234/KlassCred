import random

from models.video import TeachingScenario, VideoSubmission
from models.teacher import Teacher
from api import gemini as ai_provider  # was: from api import cencori
from extensions import db
from errors.exceptions import BadRequestError
from utils.subjects import validate_subjects


def get_scenario_for_teacher(teacher):
    used_ids = [
        scenario_id
        for (scenario_id,) in (
            db.session.query(VideoSubmission.scenario_id)
            .filter(VideoSubmission.teacher_id == teacher.id)
            .all()
        )
    ]

    query = TeachingScenario.query.filter(
        TeachingScenario.subject.in_(teacher.subjects)
    )

    if used_ids:
        query = query.filter(
            ~TeachingScenario.id.in_(used_ids)
        )

    scenarios = query.all()

    if scenarios:
        return random.choice(scenarios)

    return generate_scenario(teacher)


def generate_scenario(teacher):
    if not teacher.subjects:
        raise BadRequestError("Teacher has no subjects assigned")

    validate_subjects(teacher.subjects)

    target_level = "secondary"

    result = ai_provider.generate_scenario(
        subject=teacher.subjects[0],
        level=target_level,
    )

    scenario = TeachingScenario(
        subject=teacher.subjects[0],
        level=target_level,
        prompt_text=result["prompt_text"],
        generated_by="ai",
    )

    db.session.add(scenario)
    db.session.commit()

    return scenario