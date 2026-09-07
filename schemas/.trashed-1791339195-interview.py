from marshmallow import Schema, fields, validate

class InterviewRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    
    employer_id = fields.Int(required=True)
    teacher_id = fields.Int(required=True)
    
    contact_method = fields.Str(
        required=True,
        validate=validate.OneOf([
            "whatsapp",
            "email"
        ])
    )

    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf([
            "pending",
            "accepted",
            "rejected"
        ])
    )
    
    created_at = fields.DateTime(dump_only=True)