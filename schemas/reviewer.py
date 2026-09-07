from marshmallow import fields, validate
from schemas.user import UserSchema


class ReviewerSchema(UserSchema):
    id = fields.Int(dump_only=True)   # FIX: was fields.Str(dump_only=true) — wrong type, lowercase true is NameError
    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
