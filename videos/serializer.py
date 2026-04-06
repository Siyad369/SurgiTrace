from rest_framework import serializers
from .models import SurgeryVideo


class SurgeryVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurgeryVideo
        fields = "__all__"

        # 🔒 Read-only fields (cannot be modified from API)
        read_only_fields = [
            "id",
            "video_hash",
            "created_at",
        ]

    # 🔥 Extra protection: block updates completely
    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Update is not allowed. Video is immutable (WORM enforced)."
        )