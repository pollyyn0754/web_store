from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserRegisterView, UserLoginView, UserProfileUpdateView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile'),
]
