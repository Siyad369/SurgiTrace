import uuid
from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    VIEW_VIDEO = "view_video", "View Video"
    EXPORT_VIDEO = "export_video", "Export Video"
    CREATE_SURGERY = "create_surgery", "Create Surgery"
    UPDATE_SURGERY = "update_surgery", "Update Surgery"
    DELETE_SURGERY = "delete_surgery", "Delete Surgery"
    ACCESS_DENIED = "access_denied", "Access Denied"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=50,
        choices=AuditAction.choices
    )

    target_type = models.CharField(max_length=100)

    target_id = models.IntegerField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"