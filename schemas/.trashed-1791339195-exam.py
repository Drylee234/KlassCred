from marshmallow import Schema, fields, validate

class ExamQuestionSchema(Schema):
    question = fields.Str(required=True)
    options = fields.List(
    fields.Str(),
        required=True
    )

class ExamSchema(Schema):
    id = fields.Int(dump_only=True)

    subject = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    questions = fields.List(
        fields.Nested(ExamQuestionSchema),
        required=True
    )

    time_limit = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )
    
    max_attempts = fields.Int(
        allow_none = True
    )

class ExamStartSchema(Schema):
    exam_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

class ExamSubmitSchema(Schema):
    attempt_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    answers = fields.Dict(
        required=True
    )
    
class ExamAttemptSchema(Schema):
    id = fields.Int(dump_only=True)

    teacher_id = fields.Int(required=True)
    exam_id = fields.Int(required=True)

    score = fields.Float(required=True)

    started_at = fields.DateTime(required=True)
    submitted_at = fields.DateTime(required=True)
    
    answers = fields.Dict(dump_only=True)
    
    completed = fields.Bool(dump_only=True)