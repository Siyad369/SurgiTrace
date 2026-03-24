from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Department, Role
from .permissions import UserPermission, DepartmentPermission, IsAuthenticatedAndActive
from .serializers import UserSerializer, DepartmentSerializer, CustomTokenSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

class UserView(APIView):
    permission_classes = [IsAuthenticatedAndActive, UserPermission]

    def get(self,request):
        user = request.user

        if user.role == Role.SYSTEM_ADMIN:
            queryset = User.objects.select_related("department").filter(is_active=True)
        elif user.role == Role.HOSPITAL_ADMIN:
            queryset = User.objects.select_related("department").filter(is_active=True).exclude(role__in=[Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN])
        else:
            queryset = User.objects.select_related("department").filter(id=user.id, is_active=True)
        serializer = UserSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @transaction.atomic
    def post(self,request):
        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticatedAndActive, UserPermission]

    def get_object(self, request, pk):  # ADD THIS METHOD
        user = get_object_or_404(User.objects.select_related("department"), pk=pk)
        self.check_object_permissions(request, user)
        return user

    def get(self,request,pk):
        user = self.get_object(request, pk)
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    @transaction.atomic
    def put(self,request,pk):
        user = self.get_object(request, pk)
        serializer = UserSerializer(user, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def patch(self,request,pk):
        user = self.get_object(request, pk)
        serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self,request,pk):
        user = self.get_object(request, pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DepartmentsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, DepartmentPermission]

    def get(self,request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments,many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self,request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
