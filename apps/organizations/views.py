from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    OrganizationCreateSerializer,
    OrganizationSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
    AcceptInvitationSerializer
)

from .services.organization_service import OrganizationService
from apps.organizations.services.invitation_service import (
    create_invitation,
    accept_invitation
)

from .models import OrganizationInvitation, Membership
from .tasks import send_invitation_email
from apps.common.permissions import IsAdminOrOwner
from .serializers import MemberSerializer

from django.utils import timezone



# ==============================
# ORGANIZATION CREATE
# ==============================

class OrganizationCreateView(generics.GenericAPIView):
    serializer_class = OrganizationCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = OrganizationService.create_organization(
            user=request.user,
            name=serializer.validated_data["name"],
        )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_201_CREATED
        )


# ==============================
# INVITE MEMBER
# ==============================

class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def post(self, request):
        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitation = create_invitation(
                email=serializer.validated_data["email"],
                organization=request.organization,
                role=serializer.validated_data["role"],
                invited_by=request.user
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Async email
        send_invitation_email.delay(
            invitation.email,
            str(invitation.token)
        )

        return Response(
            {"message": "Invitation sent"},
            status=status.HTTP_201_CREATED
        )


# ==============================
# LIST INVITATIONS
# ==============================

class InvitationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get(self, request):
        invitations = OrganizationInvitation.objects.filter(
            organization=request.organization,
            status="PENDING"   # ✅ FIXED
        ).order_by("-created_at")

        serializer = InvitationSerializer(invitations, many=True)

        return Response(serializer.data)


# ==============================
# ACCEPT INVITATION
# ==============================

class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            accept_invitation(
                token=serializer.validated_data["token"],
                user=request.user
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Invitation accepted"},
            status=status.HTTP_200_OK
        )
    
class ValidateInvitationView(APIView):

    permission_classes = []  

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Token is required"},
                status=400
            )

        try:
            invitation = OrganizationInvitation.objects.select_related(
                "organization"
            ).get(token=token)
        except OrganizationInvitation.DoesNotExist:
            return Response({"error": "Invalid invitation"}, status=404)
        
        if invitation.expires_at < timezone.now():
            return Response({"error": "Invitation expired"}, status=400)

        # ❌ Already accepted
        if invitation.status == "ACCEPTED":
            return Response({"error": "Invitation already accepted"}, status=400)

        return Response({
            "email": invitation.email,
            "organization": invitation.organization.name,
            "organization_name": invitation.organization.name,
            "role": invitation.role,
            "invited_by_email": invitation.invited_by.email,
            "expires_at": invitation.expires_at,
        })
    
class OrganizationMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.organization

        members = Membership.objects.filter(organization=org).select_related("user")

        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
