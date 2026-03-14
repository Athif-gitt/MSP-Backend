import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Organization(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_organizations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Membership(models.Model):

    ROLE_OWNER = "OWNER"
    ROLE_ADMIN = "ADMIN"
    ROLE_MEMBER = "MEMBER"

    ROLE_CHOICES = (
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"
    
class OrganizationInvitation(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="invitations"
    )

    email = models.EmailField()

    role = models.CharField(
        max_length=20,
        choices=[
            ("ADMIN", "Admin"),
            ("MEMBER", "Member"),
        ]
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations"
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ["organization", "email"]
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)

        super().save(*args, **kwargs)