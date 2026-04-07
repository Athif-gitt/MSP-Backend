from core.events import emit_event


def assign_task(*, task, assigned_user, assigned_by):
    """
    Assign a task to a user and emit notification event
    """

    task.assigned_to = assigned_user
    task.save()

    emit_event(
        "TASK_ASSIGNED",
        {
            "task_id": task.id,
            "assigned_to": assigned_user.id,
            "assigned_by": assigned_by.id,
            "organization_id": task.project.organization.id,
        }
    )

    return task