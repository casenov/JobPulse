from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.sources.models import ParsingLog, Source
from apps.sources.serializers import ParsingLogSerializer, SourceSerializer
from core.permissions import IsAdminOrReadOnly


class SourceViewSet(ReadOnlyModelViewSet):
    """
    Управление источниками данных (активные источники, детали, логи парсинга).
    """

    queryset = Source.objects.filter(is_active=True).order_by("name")
    serializer_class = SourceSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=["get"], url_path="logs")
    def logs(self, request, pk=None):
        source = self.get_object()
        logs = ParsingLog.objects.filter(source=source).order_by("-started_at")[:20]
        serializer = ParsingLogSerializer(logs, many=True)
        return Response(serializer.data)
