from django.utils.translation import gettext_lazy as _

UNIT_COST = 1
SYSTEM_COST = 2
COST_TYPES = (
    (UNIT_COST, _('Unit cost')),
    (SYSTEM_COST, _('System cost')),
)

PERCENT_DISCOUNT = 1
VALUE_DISCOUNT = 2
DISCOUNT_TYPES = (
    (PERCENT_DISCOUNT, _('Discount by percent')),
    (VALUE_DISCOUNT, _('Discount by Dollar Value')),
)

PRE_DOCTOR_ORDER = 1
ON_DOCTOR_ORDER = 2
POST_DOCTOR_ORDER = 3
DISCOUNT_APPLY_TYPES = (
    (PRE_DOCTOR_ORDER, _('Preorder')),
    (ON_DOCTOR_ORDER, _('Point of Sale')),
    (POST_DOCTOR_ORDER, _('Post order')),
)


DISCOUNTS = {
    'Bulk': PRE_DOCTOR_ORDER,
    'CCO': ON_DOCTOR_ORDER,
    'Repless': ON_DOCTOR_ORDER,
}

SPEND = 1
MARKETSHARE = 2
PURCHASED_UNITS = 3
USED_UNITS = 4

TIER_TYPES = (
    (SPEND, _('Spend')),
    (MARKETSHARE, _('Marketshare')),
    (PURCHASED_UNITS, _('Purchased units')),
    (USED_UNITS, _('Used units')),
)


NEW_REBATE = 1
COMPLETE_REBATE = 2
REBATE_STATUSES = (
    (NEW_REBATE, _('New')),
    (COMPLETE_REBATE, _('Complete')),
)


ELIGIBLE_ITEM = 1
REBATED_ITEM = 2
REBATABLE_ITEM_TYPES = (
    (ELIGIBLE_ITEM, _('Eligible item')),
    (REBATED_ITEM, _('Rebated item')),
)

DROPPED = 1
WRONG_DEVICE = 2
REP_ERROR = 3
DOCTOR_ERROR = 4
DAMAGED_PACKAGING = 5
NOT_IMPLANTED_REASONS = (
    (DROPPED, _('Dropped')),
    (WRONG_DEVICE, _('Wrong device')),
    (REP_ERROR, _('Rep error')),
    (DOCTOR_ERROR, _('Doctor error')),
    (DAMAGED_PACKAGING, _('Damaged packaging')),
)
