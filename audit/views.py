from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AuditLog.objects.select_related("user").all()

        user = request.query_params.get("user")
        action = request.query_params.get("action")
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if user:
            logs = logs.filter(user_id=user)

        if action:
            logs = logs.filter(action=action)

        if start:
            start_date = parse_date(start)
            if start_date:
                logs = logs.filter(timestamp__date__gte=start_date)

        if end:
            end_date = parse_date(end)
            if end_date:
                logs = logs.filter(timestamp__date__lte=end_date)

        serializer = AuditLogSerializer(logs, many=True)

        return Response(serializer.data)


class AuditLogDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            log = AuditLog.objects.select_related("user").get(id=id)
        except AuditLog.DoesNotExist:
            return Response({"error": "Log not found"}, status=404)

        serializer = AuditLogSerializer(log)

        return Response(serializer.data)