from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from apps.projects.models import Project
from apps.tasks.models import Task

class Command(BaseCommand):
    help = "Rebuild search vectors"

    def handle(self, *args, **kwargs):
        self.stdout.write("Updating Projects...")
        Project.objects.update(
            search_vector=(
                SearchVector("name", weight="A") +
                SearchVector("description", weight="B")
            )
        )

        self.stdout.write("Updating Tasks...")
        Task.objects.update(
            search_vector=(
                SearchVector("title", weight="A") +
                SearchVector("description", weight="B")
            )
        )

        self.stdout.write(self.style.SUCCESS("Done"))