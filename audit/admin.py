from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "target_type",
        "target_id",
        "ip_address",
        "timestamp",
    )

    list_filter = ("action", "timestamp", "user")
    search_fields = ("user__username", "target_type", "ip_address")
    ordering = ("-timestamp",)

    readonly_fields = (
        "id",
        "user",
        "action",
        "target_type",
        "target_id",
        "ip_address",
        "timestamp",
    )

    # 🚫 Disable Add
    def has_add_permission(self, request):
        return False

    # 🚫 Disable Edit
    def has_change_permission(self, request, obj=None):
        return False

    # 🚫 Disable Delete
    def has_delete_permission(self, request, obj=None):
        return False