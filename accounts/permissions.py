from rest_framework.permissions import BasePermission
from .models import Role


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.role == Role.SYSTEM_ADMIN
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == Role.SYSTEM_ADMIN:
            return True

        if obj.id == user.id:
            return True

        if user.role == Role.HOSPITAL_ADMIN:
            return obj.role not in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN]

        return False

class DepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "GET":
            return True
        return request.user.role in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN]
