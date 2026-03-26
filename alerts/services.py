from django.utils import timezone
from datetime import timedelta

from .models import Alert
from surgeries.models import Surgery
from videos.models import SurgeryVideo


def create_alert_if_not_exists(surgery, alert_type, message):
    """
    Safe creation (no duplicates)
    """
    alert, created = Alert.objects.get_or_create(
        surgery=surgery,
        alert_type=alert_type,
        defaults={
            "message": message,
            "status": Alert.AlertStatus.ACTIVE
        }
    )

    # If alert exists but was resolved → reactivate
    if not created and alert.status == Alert.AlertStatus.RESOLVED:
        alert.status = Alert.AlertStatus.ACTIVE
        alert.resolved_at = None
        alert.save()


def check_missing_videos():
    surgeries = Surgery.objects.filter(status="completed")

    for surgery in surgeries:
        video_exists = SurgeryVideo.objects.filter(
            surgery_id=surgery
        ).exists()

        if not video_exists:
            # 🚨 create alert
            create_alert_if_not_exists(
                surgery,
                Alert.AlertType.VIDEO_NOT_RECORDED,
                "Surgery completed but no video recorded."
            )
        else:
            # ✅ FIXED → resolve alert
            Alert.objects.filter(
                surgery=surgery,
                alert_type=Alert.AlertType.VIDEO_NOT_RECORDED
            ).update(
                status=Alert.AlertStatus.RESOLVED,
                resolved_at=timezone.now()
            )


def check_consent():
    surgeries = Surgery.objects.all()

    for surgery in surgeries:
        if not surgery.consent_signed:
            create_alert_if_not_exists(
                surgery,
                Alert.AlertType.CONSENT_MISSING,
                "Consent form not signed."
            )
        else:
            # ✅ FIXED → resolve alert
            Alert.objects.filter(
                surgery=surgery,
                alert_type=Alert.AlertType.CONSENT_MISSING
            ).update(
                status=Alert.AlertStatus.RESOLVED,
                resolved_at=timezone.now()
            )


def check_upcoming_surgeries(hours=2):
    now = timezone.now()
    upcoming_time = now + timedelta(hours=hours)

    surgeries = Surgery.objects.filter(
        scheduled_start__range=(now, upcoming_time)
    )

    for surgery in surgeries:
        create_alert_if_not_exists(
            surgery,
            Alert.AlertType.UPCOMING_SURGERY,
            "Surgery is scheduled soon."
        )


def run_all_checks():
    check_missing_videos()
    check_consent()
    check_upcoming_surgeries()