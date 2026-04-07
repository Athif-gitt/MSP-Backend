from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        TASK_ASSIGNED = "TASK_ASSIGNED"
        COMMENT_ADDED = "COMMENT_ADDED"
        INVITATION_ACCEPTED = "INVITATION_ACCEPTED"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)

    type = models.CharField(max_length=50, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()

    data = models.JSONField(default=dict, blank=True)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} -> {self.user}"