# ai_analysis/tasks.py

import threading
from .ai_client import call_ai_service
from .models import AIAnalysis, VideoEvent


def run_ai_analysis(analysis_id, video_url):
    try:
        analysis = AIAnalysis.objects.get(id=analysis_id)
        analysis.status = "processing"
        analysis.save()

        result = call_ai_service(video_url)

        # Save summary
        analysis.summary = result.get("summary")
        analysis.status = "completed"
        analysis.save()

        # Save events
        for event in result.get("events", []):
            VideoEvent.objects.create(
                analysis=analysis,
                event_type=event.get("event_type"),
                timestamp=event.get("timestamp"),
                confidence=event.get("confidence"),
            )

    except Exception as e:
        analysis.status = "failed"
        analysis.summary = str(e)
        analysis.save()
