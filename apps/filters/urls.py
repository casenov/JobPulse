from django.urls import path

from apps.filters.views import UserFilterDetailView, UserFilterListCreateView

urlpatterns = [
    path("", UserFilterListCreateView.as_view(), name="filter-list-create"),
    path("<int:pk>/", UserFilterDetailView.as_view(), name="filter-detail"),
]
