from django.urls import include, path

urlpatterns = [
    path("vacancies/", include("apps.vacancies.urls")),
    path("sources/", include("apps.sources.urls")),
    path("filters/", include("apps.filters.urls")),
    path("users/", include("apps.users.urls")),
]
