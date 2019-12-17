import coreapi
import coreschema
from rest_framework import schemas


class CategorySchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        if method == 'GET':
            return [
                coreapi.Field('client_id', required=True, location='path',
                              schema=coreschema.Integer(description='Client ID')),
            ]
        else:
            return []


class ProductSchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        if method == 'GET':
            return [
                coreapi.Field('client_id', required=True, location='path',
                              schema=coreschema.Integer(description='Client ID')),
            ]
        else:
            return []
