from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from audit.models import AuditAction
from audit.services import log_action
from .models import User, Department, Role


class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        request = self.context.get("request")

        try:
            data = super().validate(attrs)

            # ---------------------------
            # USER DATA RESPONSE
            # ---------------------------
            user_data = {
                "id": self.user.id,
                "name": self.user.name,
                "email": self.user.email,
                "role": self.user.role,
            }

            if self.user.department:
                user_data["department"] = self.user.department.name
                user_data["department_id"] = self.user.department.id

            # ---------------------------
            # AUDIT LOG (SUCCESS LOGIN)
            # ---------------------------
            log_action(
                user=self.user,
                action=AuditAction.LOGIN,
                target_type="user",
                target_id=self.user.id,
                request=request
            )

            return {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": user_data
            }

        except Exception:
            # ---------------------------
            # AUDIT LOG (FAILED LOGIN)
            # ---------------------------
            log_action(
                user=None,  # user unknown on failure
                action=AuditAction.ACCESS_DENIED,
                target_type="user",
                target_id=None,
                request=request
            )

            raise

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={"input_type": "password"}
    )

    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance:  # CREATE operation — no instance means POST
            self.fields["password"].required = True

    class Meta:
        model = User
        fields = ["id", "name", "email", "password","role", "department", "department_name","created_at"]
        read_only_fields = ["id", "created_at"]

    # PASSWORD VALIDATION
    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be entirely numeric.")
        if not value.strip():
            raise serializers.ValidationError("Password cannot be blank.")
        return value

    # ROLE SECURITY (CRITICAL)
    def validate_role(self, value):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Invalid request")

        # Allow same role (no change)
        if self.instance and self.instance.role == value:
            return value

        # Only system admin can assign/change roles
        if request.user.role != Role.SYSTEM_ADMIN:
            raise serializers.ValidationError("Only system admin can change roles")

        return value

    # MAIN VALIDATION
    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        department = attrs.get("department", getattr(self.instance, "department", None))

        if role in [Role.DOCTOR, Role.DEPARTMENT_HEAD] and not department:
            raise serializers.ValidationError({"department": "Department required"})

        if role in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN] and department:
            raise serializers.ValidationError({"department": "Admins should not have department"})

        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is required.")

        if self.instance and "department" in attrs:
            if request.user.role not in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN]:
                raise serializers.ValidationError("Not allowed to change department")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
