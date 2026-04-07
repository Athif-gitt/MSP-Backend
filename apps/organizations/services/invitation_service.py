import uuid
from django.utils.text import slugify

from ..models import Organization, Membership

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from ..models import OrganizationInvitation

import uuid
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from apps.organizations.models import OrganizationInvitation, Membership


INVITE_EXPIRY_DAYS = 3


def create_invitation(*, email, organization, role, invited_by):
    
    # ❌ Prevent duplicate pending invite
    if OrganizationInvitation.objects.filter(
        email=email,
        organization=organization,
        status="PENDING"
    ).exists():
        raise ValueError("User already invited")

    invitation = OrganizationInvitation.objects.create(
        email=email,
        organization=organization,
        role=role,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=INVITE_EXPIRY_DAYS)
    )

    return invitation


def accept_invitation(*, token, user):

    try:
        invitation = OrganizationInvitation.objects.get(token=token)
    except OrganizationInvitation.DoesNotExist:
        raise ValueError("Invalid token")

    # ❌ Already accepted
    if invitation.status == "ACCEPTED":
        return invitation

    # ❌ Expired
    if invitation.expires_at < timezone.now():
        invitation.status = "EXPIRED"
        invitation.save()
        raise ValueError("Invitation expired")

    # ❌ Email mismatch
    if invitation.email != user.email:
        raise ValueError("This invite is not for this user")

    with transaction.atomic():

        # Prevent duplicate membership
        if Membership.objects.filter(
            user=user,
            organization=invitation.organization
        ).exists():
            raise ValueError("Already a member")

        Membership.objects.create(
            user=user,
            organization=invitation.organization,
            role=invitation.role
        )

        invitation.status = "ACCEPTED"
        invitation.save()

    return invitation