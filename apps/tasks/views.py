from apps.common.views import BaseTenantModelViewSet
from apps.common.rbac import RBACModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import (
    IsOrganizationMember,
    IsAdminOrOwner
)

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(BaseTenantModelViewSet, RBACModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = [IsAuthenticated]

    permission_map = {
        "list": [IsAuthenticated, IsOrganizationMember],
        "retrieve": [IsAuthenticated, IsOrganizationMember],
        "create": [IsAuthenticated, IsOrganizationMember],
        "update": [IsAuthenticated, IsOrganizationMember],
        "partial_update": [IsAuthenticated, IsOrganizationMember],
        "destroy": [IsAuthenticated, IsAdminOrOwner],
        "trash": [IsAuthenticated, IsAdminOrOwner],
        "restore": [IsAuthenticated, IsAdminOrOwner],
    }

    # How to reach organization from Task model
    tenant_field = "project__organization"

    def get_queryset(self):

        queryset = super().get_queryset().select_related(
            "project",
            "assigned_to",
            "created_by",
        )

        project_id = self.request.query_params.get("project")

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset

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

        return Response({"message": "successfully restored"})