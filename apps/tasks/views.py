from django.contrib.auth import get_user_model

from apps.common.views import BaseTenantModelViewSet
from apps.common.rbac import RBACModelViewSet

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.common.permissions import (
    IsOrganizationMember,
    IsAdminOrOwner
)

from .models import Task
from .serializers import TaskSerializer
from .services.task_service import assign_task


User = get_user_model()


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
        "bulk_restore": [IsAuthenticated, IsAdminOrOwner],
        "hard_delete": [IsAuthenticated, IsAdminOrOwner],
        "bulk_hard_delete": [IsAuthenticated, IsAdminOrOwner],
        "empty_trash": [IsAuthenticated, IsAdminOrOwner],
        "assign": [IsAuthenticated, IsOrganizationMember],  # ✅ ADDED
    }

    # Tenant isolation
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

    # -------------------------------
    # Trash
    # -------------------------------
    @action(detail=False, methods=["get"])
    def trash(self, request):
        tasks = Task.all_objects.filter(
            is_deleted=True,
            project__organization=request.organization
        )

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    # -------------------------------
    # Restore
    # -------------------------------
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        task = Task.all_objects.get(
            pk=pk,
            project__organization=request.organization
        )

        task.restore()
        return Response({"message": "successfully restored"})

    @action(detail=False, methods=["post"], url_path="bulk-restore")
    def bulk_restore(self, request):
        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {"detail": "ids is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        restored_count = Task.all_objects.filter(
            id__in=ids,
            is_deleted=True,
            project__organization=request.organization,
        ).restore()

        return Response({"restored": restored_count})

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        task = Task.all_objects.get(
            pk=pk,
            is_deleted=True,
            project__organization=request.organization,
        )
        task.hard_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"], url_path="bulk-hard-delete")
    def bulk_hard_delete(self, request):
        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {"detail": "ids is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = Task.all_objects.filter(
            id__in=ids,
            is_deleted=True,
            project__organization=request.organization,
        ).hard_delete()

        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["delete"], url_path="empty_trash")
    def empty_trash(self, request):
        deleted_count, _ = Task.all_objects.filter(
            is_deleted=True,
            project__organization=request.organization,
        ).hard_delete()

        return Response({"deleted": deleted_count})

    # -------------------------------
    # Assign Task (🔥 NEW)
    # -------------------------------
    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        task = self.get_object()

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=400
            )

        try:
            assigned_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        # Optional safety check (recommended)
        if task.project.organization != request.organization:
            raise PermissionDenied("Invalid organization")

        assign_task(
            task=task,
            assigned_user=assigned_user,
            assigned_by=request.user
        )

        return Response({
            "message": "Task assigned successfully"
        })
