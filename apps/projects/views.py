from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.common.views import BaseTenantModelViewSet

from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(BaseTenantModelViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    tenant_field = "organization"

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user
        )



        