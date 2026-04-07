from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Project


@receiver(post_save, sender=Project)
def update_project_search_vector(sender, instance, **kwargs):
    Project.objects.filter(id=instance.id).update(
        search_vector=(
            SearchVector("name", weight="A") +
            SearchVector("description", weight="B")
        )
    )