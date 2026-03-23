from rest_framework.permissions import BasePermission, SAFE_METHODS


# ROLE CHECK (BASE)
class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
                bool(request.user and request.user.is_authenticated)
                and request.user.role in self.allowed_roles
        )

# SURGERY PERMISSIONS
class SurgeryPermission(BasePermission):
    def has_permission(self, request, view):
        # Block unauthenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # CREATE
        if request.method == "POST":
            return request.user.role in ["hospital_admin", "system_admin"]

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System Admin → full access
        if user.role == "system_admin":
            return True

        # Hospital Admin → full except delete
        if user.role == "hospital_admin":
            if request.method == "DELETE":
                return False
            return True

        # Department Head → only their department
        if user.role == "department_head":
            return obj.department_id == user.department_id

        # Doctor → only assigned surgeries
        if user.role == "doctor":
            return obj.doctor_id == user.id

        # External → read-only
        if user.role == "external_entity":
            return request.method in SAFE_METHODS

        # Student → read-only limited
        if user.role == "student":
            return request.method in SAFE_METHODS

        return False

# DEPARTMENT PERMISSIONS
class DepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ["hospital_admin", "system_admin"]

# USER MANAGEMENT PERMISSIONS
class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return request.user.role == "system_admin"
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admin → full
        if user.role == "system_admin":
            return True

        # Users can view/update themselves
        if obj.id == user.id:
            return True

        # Hospital admin → manage non-admin users
        if user.role == "hospital_admin":
            return obj.role not in ["system_admin", "hospital_admin"]

        return False

# AUDIT LOG PERMISSIONS
class AuditLogPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == "system_admin"

# VIDEO PERMISSIONS
class SurgeryVideoPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        surgery = obj.surgery

        if user.role == "system_admin":
            return True

        if user.role == "hospital_admin":
            return True

        if user.role == "department_head":
            return surgery.department_id == user.department_id

        if user.role == "doctor":
            return surgery.doctor_id == user.id

        if user.role == "external_entity":
            return request.method in SAFE_METHODS

        return False
