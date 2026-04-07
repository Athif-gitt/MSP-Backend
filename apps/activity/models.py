import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ActivityLog(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE
    )

    object_type = models.CharField(max_length=50)
    object_id = models.UUIDField()

    action = models.CharField(max_length=100)

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]