from django.urls import path
from .api.search import GlobalSearchView

urlpatterns = [
    path("", GlobalSearchView.as_view()),
]