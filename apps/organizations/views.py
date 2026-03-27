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

from .models import OrganizationInvitation
from .tasks import send_invitation_email
from apps.common.permissions import IsAdminOrOwner


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