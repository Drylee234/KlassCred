from marshmallow import Schema, fields, validate
    
class TeachingScenarioSchema(Schema):
    id = fields.Int(dump_only=True)
    
    subject = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    
    level = fields.Str(
        allow_none=True,
        validate=validate.Length(max=50)
    )
    
    prompt_text = fields.Str(allow_none=True)
    
    generated_by = fields.Str(
        allow_none=True,
        validate=validate.OneOf(["ai", "bank"])
    )
    
class VideoSubmissionSchema(Schema):
    id = fields.Int(dump_only=True)
    
    teacher_id = fields.Int(required=True)
    scenario_id = fields.Int(required=True)
    
    video_url = fields.Str(dump_only=True)
    
    uploaded_at = fields.DateTime(dump_only=True)
    
    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf([
            "pending",
            "uploaded",
            "ai_reviewed",
            "human_review",
            "completed",
            "failed"
        ])
    )