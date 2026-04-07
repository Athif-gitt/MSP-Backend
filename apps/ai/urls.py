from django.urls import path
from .views import GenerateSubtasksView

urlpatterns = [
    path("generate-subtasks/", GenerateSubtasksView.as_view()),
]