from django.utils.translation import gettext_lazy as _


NEW_CASE = 1
COMPLETE_CASE = 2
CASE_STATUSES = (
    (NEW_CASE, _('New')),
    (COMPLETE_CASE, _('Complete')),
)
