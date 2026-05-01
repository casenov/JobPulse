"""
Tests for UserFilter CRUD API.
"""

import pytest


@pytest.mark.django_db
class TestUserFilterAPI:
    url = "/api/v1/filters/"

    def test_unauthenticated_returns_401(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == 401

    def test_authenticated_list(self, auth_client, user_filter):
        resp = auth_client.get(self.url)
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    def test_create_filter(self, auth_client):
        data = {
            "name": "Django Jobs",
            "keywords": ["django", "python"],
            "locations": ["Remote"],
            "work_format": "remote",
            "experience_level": "junior",
            "salary_min": 80000,
            "is_active": True,
            "notify_on_match": True,
        }
        resp = auth_client.post(self.url, data, format="json")
        assert resp.status_code == 201
        assert resp.json()["name"] == "Django Jobs"

    def test_keywords_normalized_to_lowercase(self, auth_client):
        data = {
            "name": "Test",
            "keywords": ["Python", "DJANGO"],
            "excluded_keywords": [],
            "locations": [],
        }
        resp = auth_client.post(self.url, data, format="json")
        assert resp.status_code == 201
        assert "python" in resp.json()["keywords"]
        assert "django" in resp.json()["keywords"]

    def test_update_filter(self, auth_client, user_filter):
        resp = auth_client.patch(
            f"{self.url}{user_filter.id}/",
            {"salary_min": 200000},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["salary_min"] == 200000

    def test_delete_filter(self, auth_client, user_filter):
        resp = auth_client.delete(f"{self.url}{user_filter.id}/")
        assert resp.status_code == 204

    def test_cannot_access_other_users_filter(self, api_client, user_filter, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(email="other@example.com")
        api_client.force_authenticate(user=other_user)
        resp = api_client.get(f"{self.url}{user_filter.id}/")
        assert resp.status_code == 404
