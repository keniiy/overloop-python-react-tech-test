import json

import pytest


def _create_region(client, code="US", name="United States"):
    response = client.post(
        '/regions',
        data=json.dumps({"code": code, "name": name}),
        content_type='application/json'
    )
    assert response.status_code == 201
    return json.loads(response.data)


@pytest.mark.integration
class TestRegionAPI:
    """Integration tests for Region API endpoints."""

    def test_create_region_success(self, client):
        response = client.post(
            '/regions',
            data=json.dumps({"code": "CA", "name": "Canada"}),
            content_type='application/json'
        )

        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["code"] == "CA"
        assert body["name"] == "Canada"

    def test_create_region_validation_error(self, client):
        response = client.post(
            '/regions',
            data=json.dumps({"code": "C1", "name": "C"}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert "error" in json.loads(response.data)

    def test_create_region_duplicate_code(self, client):
        _create_region(client, code="MX", name="Mexico")

        response = client.post(
            '/regions',
            data=json.dumps({"code": "MX", "name": "Duplicate"}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert "already exists" in json.loads(response.data)["error"]

    def test_get_regions_with_search(self, client):
        _create_region(client, code="FR", name="France")
        _create_region(client, code="DE", name="Germany")

        response_all = client.get('/regions')
        assert response_all.status_code == 200
        data_all = json.loads(response_all.data)
        assert len(data_all["data"]) == 2
        assert "pagination" in data_all

        response_filtered = client.get('/regions?search=Fran')
        assert response_filtered.status_code == 200
        data_filtered = json.loads(response_filtered.data)
        assert len(data_filtered["data"]) == 1
        assert data_filtered["data"][0]["name"] == "France"

    def test_get_region_by_id_success(self, client):
        region = _create_region(client, code="IT", name="Italy")

        response = client.get(f'/regions/{region["id"]}')
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["id"] == region["id"]
        assert body["code"] == "IT"

    def test_get_region_by_id_not_found(self, client):
        response = client.get('/regions/9999')
        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_update_region_success(self, client):
        region = _create_region(client, code="ES", name="Spain")

        payload = {"code": "ES", "name": "Reino de España"}
        response = client.put(
            f'/regions/{region["id"]}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        updated = json.loads(response.data)
        assert updated["name"] == "Reino de España"

    def test_update_region_duplicate_code(self, client):
        existing = _create_region(client, code="JP", name="Japan")
        other = _create_region(client, code="KR", name="Korea")

        payload = {"code": existing["code"], "name": "Republic of Korea"}
        response = client.put(
            f'/regions/{other["id"]}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert "already exists" in json.loads(response.data)["error"]

    def test_update_region_not_found(self, client):
        payload = {"code": "CH", "name": "Switzerland"}
        response = client.put(
            '/regions/9999',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_delete_region_success(self, client):
        region = _create_region(client, code="SE", name="Sweden")

        delete_response = client.delete(f'/regions/{region["id"]}')
        assert delete_response.status_code == 200
        assert json.loads(delete_response.data)["message"] == "Region deleted successfully"

    def test_delete_region_not_found(self, client):
        response = client.delete('/regions/9999')
        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_region_content_type_validation(self, client):
        response = client.post(
            '/regions',
            data=json.dumps({"code": "BR", "name": "Brazil"})
        )

        assert response.status_code == 400
        assert "error" in json.loads(response.data)
