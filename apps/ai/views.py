from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task
from apps.ai.services.llm_service import generate_subtasks


class GenerateSubtasksView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get("task_id")
        priority_hint = request.data.get("priority_hint", "")

        organization = request.organization

        task = Task.objects.filter(
        id=task_id,
    project__organization=organization
).first()

        if not task:
            return Response({"error": "Task not found"}, status=400)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        subtasks = generate_subtasks(
            task_title=task.title,
            priority_hint=priority_hint
        )

        return Response({"subtasks": subtasks})