from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AIAnalysis, VideoEvent
from .services import run_medgemma_analysis
from videos.models import SurgeryVideo


class RunAnalysisAPIView(APIView):

    def post(self, request, video_id):
        try:
            video = SurgeryVideo.objects.get(id=video_id)

            # ✅ create analysis record
            analysis = AIAnalysis.objects.create(
                video=video,
                status="processing"
            )

            # 🔥 run AI
            result = run_medgemma_analysis(video.video_path.path)

            # ✅ save summary
            analysis.summary = result["summary"]
            analysis.status = "completed"
            analysis.completed_at = now()
            analysis.save()

            # ✅ save events
            for event in result["events"]:
                VideoEvent.objects.create(
                    analysis=analysis,
                    event_type=event["event_type"],
                    timestamp=event["timestamp"],
                    confidence=event["confidence"]
                )

            return Response({"message": "Analysis completed"})

        except SurgeryVideo.DoesNotExist:
            return Response({"error": "Video not found"}, status=404)

    
class GetAnalysisAPIView(APIView):

    def get(self, request, video_id):
        analysis = AIAnalysis.objects.filter(video_id=video_id).order_by('-id').first()

        if not analysis:
            return Response({"error": "No analysis found"}, status=404)

        events = VideoEvent.objects.filter(analysis=analysis).values()

        return Response({
            "status": analysis.status,
            "summary": analysis.summary,
            "events": list(events)
        })