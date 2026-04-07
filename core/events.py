from apps.notifications.tasks import process_notification_event


def emit_event(event_type: str, payload: dict):
    """
    Entry point for emitting domain events.
    Always async.
    """
    process_notification_event.delay(event_type, payload)

# def emit_event(event_type: str, payload: dict):
#     from apps.notifications.services.notification_service import handle_event
#     handle_event(event_type, payload)