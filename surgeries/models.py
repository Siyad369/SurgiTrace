from django.db import models
from accounts.models import Department, User


class OperatingRoom(models.Model):
    room_number = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    camera_id = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"Room {self.room_number} - {self.department.name}"


class Surgery(models.Model):

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=255)
    patient_reference = models.CharField(max_length=100)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    room = models.ForeignKey(OperatingRoom, on_delete=models.SET_NULL, null=True)

    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()

    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    consent_signed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title







