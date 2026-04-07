from django.contrib.postgres.search import SearchQuery, SearchRank
from apps.projects.models import Project
from apps.tasks.models import Task

def global_search(user, query):
    search_query = SearchQuery(query)

    org = user.memberships.first().organization

    projects = (
        Project.objects
        .filter(organization=org)
        .annotate(rank=SearchRank("search_vector", search_query))
        # .filter(rank__gte=0)
        .order_by("-rank")[:5]
    )

    tasks = (
        Task.objects
        .filter(project__organization=org)
        .annotate(rank=SearchRank("search_vector", search_query))
        # .filter(rank__gte=0)
        .order_by("-rank")[:5]
    )

    return projects, tasks