from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.filters.models import UserFilter
from apps.filters.serializers import UserFilterSerializer


class UserFilterListCreateView(generics.ListCreateAPIView):
    """
    Список фильтров пользователя и создание новых фильтров.
    """

    serializer_class = UserFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserFilter.objects.none()
        return UserFilter.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, обновление и удаление конкретного фильтра пользователя.
    """

    serializer_class = UserFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFilter.objects.filter(user=self.request.user)
