"""
pytest configuration and shared fixtures.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="testpass123")


@pytest.fixture
def telegram_user(db, user):
    from apps.users.models import TelegramProfile
    return TelegramProfile.objects.create(
        user=user,
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        notifications_enabled=True,
    )


@pytest.fixture
def source(db):
    from apps.sources.models import Source, SourceType
    return Source.objects.create(
        name="HeadHunter",
        slug="hh",
        source_type=SourceType.API,
        base_url="https://api.hh.ru",
        is_active=True,
    )


@pytest.fixture
def vacancy(db, source):
    from apps.vacancies.models import Vacancy, WorkFormat, ExperienceLevel
    return Vacancy.objects.create(
        external_id="test-001",
        source=source,
        title="Python Backend Developer",
        description="We need a Django developer with REST API experience.",
        company_name="Acme Corp",
        location_raw="Москва",
        location_normalized="Москва",
        work_format=WorkFormat.REMOTE,
        experience_level=ExperienceLevel.MIDDLE,
        salary_from=150000,
        salary_to=250000,
        currency="RUB",
        skills=["python", "django", "rest api"],
        url="https://hh.ru/vacancy/test-001",
    )


@pytest.fixture
def user_filter(db, user):
    from apps.filters.models import UserFilter
    from apps.vacancies.models import WorkFormat, ExperienceLevel
    return UserFilter.objects.create(
        user=user,
        name="Python Jobs",
        keywords=["python", "django"],
        locations=["Москва"],
        work_format=WorkFormat.REMOTE,
        experience_level=ExperienceLevel.MIDDLE,
        salary_min=100000,
        is_active=True,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
