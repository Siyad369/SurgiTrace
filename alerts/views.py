from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404

from surgeries.models import Surgery
from videos.models import SurgeryVideo
from .models import Alert
from .serializers import AlertSerializer
from .services import run_all_checks


class AlertListAPIView(APIView):

    def get(self, request):
        run_all_checks()

        alerts = Alert.objects.all()
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AlertDetailAPIView(APIView):

    def get(self, request, pk):
        alert = get_object_or_404(Alert, pk=pk)
        serializer = AlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResolveAlertAPIView(APIView):

    def patch(self, request, pk):
        alert = get_object_or_404(Alert, pk=pk)

        if alert.status == Alert.AlertStatus.RESOLVED:
            return Response(
                {"detail": "Alert already resolved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        alert.status = Alert.AlertStatus.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save()

        serializer = AlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MissingVideosAPIView(APIView):

    def get(self, request):
        surgeries = Surgery.objects.filter(status="completed")

        data = []

        for surgery in surgeries:
            video_exists = SurgeryVideo.objects.filter(
                surgery_id=surgery
            ).exists()

            if not video_exists:
                data.append({
                    "surgery_id": surgery.id,
                    "message": "Video not recorded"
                })

        return Response(data, status=status.HTTP_200_OK)
