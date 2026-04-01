from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .tokens import email_verification_token

from .serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer
)
from .services import get_current_user, update_current_user

from .models import PasswordReset

from .tasks import send_reset_email



User = get_user_model()


# REGISTER VIEW
class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# EMAIL VERIFICATION VIEW
class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, uid, token):

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):

            return Response(
                {"message": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email_verification_token.check_token(user, token):

            user.is_active = True
            user.save()

            return Response(
                {"message": "Email verified successfully"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Invalid or expired token"},
            status=status.HTTP_400_BAD_REQUEST
        )


# LOGIN VIEW
class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )
    
class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):


        user = request.user
        serializer = UserSerializer(
            user,
            context ={"request": request}
            )

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        user = update_current_user(
            request.user,
            serializer.validated_data
        )

        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_202_ACCEPTED
        )

User = get_user_model()

class ForgotPasswordView(APIView):
    # permission_classes = []

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If account exists, email sent"}, status=200)
        
        reset = PasswordReset.objects.create(user=user)

        reset_link = f"http://localhost:5173/reset-password?token={reset.token}"

        send_reset_email.delay(user.email, reset_link)

        return Response({"detail": "Password reset email sent"})
    
class ResetPasswordView(APIView):

    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("password")

        try:
            reset = PasswordReset.objects.get(token=token, is_used=False)
        except PasswordReset.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=400)

        if reset.is_expired():
            return Response({"detail": "Token expired"}, status=400)

        user = reset.user
        user.set_password(password)
        user.save()

        reset.is_used = True
        reset.save()

        return Response({"detail": "Password reset successful"})



