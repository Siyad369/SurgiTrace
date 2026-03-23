from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from .views import UserView, UserUpdateView, DepartmentsView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('users/', UserView.as_view(), name="user_list"),
    path('users/<int:pk>/', UserUpdateView.as_view(), name="user_detail"),
    path('departments/', DepartmentsView.as_view(), name="department_list")
]
