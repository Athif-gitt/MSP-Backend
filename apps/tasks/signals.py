from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task
from apps.activity.service import log_activity

# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Task


@receiver (post_save, sender=Task)

def log_task_created(sender, instance, created, **kwargs):

    if created:
        log_activity(
            user=instance.created_by,
            organization=instance.project.organization,
            object_type="task",
            object_id=instance.id,
            action="TASK_CREATED",
        )

@receiver(post_save, sender=Task)

def update_task_search_vector(sender, instance, **kwargs):
    Task.objects.filter(id=instance.id).update(
        search_vector=(
            SearchVector("title", weight="A") +
            SearchVector("description", weight="B")
        )
    )