from django.utils.deprecation import MiddlewareMixin
from apps.organizations.models import Organization, Membership
from rest_framework.exceptions import PermissionDenied


from django.utils.deprecation import MiddlewareMixin
from apps.organizations.models import Membership


class OrganizationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.organization = None

        org_id = request.META.get("HTTP_X_ORGANIZATION_ID")

        if not org_id:
            return

        # ❗ DO NOT check request.user here
        # Because JWT auth not applied yet

        membership = Membership.objects.filter(
            organization_id=org_id
        ).select_related("organization").first()

        if membership:
            request.organization = membership.organization