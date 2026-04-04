from django.urls import path
from .views import RunAnalysisAPIView, GetAnalysisAPIView

urlpatterns = [
    path("analyze/<int:video_id>/", RunAnalysisAPIView.as_view()),
    path("analysis/<int:analysis_id>/", GetAnalysisAPIView.as_view()),
]