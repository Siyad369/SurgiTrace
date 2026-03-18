from django.db import models


class Alert(models.Model):

    class AlertType(models.TextChoices):
        VIDEO_NOT_RECORDED = "video_not_recorded", "Video Not Recorded"
        CAMERA_OFFLINE = "camera_offline", "Camera Offline"
        CONSENT_MISSING = "consent_missing", "Consent Missing"
        VIDEO_TAMPERED = "video_tampered", "Video Tampered"
        UPCOMING_SURGERY = "upcoming_surgery", "Upcoming Surgery"

    class AlertStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    surgery = models.ForeignKey(
        "surgeries.Surgery",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts"
    )

    alert_type = models.CharField(max_length=50, choices=AlertType.choices)
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("surgery", "alert_type")

    def __str__(self):
        return f"{self.alert_type} - {self.status}"
