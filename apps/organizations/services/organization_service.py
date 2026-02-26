import uuid
from django.db import transaction
from django.utils.text import slugify

from apps.organizations.models import Organization, Membership


class OrganizationService:

    @staticmethod
    @transaction.atomic
    def create_organization(*, user, name: str) -> Organization:
        """
        Creates organization and assigns owner membership.
        Runs inside database transaction.
        """

        # generate unique slug
        base_slug = slugify(name)
        slug = base_slug

        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # create organization
        organization = Organization.objects.create(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            owner=user,
        )

        # create membership
        Membership.objects.create(
            user=user,
            organization=organization,
            role=Membership.ROLE_OWNER,
        )

        return organization