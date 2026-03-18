from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import FileResponse, Http404

from .models import SurgeryVideo
from .serializers import SurgeryVideoSerializer


# 📌 GET all videos / GET single / POST upload
class SurgeryVideoAPIView(APIView):

    def get(self, request, pk=None):
        # 👉 Get single video
        if pk:
            try:
                video = SurgeryVideo.objects.get(pk=pk)
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🎥 Stream video
class VideoStreamAPIView(APIView):

    def get(self, request, pk):
        try:
            video = SurgeryVideo.objects.get(pk=pk)

            # return video file
            return FileResponse(
                video.video_path.open('rb'),
                content_type='video/mp4'
            )

        except SurgeryVideo.DoesNotExist:
            raise Http404("Video not found")


# 🔐 Verify video integrity (hash check)
class VideoVerifyAPIView(APIView):

    def get(self, request, pk):
        try:
            video = SurgeryVideo.objects.get(pk=pk)

            current_hash = video.generate_hash()

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