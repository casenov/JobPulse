"""
Tests for Matching Engine scoring functions.
"""

import pytest

from apps.matching.scoring import (
    compute_score,
    score_experience,
    score_keywords,
    score_location,
    score_salary,
)


@pytest.mark.django_db
class TestKeywordScoring:
    def test_match_single_keyword(self, vacancy, user_filter):
        user_filter.keywords = ["python"]
        score = score_keywords(vacancy, user_filter)
        assert score == 1.0

    def test_match_multiple_keywords(self, vacancy, user_filter):
        user_filter.keywords = ["python", "django", "react"]
        # vacancy has python and django → 2/3
        score = score_keywords(vacancy, user_filter)
        assert score == pytest.approx(2 / 3, rel=0.01)

    def test_no_keywords_returns_full_score(self, vacancy, user_filter):
        user_filter.keywords = []
        assert score_keywords(vacancy, user_filter) == 1.0

    def test_excluded_keyword_returns_zero(self, vacancy, user_filter):
        user_filter.keywords = ["python"]
        user_filter.excluded_keywords = ["django"]
        assert score_keywords(vacancy, user_filter) == 0.0

    def test_no_match_returns_zero(self, vacancy, user_filter):
        user_filter.keywords = ["java", "spring"]
        assert score_keywords(vacancy, user_filter) == 0.0


@pytest.mark.django_db
class TestLocationScoring:
    def test_remote_always_matches(self, vacancy, user_filter):
        from apps.vacancies.models import WorkFormat
        vacancy.work_format = WorkFormat.REMOTE
        assert score_location(vacancy, user_filter) == 1.0

    def test_matching_location(self, vacancy, user_filter):
        from apps.vacancies.models import WorkFormat
        vacancy.work_format = WorkFormat.ONSITE
        user_filter.locations = ["Москва"]
        assert score_location(vacancy, user_filter) == 1.0

    def test_non_matching_location(self, vacancy, user_filter):
        from apps.vacancies.models import WorkFormat
        vacancy.work_format = WorkFormat.ONSITE
        vacancy.location_normalized = "Новосибирск"
        user_filter.locations = ["Москва"]
        assert score_location(vacancy, user_filter) == 0.0

    def test_no_location_preference(self, vacancy, user_filter):
        user_filter.locations = []
        assert score_location(vacancy, user_filter) == 1.0


@pytest.mark.django_db
class TestSalaryScoring:
    def test_meets_minimum(self, vacancy, user_filter):
        user_filter.salary_min = 100000
        vacancy.salary_to = 250000
        assert score_salary(vacancy, user_filter) == 1.0

    def test_below_minimum_partial(self, vacancy, user_filter):
        user_filter.salary_min = 300000
        vacancy.salary_from = 150000
        vacancy.salary_to = 200000
        score = score_salary(vacancy, user_filter)
        assert 0.0 < score < 1.0

    def test_no_salary_preference(self, vacancy, user_filter):
        user_filter.salary_min = None
        assert score_salary(vacancy, user_filter) == 1.0

    def test_no_salary_disclosed(self, vacancy, user_filter):
        user_filter.salary_min = 100000
        vacancy.salary_from = None
        vacancy.salary_to = None
        assert score_salary(vacancy, user_filter) == 0.5


@pytest.mark.django_db
class TestExperienceScoring:
    def test_exact_match(self, vacancy, user_filter):
        from apps.vacancies.models import ExperienceLevel
        vacancy.experience_level = ExperienceLevel.MIDDLE
        user_filter.experience_level = ExperienceLevel.MIDDLE
        assert score_experience(vacancy, user_filter) == 1.0

    def test_no_match(self, vacancy, user_filter):
        from apps.vacancies.models import ExperienceLevel
        vacancy.experience_level = ExperienceLevel.SENIOR
        user_filter.experience_level = ExperienceLevel.JUNIOR
        assert score_experience(vacancy, user_filter) == 0.0

    def test_no_preference(self, vacancy, user_filter):
        user_filter.experience_level = None
        assert score_experience(vacancy, user_filter) == 1.0


@pytest.mark.django_db
class TestComputeScore:
    def test_perfect_match(self, vacancy, user_filter):
        result = compute_score(vacancy, user_filter)
        assert result.total > 0.7

    def test_score_dataclass_fields(self, vacancy, user_filter):
        result = compute_score(vacancy, user_filter)
        assert hasattr(result, "keyword")
        assert hasattr(result, "location")
        assert hasattr(result, "salary")
        assert hasattr(result, "experience")
        assert 0.0 <= result.total <= 1.0
