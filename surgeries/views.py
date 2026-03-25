from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from audit.models import AuditAction
from audit.services import log_action
from .models import OperatingRoom, Surgery
from .serializers import OperatingRoomSerializer, SurgerySerializer


class OperatingRoomListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = OperatingRoom.objects.select_related('department').all()
        serializer = OperatingRoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OperatingRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OperatingRoomDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(OperatingRoom.objects.select_related('department'),pk=pk)

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = OperatingRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        room = self.get_object(pk)
        serializer = OperatingRoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        room = self.get_object(pk)
        serializer = OperatingRoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        room = self.get_object(pk)
        room.delete()
        return Response({"message": "Operating room deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SurgeryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        surgeries = Surgery.objects.select_related('doctor', 'department', 'room').all().order_by('-created_at')
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SurgerySerializer(data=request.data)
        if serializer.is_valid():
            surgery = serializer.save()
            log_action(
                user=request.user,
                action=AuditAction.CREATE_SURGERY,
                target_type="surgery",
                target_id=surgery.id,
                request=request
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurgeryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Surgery.objects.select_related('doctor', 'department', 'room'),pk=pk)

    def get(self, request, pk):
        surgery = self.get_object(pk)
        serializer = SurgerySerializer(surgery)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        surgery = self.get_object(pk)
        serializer = SurgerySerializer(surgery, data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_action(
                user=request.user,
                action=AuditAction.UPDATE_SURGERY,
                target_type="surgery",
                target_id=surgery.id,
                request=request
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        surgery = self.get_object(pk)
        serializer = SurgerySerializer(surgery, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_action(
                user=request.user,
                action=AuditAction.UPDATE_SURGERY,
                target_type="surgery",
                target_id=surgery.id,
                request=request
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        surgery = self.get_object(pk)
        surgery.delete()
        log_action(
            user=request.user,
            action=AuditAction.DELETE_SURGERY,
            target_type="surgery",
            target_id=surgery.id,
            request=request
        )
        return Response({"message": "Surgery deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class UpcomingSurgeriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        surgeries = Surgery.objects.select_related('doctor', 'department', 'room').filter(scheduled_start__gt=now()).order_by('scheduled_start')
        if not surgeries.exists():
            return Response(
                {"message": "No upcoming surgeries"},
                status=status.HTTP_200_OK
            )
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedSurgeriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        surgeries = Surgery.objects.select_related('doctor', 'department', 'room').filter(status='completed').order_by('-actual_end')
        if not surgeries.exists():
            return Response(
                {"message": "No completed surgeries"},
                status=status.HTTP_200_OK
            )
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DepartmentSurgeriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id):
        surgeries = Surgery.objects.select_related('doctor', 'department', 'room').filter(department_id=department_id).order_by('-created_at')
        if not surgeries.exists():
            return Response(
                {"message": "No surgeries found for this department"},
                status=status.HTTP_200_OK
            )
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)