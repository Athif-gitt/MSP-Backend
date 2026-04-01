from apps.common.views import BaseTenantModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=["get"])
    def trash(self, request):
        projects = Project.all_objects.filter(
            is_deleted=True,
            organization=request.organization,
        )
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        project = Project.all_objects.get(
            pk=pk,
            organization=request.organization,
        )
        project.restore()
        return Response({"message": "successfully restored"})



        
