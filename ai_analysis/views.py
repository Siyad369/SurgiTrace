import threading

from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response

from .ai_client import call_ai_service
from .models import AIAnalysis, VideoEvent
from videos.models import SurgeryVideo
from .tasks import run_ai_analysis


class RunAnalysisAPIView(APIView):

    #     def post(self, request, video_id):
    #         try:
    #             video = SurgeryVideo.objects.get(id=video_id)
    #
    #             # ✅ Create analysis record
    #             analysis = AIAnalysis.objects.create(
    #                 video=video,
    #                 status="processing"
    #             )
    #
    #
    #             # 🔥 Build PUBLIC URL
    #             video_url = request.build_absolute_uri(video.video_path.url)
    #
    #             # 🔥 START BACKGROUND THREAD
    #             thread = threading.Thread(
    #                 target=run_ai_analysis,
    #                 args=(analysis.id, video_url)
    #             )
    #             thread.start()
    #
    #             print("VIDEO URL:", video_url)
    #
    #             # 🔥 Call HuggingFace AI
    #             result = call_ai_service(video_url)
    #
    #             print("AI RESULT:", result)
    #
    #             # ✅ Save summary
    #             analysis.summary = result.get("summary", "")
    #             analysis.status = "completed"
    #             analysis.completed_at = now()
    #             analysis.save()
    #
    #             # ✅ Save events
    #             events = result.get("events", [])
    #
    #             for event in events:
    #                 VideoEvent.objects.create(
    #                     analysis=analysis,
    #                     event_type=event.get("event_type", "unknown"),
    #                     timestamp=event.get("timestamp", 0),
    #                     confidence=event.get("confidence", 0.9)
    #                 )
    #
    #             return Response({"message": "Analysis completed"})
    #
    #         except SurgeryVideo.DoesNotExist:
    #             return Response({"error": "Video not found"}, status=404)

    def post(self, request, video_id):
        video = SurgeryVideo.objects.get(id=video_id)

        # create analysis
        analysis = AIAnalysis.objects.create(video=video)

        video_url = request.build_absolute_uri(video.video_path.url)

        # 🔥 START BACKGROUND THREAD
        thread = threading.Thread(
            target=run_ai_analysis,
            args=(analysis.id, video_url)
        )
        thread.start()

        return Response({
            "message": "Analysis started",
            "analysis_id": analysis.id,
            "status": "processing"
        })


class GetAnalysisAPIView(APIView):

    def get(self, request, analysis_id):
        analysis = AIAnalysis.objects.get(id=analysis_id)

        events = VideoEvent.objects.filter(analysis=analysis)

        return Response({
            "status": analysis.status,
            "summary": analysis.summary,
            "events": [
                {
                    "event_type": e.event_type,
                    "timestamp": e.timestamp,
                    "confidence": e.confidence
                }
                for e in events
            ]
        })
