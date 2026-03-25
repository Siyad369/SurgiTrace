from django.urls import path
from .views import (
    SurgeryVideoAPIView,
    VideoStreamAPIView,
    VideoVerifyAPIView
)

urlpatterns = [
    # 📌 GET all videos / POST upload
    path("operation/videos/", SurgeryVideoAPIView.as_view()),

    # 📌 GET single video
    path("video/get_single/<int:pk>/", SurgeryVideoAPIView.as_view()),

    # 🎥 Stream video
    path("<int:pk>/stream/", VideoStreamAPIView.as_view()),

    # 🔐 Verify hash
    path("<int:pk>/verify/", VideoVerifyAPIView.as_view()),
]