from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.filters.models import UserFilter
from apps.filters.serializers import UserFilterSerializer


class UserFilterListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/filters/   — list own filters
    POST /api/v1/filters/   — create new filter
    """

    serializer_class = UserFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFilter.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/filters/{id}/ — retrieve
    PUT    /api/v1/filters/{id}/ — full update
    PATCH  /api/v1/filters/{id}/ — partial update
    DELETE /api/v1/filters/{id}/ — delete
    """

    serializer_class = UserFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFilter.objects.filter(user=self.request.user)
