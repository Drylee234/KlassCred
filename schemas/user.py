from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    id_verified = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
