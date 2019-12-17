from rest_framework.permissions import BasePermission

from hospital.constants import RolePriority


class HasPhysicianAccess(BasePermission):
    message = 'Unauthorized physician access'

    def has_permission(self, request, view):
        return request.user and request.user.account_set.filter(role__priority=RolePriority.PHYSICIAN.value).exists()


class HasAdminAccess(BasePermission):
    message = 'Unauthorized admin access'

    def has_permission(self, request, view):
        return request.user and request.user.account_set.filter(role__priority=RolePriority.ADMIN.value).exists()


class IsClientAdmin(BasePermission):
    message = 'Unauthorized admin access'

    def has_permission(self, request, view, *args, **kwargs):
        client_id = view.kwargs.get('client_id')
        return request.user and request.user.account_set.filter(role__priority=RolePriority.ADMIN.value,
                                                                client_id=client_id).exists()


class IsClientPhysician(BasePermission):
    message = 'Unauthorized physician access'

    def has_permission(self, request, view, *args, **kwargs):
        client_id = view.kwargs.get('client_id')
        return request.user and request.user.account_set.filter(role__priority=RolePriority.PHYSICIAN.value,
                                                                client_id=client_id).exists()
