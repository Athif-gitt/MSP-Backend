from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from apps.tasks.models import Task, TaskComment
from apps.tasks.serializers.comment_serializer import (
    TaskCommentSerializer,
    CreateTaskCommentSerializer,
)
from apps.common.permissions import IsOrganizationMember


class TaskCommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        queryset = TaskComment.objects.filter(
            task__project__organization=self.request.organization,
            task__is_deleted=False,
        ).select_related("author")

        task_id = self.kwargs.get("task_id")

        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset.order_by("created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return CreateTaskCommentSerializer
        return TaskCommentSerializer

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_id")

        try:
            task = Task.objects.get(
                id=task_id,
                project__organization=self.request.organization,
                is_deleted=False,
            )
        except Task.DoesNotExist:
            raise PermissionDenied("Task not found or access denied")

        serializer.save(task=task, author=self.request.user)

    def perform_update(self, serializer):
        comment = self.get_object()

        # 🔐 Only author can edit
        if comment.author != self.request.user:
            raise PermissionDenied("You cannot edit this comment")

        serializer.save()

    def perform_destroy(self, instance):
        # 🔐 Only author OR admin/owner (optional)
        if instance.author != self.request.user:
            raise PermissionDenied("You cannot delete this comment")

        instance.delete()

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_id")

        task = Task.objects.get(
            id=task_id,
            project__organization=self.request.organization,
            is_deleted=False,
        )

        serializer.save(
            task=task,
            author=self.request.user
        )