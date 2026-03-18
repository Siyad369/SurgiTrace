from django.urls import path
from .views import (
    SurgeryVideoAPIView,
    VideoStreamAPIView,
    VideoVerifyAPIView
)

urlpatterns = [
    # 📌 GET all videos / POST upload
    path("", SurgeryVideoAPIView.as_view()),

    # 📌 GET single video
    path("<int:pk>/", SurgeryVideoAPIView.as_view()),

    # 🎥 Stream video
    path("<int:pk>/stream/", VideoStreamAPIView.as_view()),

    # 🔐 Verify hash
    path("<int:pk>/verify/", VideoVerifyAPIView.as_view()),
]