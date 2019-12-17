import coreapi
import coreschema
from rest_framework import schemas


class LoginSchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        if method == 'POST':
            return [
                coreapi.Field('email', required=True, location='form',
                              schema=coreschema.String(description='Email address')),
                coreapi.Field('password', required=True, location='form',
                              schema=coreschema.String(description='Password'))
            ]
        return []
