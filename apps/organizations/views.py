from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import OrganizationCreateSerializer, OrganizationSerializer
from .services.organization_service import OrganizationService

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
        