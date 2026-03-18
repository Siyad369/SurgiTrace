from django.urls import path
from .views import OperatingRoomListCreateAPIView, OperatingRoomDetailAPIView, SurgeryListCreateAPIView, SurgeryDetailAPIView, UpcomingSurgeriesAPIView, CompletedSurgeriesAPIView, DepartmentSurgeriesAPIView


urlpatterns = [

    path('surgeries/', SurgeryListCreateAPIView.as_view(), name='surgery-list-create'),
    path('surgeries/<int:pk>/', SurgeryDetailAPIView.as_view(), name='surgery-detail'),

    path('surgeries/upcoming/', UpcomingSurgeriesAPIView.as_view(), name='surgery-upcoming'),
    path('surgeries/completed/', CompletedSurgeriesAPIView.as_view(), name='surgery-completed'),
    path('surgeries/department/<int:department_id>/', DepartmentSurgeriesAPIView.as_view(), name='surgery-by-department'),

    path('rooms/', OperatingRoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', OperatingRoomDetailAPIView.as_view(), name='room-detail'),
]
