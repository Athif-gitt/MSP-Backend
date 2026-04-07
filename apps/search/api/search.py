from rest_framework.views import APIView
from rest_framework.response import Response
from apps.search.services.search_service import global_search
from apps.projects.serializers import ProjectSerializer
from apps.tasks.serializers.task_serializer import TaskSerializer

class GlobalSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q")

        if not query:
            return Response({"projects": [], "tasks": []})

        projects, tasks = global_search(request.user, query)

        return Response({
            "projects": ProjectSerializer(projects, many=True).data,
            "tasks": TaskSerializer(tasks, many=True).data,
        })