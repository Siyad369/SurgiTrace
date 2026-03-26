from django.urls import path
from .views import (AlertListAPIView, AlertDetailAPIView, ResolveAlertAPIView, MissingVideosAPIView, )

urlpatterns = [
    path("alerts/", AlertListAPIView.as_view(), name="alert-list"),
    path("alerts/<int:pk>/", AlertDetailAPIView.as_view(), name="alert-detail"),
    path("alerts/<int:pk>/resolve/", ResolveAlertAPIView.as_view(), name="alert-resolve"),
    path("alerts/missing-videos/", MissingVideosAPIView.as_view()),
]
