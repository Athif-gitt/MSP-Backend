from .models import ActivityLog

def log_activity(
    *,
    user,
    organization,
    object_type,
    object_id,
    action,
    metadata=None
):

    ActivityLog.objects.create(
        user=user,
        organization=organization,
        object_type=object_type,
        object_id=object_id,
        action=action,
        metadata=metadata or {}
    )