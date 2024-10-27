from django.urls import path
from .views import login,register,forgot_password,reset_password

urlpatterns = [
    path("login/",login,name='login'),
    path("register/",register,name="register"),
    path("forgot-password/",forgot_password,name="forgot_password"),
    path("reset-password/<str:uuid>/",reset_password,name="reset_password"),
]
    