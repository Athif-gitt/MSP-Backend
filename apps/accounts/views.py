from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
from .tokens import email_verification_token


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