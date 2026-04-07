from datetime import date
from django.db.models import Count, Q

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.organizations.models import Membership


def get_dashboard_metrics(organization, user):
    """
    Aggregates all dashboard metrics for a tenant.
    """

    # Projects
    active_projects = Project.objects.filter(
        organization=organization,
        is_deleted=False
    ).count()

    # Tasks
    tasks_qs = Task.objects.filter(
        project__organization=organization,
        is_deleted=False
    )

    tasks_due_today = tasks_qs.filter(
        due_date=date.today()
    ).count()

    overdue_tasks = tasks_qs.filter(
        due_date__lt=date.today()
    ).exclude(status="DONE").count()

    completed_tasks = tasks_qs.filter(
        status="DONE"
    ).count()

    # Members
    total_members = Membership.objects.filter(
        organization=organization
    ).count()

    return {
        "active_projects": active_projects,
        "tasks_due_today": tasks_due_today,
        "overdue_tasks": overdue_tasks,
        "completed_tasks": completed_tasks,
        "total_members": total_members,
    }