from marshmallow import  fields, validate
from schemas.user import UserSchema

class ReviewerSchema(UserSchema):
    id = fields.Str(dump_only=true)
    full_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    
    