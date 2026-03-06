from apps.common.views import BaseTenantModelViewSet
from rest_framework.exceptions import PermissionDenied
from .models import Task
from .serializers import TaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


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

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def trash(self, request):

        tasks = Task.all_objects.filter(
            is_deleted=True,
            project__organization=request.organization
        )

        serializer = self.get_serializer(tasks, many=True)

        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def restore(self, request, pk):

        task = Task.all_objects.get(
            pk=pk,
            project__organization=request.organization
        )

        task.restore()
        
        return Response({"message": "succesfuly restored"})

    

    