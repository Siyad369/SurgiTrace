from rest_framework import serializers
from django.utils.timezone import now

from accounts.models import User, Department
from .models import Surgery, OperatingRoom


class OperatingRoomSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = OperatingRoom
        fields = [
            'id',
            'room_number',
            'camera_id',
            'status',
            'department',
            'department_name',
        ]

    def validate_room_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Room number cannot be empty")
        return value


class SurgerySerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=OperatingRoom.objects.all())

    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = Surgery
        fields = [
            'id',
            'title',
            'patient_reference',
            'doctor',
            'doctor_name',
            'department',
            'department_name',
            'room',
            'room_number',
            'scheduled_start',
            'scheduled_end',
            'actual_start',
            'actual_end',
            'status',
            'consent_signed',
            'created_at',
        ]

    def get_room_number(self, obj):
        return obj.room.room_number if obj.room else None

    def validate(self, data):
        scheduled_start = data.get('scheduled_start')
        scheduled_end = data.get('scheduled_end')

        if scheduled_start and scheduled_end:
            if scheduled_start >= scheduled_end:
                raise serializers.ValidationError(
                    "Scheduled end time must be after start time"
                )

            if scheduled_start < now():
                raise serializers.ValidationError(
                    "Scheduled start time cannot be in the past"
                )

        actual_start = data.get('actual_start')
        actual_end = data.get('actual_end')

        if actual_start and actual_end:
            if actual_start >= actual_end:
                raise serializers.ValidationError(
                    "Actual end time must be after actual start time"
                )

        status = data.get('status')
        consent_signed = data.get('consent_signed')

        if status == 'in_progress' and not consent_signed:
            raise serializers.ValidationError(
                "Consent must be signed before surgery starts"
            )

        return data
