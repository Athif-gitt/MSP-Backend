from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.organizations.models import Organization

User = get_user_model()


def create_notification(
    *,
    user,
    organization,
    type,
    title,
    message,
    data=None
):
    return Notification.objects.create(
        user=user,
        organization=organization,
        type=type,
        title=title,
        message=message,
        data=data or {}
    )


def handle_event(event_type: str, payload: dict):
    """
    Central event router
    """

    if event_type == "TASK_ASSIGNED":
        _handle_task_assigned(payload)

    elif event_type == "COMMENT_ADDED":
        _handle_comment_added(payload)

    elif event_type == "INVITATION_ACCEPTED":
        _handle_invitation_accepted(payload)


# -------------------------------
# Event Handlers
# -------------------------------

def _handle_task_assigned(payload):
    user = User.objects.get(id=payload["assigned_to"])
    organization = Organization.objects.get(id=payload["organization_id"])

    create_notification(
        user=user,
        organization=organization,
        type="TASK_ASSIGNED",
        title="New Task Assigned",
        message="You have been assigned a new task",
        data=payload
    )


def _handle_comment_added(payload):
    user = User.objects.get(id=payload["user_id"])
    organization = Organization.objects.get(id=payload["organization_id"])

    create_notification(
        user=user,
        organization=organization,
        type="COMMENT_ADDED",
        title="New Comment",
        message="A comment was added",
        data=payload
    )


def _handle_invitation_accepted(payload):
    user = User.objects.get(id=payload["user_id"])
    organization = Organization.objects.get(id=payload["organization_id"])

    create_notification(
        user=user,
        organization=organization,
        type="INVITATION_ACCEPTED",
        title="Invitation Accepted",
        message="A user joined your organization",
        data=payload
    )