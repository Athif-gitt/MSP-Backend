from apps.common.views import BaseTenantModelViewSet
from rest_framework.exceptions import PermissionDenied
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(BaseTenantModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # How to reach organization from Task model
    tenant_field = "project__organization"

    def perform_create(self, serializer):

        project = serializer.validated_data["project"]

        if project.organization != self.request.organization:
            raise PermissionDenied(
                "Project does not belong to your organization"
            )

        serializer.save(created_by=self.request.user)