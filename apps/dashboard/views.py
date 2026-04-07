from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.dashboard.services.dashboard_service import get_dashboard_metrics


class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = getattr(request, "organization", None)

        if not organization:
            return Response({"error": "Organization not found"}, status=400)

        data = get_dashboard_metrics(
            organization=organization,
            user=request.user
        )

        return Response(data)