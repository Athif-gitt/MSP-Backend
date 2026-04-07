from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Task


@shared_task
def send_due_reminders():
    now = timezone.now()
    tomorrow = now + timedelta(days=1)

    print("Checking for due task reminders...")

    with transaction.atomic():

        tasks = (
            Task.objects
            .select_for_update()
            .filter(
                due_date__isnull=False,
                due_date__lte=tomorrow,
                due_date__gte=now,
                reminder_sent=False
            )
        )

        print(f"{tasks.count()} tasks found")

        for task in tasks:

            if not task.assigned_to:
                continue

            subject = f"Reminder: Task '{task.title}' is due soon"

            message = f"""
Hello,

This is a reminder that your task is due soon.

Task: {task.title}
Description: {task.description}
Due Date: {task.due_date}

Please complete it before the deadline.

— MSP Task Manager
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assigned_to.email],
                fail_silently=False,
            )

            print(f"Email reminder sent for: {task.title}")

            task.reminder_sent = True
            task.save()

    print("Reminder job completed")