from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from apps.organizations.models import Membership

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.organizations.models import Membership


class IsOrganizationMember(BasePermission):

    def has_permission(self, request, view):

        organization = getattr(request, "organization", None)

        if not organization:
            raise PermissionDenied("Organization not set")

        if not request.user or not request.user.is_authenticated:
            return False

        is_member = Membership.objects.filter(
            user=request.user,
            organization=organization
        ).exists()

        if not is_member:
            raise PermissionDenied("Not a member of this organization")

        return True

# class IsOrganizationMember(BasePermission):

#     def has_permission(self, request, view):

#         return Membership.objects.filter(
#             user=request.user,
#             organization=request.organization
#         ).exists()

class IsAdminOrOwner(BasePermission):

    def has_permission(self, request, view):

        membership = Membership.objects.filter(
            user=request.user,
            organization=request.organization
        ).first()

        if not membership:
            return False

        return membership.role.upper() in ["OWNER", "ADMIN"]
    
class IsOwner(BasePermission):

    def has_permission(self, request, view):

        membership = Membership.objects.filter(
            user=request.user,
            organization=request.organization
        ).first()

        return membership and membership.role.upper() == "OWNER"
