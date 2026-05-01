"""
Tests for data normalizers.
"""

import pytest

from parsers.normalizers import (
    detect_experience_level,
    detect_work_format,
    extract_skills,
    normalize_currency,
    strip_html,
)


class TestStripHtml:
    def test_removes_tags(self):
        assert strip_html("<b>Hello</b> <i>World</i>") == "Hello World"

    def test_collapses_whitespace(self):
        assert strip_html("Hello   World") == "Hello World"

    def test_empty_string(self):
        assert strip_html("") == ""

    def test_none_safe(self):
        assert strip_html(None) == ""


class TestDetectWorkFormat:
    def test_detects_remote(self):
        assert detect_work_format("Senior Python Developer, remote") == "remote"

    def test_detects_hybrid(self):
        assert detect_work_format("Работа в гибридном режиме") == "hybrid"

    def test_detects_onsite(self):
        assert detect_work_format("Работа в офисе, Москва") == "onsite"

    def test_unknown_returns_not_specified(self):
        assert detect_work_format("Senior Developer") == "not_specified"


class TestDetectExperienceLevel:
    def test_detects_junior(self):
        assert detect_experience_level("Junior Python Developer") == "junior"

    def test_detects_middle(self):
        assert detect_experience_level("Middle Backend Engineer") == "middle"

    def test_detects_senior(self):
        assert detect_experience_level("Senior Software Engineer") == "senior"

    def test_detects_lead(self):
        assert detect_experience_level("Team Lead Django") == "lead"

    def test_unknown_returns_not_specified(self):
        assert detect_experience_level("Software Developer") == "not_specified"


class TestExtractSkills:
    def test_extracts_known_skills(self):
        text = "We need Python, Django, PostgreSQL and Docker"
        skills = extract_skills(text)
        assert "python" in skills
        assert "django" in skills
        assert "postgresql" in skills
        assert "docker" in skills

    def test_case_insensitive(self):
        skills = extract_skills("PYTHON DEVELOPER")
        assert "python" in skills

    def test_no_skills_returns_empty(self):
        assert extract_skills("Manager needed") == []


class TestNormalizeCurrency:
    def test_ruble_symbol(self):
        assert normalize_currency("₽") == "RUB"

    def test_rub_text(self):
        assert normalize_currency("руб") == "RUB"

    def test_usd(self):
        assert normalize_currency("USD") == "USD"

    def test_dollar_sign(self):
        assert normalize_currency("$") == "USD"

    def test_empty_returns_rub(self):
        assert normalize_currency("") == "RUB"
