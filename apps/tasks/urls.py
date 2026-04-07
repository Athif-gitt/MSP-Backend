from .views import TaskViewSet, BulkCreateSubtasksView
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.tasks.views1.comment_views import TaskCommentViewSet

router = DefaultRouter()

router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = router.urls

comment_list = TaskCommentViewSet.as_view({
    "get": "list",
    "post": "create",
})

comment_detail = TaskCommentViewSet.as_view({
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns += [
    path("tasks/<uuid:task_id>/comments/", comment_list, name="task-comments"),
    path("comments/<uuid:pk>/", comment_detail, name="comment-detail"),
    path("bulk-create-subtasks/", BulkCreateSubtasksView.as_view()),
]



