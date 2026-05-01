"""
Tests for Vacancies API endpoints.
"""

import pytest


@pytest.mark.django_db
class TestVacancyListView:
    url = "/api/v1/vacancies/"

    def test_list_returns_200(self, api_client, vacancy):
        resp = api_client.get(self.url)
        assert resp.status_code == 200

    def test_list_pagination(self, api_client, vacancy):
        resp = api_client.get(self.url)
        data = resp.json()
        assert "results" in data
        assert "count" in data
        assert "total_pages" in data

    def test_filter_by_work_format(self, api_client, vacancy):
        resp = api_client.get(self.url, {"work_format": "remote"})
        assert resp.status_code == 200
        results = resp.json()["results"]
        for v in results:
            assert v["work_format"] == "remote"

    def test_filter_by_experience_level(self, api_client, vacancy):
        resp = api_client.get(self.url, {"experience_level": "middle"})
        assert resp.status_code == 200

    def test_search_by_title(self, api_client, vacancy):
        resp = api_client.get(self.url, {"search": "Python"})
        assert resp.status_code == 200

    def test_soft_deleted_not_shown(self, api_client, vacancy):
        vacancy.delete()  # soft delete
        resp = api_client.get(self.url)
        ids = [v["id"] for v in resp.json()["results"]]
        assert str(vacancy.id) not in ids


@pytest.mark.django_db
class TestVacancyDetailView:
    def test_detail_returns_200(self, api_client, vacancy):
        resp = api_client.get(f"/api/v1/vacancies/{vacancy.id}/")
        assert resp.status_code == 200
        assert resp.json()["title"] == vacancy.title

    def test_detail_returns_404_for_deleted(self, api_client, vacancy):
        vacancy.delete()
        resp = api_client.get(f"/api/v1/vacancies/{vacancy.id}/")
        assert resp.status_code == 404


@pytest.mark.django_db
class TestVacancyStatsView:
    def test_stats_returns_200(self, api_client, vacancy):
        resp = api_client.get("/api/v1/vacancies/stats/")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "by_experience_level" in data
        assert "by_work_format" in data
