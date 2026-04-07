from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_invitation_email(email, token):

    print("Task Executing")

    invite_url = f"{settings.FRONTEND_URL}/invite/{token}"

    send_mail(
        subject="You're invited to MSP",
        message=f"Join your team:\n\n{invite_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )