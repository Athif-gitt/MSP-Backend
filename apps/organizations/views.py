from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationCreateSerializer, OrganizationSerializer, InvitationCreateSerializer, InvitationSerializer, AcceptInvitationSerializer
from .services.organization_service import OrganizationService
from .models import OrganizationInvitation
from .tasks import send_invitation_email
from apps.common.permissions import IsAdminOrOwner
# from .services import accept_invitation
from apps.organizations.services.invitation_service import accept_invitation

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
    
class InviteMemberView(APIView):

    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def post(self, request):

        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = OrganizationInvitation.objects.create(
            organization=request.organization,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
            invited_by=request.user
        )

        send_invitation_email.delay(
            invitation.email,
            str(invitation.token)
        )

        return Response({"message": "Invitation sent"})
    
class InvitationListView(APIView):

    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get(self, request):

        invitations = OrganizationInvitation.objects.filter(
            organization=request.organization,
            accepted=False
        )

        serializer = InvitationSerializer(invitations, many=True)

        return Response(serializer.data)
    

class AcceptInvitationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accept_invitation(
            serializer.validated_data["token"],
            request.user
        )

        return Response({"message": "Invitation accepted"})
    

        