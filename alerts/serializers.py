from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    surgery_name = serializers.CharField(source="surgery.title", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id",
            "surgery",        # keep this if you want ID
            "surgery_name",   # 👈 added
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
