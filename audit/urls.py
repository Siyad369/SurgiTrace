from django.urls import path
from .views import AuditLogListView, AuditLogDetailView


urlpatterns = [
    path("logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("logs/<uuid:id>/", AuditLogDetailView.as_view(), name="audit-log-detail"),
]