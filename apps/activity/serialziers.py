from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer:
    class Meta:
        model = ActivityLog
        fields = '__all__'