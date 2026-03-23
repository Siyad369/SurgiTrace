from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView, TokenRefreshView
from .views import UserView, UserUpdateView, DepartmentsView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('users/', UserView.as_view(), name="user_list"),
    path('users/<int:pk>/', UserUpdateView.as_view(), name="user_detail"),
    path('departments/', DepartmentsView.as_view(), name="department_list")
]
