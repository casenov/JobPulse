from rest_framework import serializers

from apps.filters.models import UserFilter


class UserFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFilter
        fields = [
            "id", "name", "keywords", "excluded_keywords",
            "locations", "work_format", "experience_level",
            "salary_min", "is_active", "notify_on_match",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_keywords(self, value):
        return [kw.lower().strip() for kw in value if kw.strip()]

    def validate_excluded_keywords(self, value):
        return [kw.lower().strip() for kw in value if kw.strip()]
