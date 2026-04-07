from rest_framework import generics
from .models import ActivityLog
from .serialziers import ActivityLogSerializer

class ActivityListView(generics.ListAPIView):

    serializer_class = ActivityLogSerializer

    def get_queryset(self):

        organization = self.request.organization

        return ActivityLog.objects.filter(
            organization = organization,
        )