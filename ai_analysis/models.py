from django.db import models


class AnalysisStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class AIAnalysis(models.Model):
    video = models.ForeignKey(
        "videos.SurgeryVideo",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.PENDING
    )

    summary = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class VideoEvent(models.Model):
    analysis = models.ForeignKey(
        AIAnalysis,
        on_delete=models.CASCADE,
        related_name="events"
    )

    event_type = models.CharField(max_length=100)
    timestamp = models.FloatField()  # seconds
    confidence = models.FloatField()

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} @ {self.timestamp}s"