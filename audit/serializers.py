from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "action",
            "target_type",
            "target_id",
            "ip_address",
            "timestamp",
        ]