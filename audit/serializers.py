from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "role",
            "action",
            "target_type",
            "target_id",
            "ip_address",
            "timestamp",
        ]