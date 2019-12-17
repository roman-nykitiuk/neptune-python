import coreapi
import coreschema
from rest_framework import schemas

from price.models import UNIT_COST, SYSTEM_COST


class OrderSchema(schemas.AutoSchema):
    def get_manual_fields(self, path, method):
        return [
            coreapi.Field('client_id', required=True, location='path',
                          schema=coreschema.Integer(description='Client ID')),
            coreapi.Field('product', required=True, location='form',
                          schema=coreschema.Integer(description='Product ID')),
            coreapi.Field('procedure_datetime', required=True, location='form',
                          schema=coreschema.String(description='Procedure datetime in format '
                                                               'YYYY-MM-DD hh:mm:ss')),
            coreapi.Field('cost_type', required=True, location='form',
                          schema=coreschema.Integer(description=f'Cost type: {UNIT_COST} for unit cost, '
                                                                f'{SYSTEM_COST} for system cost')),
            coreapi.Field('discounts', required=False, location='form',
                          schema=coreschema.Array(description=f'Selected discounts, eg. "CCO, Repless"')),
            coreapi.Field('preference_questions', required=True, location='form',
                          schema=coreschema.Array(description=f'Preference question IDs'))
        ]
