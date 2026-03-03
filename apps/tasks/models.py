import uuid
from django.db import models
from django.conf import settings
from apps.projects.models import Project

class Task(models.Model):
    
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_DONE = "DONE"

    STATUS_CHOICES = [
        (STATUS_TODO, "to do"),
        (STATUS_IN_PROGRESS, "in progress"),
        (STATUS_DONE, "Done")
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title