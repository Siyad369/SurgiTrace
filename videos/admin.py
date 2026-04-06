from django.contrib import admin
from .models import SurgeryVideo


@admin.register(SurgeryVideo)
class SurgeryVideoAdmin(admin.ModelAdmin):

    # 📋 Columns to show
    list_display = (
        "id",
        "surgery_id",
        "storage_type",
        "duration",
        "created_at",
    )

    # 🔍 Filters
    list_filter = ("storage_type", "created_at")

    # 🔎 Search
    search_fields = ("id", "surgery_id__id")

    # 📄 Read-only fields
    readonly_fields = (
        "video_hash",
        "created_at",
        "video_url",
        "recording_start",
        "recording_end",
        "duration",
        "storage_type",
        "surgery_id",
    )

    # ❌ Disable edit
    def has_change_permission(self, request, obj=None):
        return False

    # ❌ Disable delete
    def has_delete_permission(self, request, obj=None):
        return False

    # ❌ Optional: disable add from admin (strict WORM)
    def has_add_permission(self, request):
        return False