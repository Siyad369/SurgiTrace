from django.db import transaction
from rest_framework import serializers
from models import User, Department, Role


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,min_length=8, style={"input_type": "password"},)

    class Meta:
        model = User
        fields = ["id", "name", "email", "password", "role", "department", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be entirely numeric.")
        return value

    def validate_role(self, value):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Invalid request context.")
        #only validate role field if it's actually being changed
        if self.instance and self.instance.role == value:
            return value  # no-op change, allow it

        if request.user.role != Role.SYSTEM_ADMIN:
            raise serializers.ValidationError("Only system admin can assign roles.")
        return value

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        department = attrs.get("department", getattr(self.instance, "department", None))

        if role in [Role.DOCTOR, Role.DEPARTMENT_HEAD] and not department:
            raise serializers.ValidationError({"department": "Department is required for Doctors and Department Heads."})
        #system_admin and hospital_admin should not be tied to a department
        if role in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN] and department:
            raise serializers.ValidationError({"department": "This role should not be assigned a department."})
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
            if len(password.strip()) == 0:  #reject blank password
                raise serializers.ValidationError({"password": "Password cannot be blank."})
            instance.set_password(password)

        instance.save()
        return instance
