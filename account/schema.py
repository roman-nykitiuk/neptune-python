import coreapi
import coreschema
from rest_framework import schemas


class UserSchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        if method == 'PUT':
            return [
                coreapi.Field('default_client_id', required=True, location='form',
                              schema=coreschema.Integer(description='Default client ID')),
            ]
        elif method == 'GET':
            return []
