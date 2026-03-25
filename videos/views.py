from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import FileResponse, Http404

from audit.models import AuditAction
from audit.services import log_action
from .models import SurgeryVideo
from .serializer import SurgeryVideoSerializer


# 📌 GET all videos / GET single / POST upload
class SurgeryVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # 👉 Get single video
        if pk:
            try:
                video = SurgeryVideo.objects.get(pk=pk)
                # ✅ LOG METADATA ACCESS
                log_action(
                    user=request.user,
                    action=AuditAction.VIEW_VIDEO,
                    target_type="video",
                    target_id=video.id,
                    request=request
                )

                serializer = SurgeryVideoSerializer(video)
                return Response(serializer.data)
            except SurgeryVideo.DoesNotExist:
                return Response(
                    {"error": "Video not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 👉 Get all videos
        videos = SurgeryVideo.objects.all()
        serializer = SurgeryVideoSerializer(videos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SurgeryVideoSerializer(data=request.data)

        if serializer.is_valid():
            video = serializer.save()
            # ✅ LOG UPLOAD
            log_action(
                user=request.user,
                action=AuditAction.UPLOAD_VIDEO,
                target_type="video",
                target_id=video.id,
                request=request
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🎥 Stream video
class VideoStreamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            video = SurgeryVideo.objects.get(pk=pk)
            # ✅ LOG BEFORE RETURNING VIDEO
            log_action(
                user=request.user,
                action=AuditAction.VIEW_VIDEO,
                target_type="video",
                target_id=video.id,
                request=request
            )
            # return video file
            return FileResponse(
                video.video_path.open('rb'),
                content_type='video/mp4'
            )

        except SurgeryVideo.DoesNotExist:
            raise Http404("Video not found")


# 🔐 Verify video integrity (hash check)
class VideoVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            video = SurgeryVideo.objects.get(pk=pk)

            current_hash = video.generate_hash()
            # ✅ LOG VERIFY ACTION
            log_action(
                user=request.user,
                action=AuditAction.VIEW_VIDEO,  # or create VERIFY_VIDEO action
                target_type="video",
                target_id=video.id,
                request=request
            )
            return Response({
                "stored_hash": video.video_hash,
                "current_hash": current_hash,
                "is_valid": video.video_hash == current_hash
            })

        except SurgeryVideo.DoesNotExist:
            return Response(
                {"error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND
            )
