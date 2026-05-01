from django.urls import path

from apps.vacancies.views import VacancyDetailView, VacancyListView, VacancyStatsView

urlpatterns = [
    path("", VacancyListView.as_view(), name="vacancy-list"),
    path("stats/", VacancyStatsView.as_view(), name="vacancy-stats"),
    path("<uuid:id>/", VacancyDetailView.as_view(), name="vacancy-detail"),
]
