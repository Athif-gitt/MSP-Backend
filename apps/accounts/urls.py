from django.urls import path
from .views import RegisterView, VerifyEmailView, LoginView, MeView, ProfileView, ResetPasswordView, ForgotPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/<uid>/<token>/", VerifyEmailView.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
    path('refresh/', TokenRefreshView.as_view()),
    path('me/', MeView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]