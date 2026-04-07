from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_reset_email(email, reset_link):
    send_mail(
        subject="Reset your password",
        message=f"Click here to reset: {reset_link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
