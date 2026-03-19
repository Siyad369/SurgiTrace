from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    surgery_id = serializers.IntegerField(source="surgery.id", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id",
            "surgery",
            "surgery_id",
            "alert_type",
            "status",
            "message",
            "created_at",
            "resolved_at",
        ]
        read_only_fields = ["created_at", "resolved_at", "status"]

    def validate(self, data):
        if not data.get("message"):
            raise serializers.ValidationError("Message is required.")
        return data