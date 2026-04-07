from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def send_verification_email(user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_link = f"http://127.0.0.1:8000/api/auth/verify-email/{uid}/{token}/"

    subject = "Verify your MSP account"

    message = f"""
Click the link below to verify your email:

{verification_link}
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def get_current_user(user):
    return user


def update_current_user(user, data):
    for attr, value in data.items():
        setattr(user, attr, value)

    user.save()
    return user