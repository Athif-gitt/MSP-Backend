import uuid
from django.db import models
from django.conf import settings
from apps.organizations.models import Organization
from apps.common.models import SoftDeleteModel
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


def generate_public_id():
    return f"MSP-{str(uuid.uuid4())[:8].upper()}"

class Project(SoftDeleteModel):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_projects"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    search_vector = SearchVectorField(null=True)



    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization"]),
            GinIndex(fields=['search_vector']),
        ]

    def save(self, *args, **kwargs):
        if not self.public_id:
            public_id = generate_public_id()

            while Project.all_objects.filter(public_id=public_id).exists():
                public_id = generate_public_id()

            self.public_id = public_id

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
