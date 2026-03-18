from .models import AuditLog


def get_client_ip(request):
    """Extract client IP safely"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]

    return request.META.get("REMOTE_ADDR")


def log_action(user, action, target_type=None, target_id=None, request=None):
    """
    Create an audit log entry.
    This should be called by services or views.
    """

    ip = None

    if request:
        ip = get_client_ip(request)

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip,
    )