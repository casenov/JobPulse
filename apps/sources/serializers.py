from rest_framework import serializers

from apps.sources.models import ParsingLog, Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = [
            "id", "name", "slug", "source_type", "base_url",
            "rate_limit", "is_active", "last_parsed_at",
        ]
        read_only_fields = ["id", "last_parsed_at"]


class ParsingLogSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = ParsingLog
        fields = [
            "id", "source_name", "status", "parsed_count", "new_count",
            "duplicate_count", "error_message", "started_at", "finished_at",
            "duration_seconds",
        ]
