from celery import shared_task
from .services.notification_service import handle_event


@shared_task(bind=True, max_retries=3)
def process_notification_event(self, event_type, payload):
    try:
        handle_event(event_type, payload)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)