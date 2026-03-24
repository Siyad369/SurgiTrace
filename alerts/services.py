from django.utils import timezone
from datetime import timedelta

from .models import Alert
from surgeries.models import Surgery
from videos.models import SurgeryVideo


def create_alert_if_not_exists(surgery, alert_type, message):
    """
    Prevent duplicate alerts
    """
    exists = Alert.objects.filter(
        surgery=surgery,
        alert_type=alert_type,
        status__in=[Alert.AlertStatus.ACTIVE, Alert.AlertStatus.ACKNOWLEDGED],
    ).exists()

    if not exists:
        Alert.objects.create(
            surgery=surgery,
            alert_type=alert_type,
            message=message
        )


def check_missing_videos():
    surgeries = Surgery.objects.filter(status="completed")

    for surgery in surgeries:
        video_exists = SurgeryVideo.objects.filter(surgery_id=surgery).exists()
        if not video_exists:
            create_alert_if_not_exists(
                surgery,
                Alert.AlertType.VIDEO_NOT_RECORDED,
                "Surgery completed but no video recorded."
            )


def check_consent():
    surgeries = Surgery.objects.filter(consent_signed=False)

    for surgery in surgeries:
        create_alert_if_not_exists(
            surgery,
            Alert.AlertType.CONSENT_MISSING,
            "Consent form not signed."
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