import json
import itertools

import pytest


def _create_author(client, first_name="Test", last_name="Author"):
    response = client.post(
        '/authors',
        data=json.dumps({"first_name": first_name, "last_name": last_name}),
        content_type='application/json'
    )
    assert response.status_code == 201
    return json.loads(response.data)


_region_code_counter = itertools.count()


def _generate_region_code():
    idx = next(_region_code_counter)
    first = chr(ord('A') + (idx % 26))
    second = chr(ord('A') + ((idx // 26) % 26))
    return f"{first}{second}"


def _create_region(client, code=None, name="Test Region"):
    region_code = code or _generate_region_code()
    response = client.post(
        '/regions',
        data=json.dumps({"code": region_code, "name": name}),
        content_type='application/json'
    )
    assert response.status_code == 201
    return json.loads(response.data)


def _create_article(client, payload):
    response = client.post(
        '/articles',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    return json.loads(response.data)


@pytest.mark.integration
class TestArticleAPI:
    """Integration tests for Article API endpoints."""

    def test_create_article_success(self, client):
        author = _create_author(client)
        region = _create_region(client, code="US", name="United States")

        article_data = {
            "title": "Article Title",
            "content": "This is some valid content for the article.",
            "author_id": author["id"],
            "region_ids": [region["id"]]
        }

        response = client.post(
            '/articles',
            data=json.dumps(article_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["title"] == article_data["title"]
        assert response_data["author"]["id"] == author["id"]
        assert response_data["regions"][0]["id"] == region["id"]

    def test_create_article_validation_error(self, client):
        invalid_data = {
            "title": "abc",
            "content": "short",
        }

        response = client.post(
            '/articles',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert "error" in json.loads(response.data)

    def test_create_article_invalid_author(self, client):
        article_data = {
            "title": "Valid Title",
            "content": "Valid content for the article.",
            "author_id": 9999
        }

        response = client.post(
            '/articles',
            data=json.dumps(article_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        body = json.loads(response.data)
        assert "Author with ID" in body["error"]

    def test_get_articles_with_filters(self, client):
        author_1 = _create_author(client, first_name="Alice", last_name="One")
        author_2 = _create_author(client, first_name="Bob", last_name="Two")

        region_1 = _create_region(client, code="AA", name="Alpha")
        region_2 = _create_region(client, code="BB", name="Beta")

        article_1 = _create_article(client, {
            "title": "First Story",
            "content": "Content for the first story.",
            "author_id": author_1["id"],
            "region_ids": [region_1["id"]]
        })

        _create_article(client, {
            "title": "Second Story",
            "content": "Content for the second story.",
            "author_id": author_2["id"],
            "region_ids": [region_2["id"]]
        })

        response_author = client.get(f'/articles?author_id={author_1["id"]}')
        assert response_author.status_code == 200
        data_author = json.loads(response_author.data)
        assert len(data_author["data"]) == 1
        assert data_author["data"][0]["id"] == article_1["id"]

        response_region = client.get(f'/articles?region_id={region_2["id"]}')
        assert response_region.status_code == 200
        data_region = json.loads(response_region.data)
        assert len(data_region["data"]) == 1
        assert data_region["data"][0]["regions"][0]["id"] == region_2["id"]

        response_search = client.get('/articles?search=Second')
        assert response_search.status_code == 200
        data_search = json.loads(response_search.data)
        assert len(data_search["data"]) == 1
        assert data_search["data"][0]["title"] == "Second Story"

    def test_get_article_by_id_success(self, client):
        author = _create_author(client)
        article = _create_article(client, {
            "title": "Single Story",
            "content": "Singular article content.",
            "author_id": author["id"]
        })

        response = client.get(f'/articles/{article["id"]}')
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["id"] == article["id"]
        assert body["title"] == "Single Story"

    def test_get_article_by_id_not_found(self, client):
        response = client.get('/articles/99999')
        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_update_article_success(self, client):
        author = _create_author(client, first_name="Update", last_name="Author")
        region = _create_region(client, code="CC", name="Gamma")

        article = _create_article(client, {
            "title": "Original Title",
            "content": "Original content for article.",
            "author_id": author["id"],
            "region_ids": [region["id"]]
        })

        new_region = _create_region(client, code="DD", name="Delta")

        update_payload = {
            "title": "Updated Title",
            "content": "Updated content for article.",
            "author_id": author["id"],
            "region_ids": [new_region["id"]]
        }

        response = client.put(
            f'/articles/{article["id"]}',
            data=json.dumps(update_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        updated = json.loads(response.data)
        assert updated["title"] == "Updated Title"
        assert updated["regions"][0]["id"] == new_region["id"]

    def test_update_article_not_found(self, client):
        update_payload = {
            "title": "Does Not Exist",
            "content": "Irrelevant content.",
            "author_id": None,
            "region_ids": []
        }

        response = client.put(
            '/articles/99999',
            data=json.dumps(update_payload),
            content_type='application/json'
        )

        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_delete_article_success(self, client):
        article = _create_article(client, {
            "title": "Delete Me",
            "content": "Delete me content."
        })

        delete_response = client.delete(f'/articles/{article["id"]}')
        assert delete_response.status_code == 200
        assert json.loads(delete_response.data)["message"] == "Article deleted successfully"

        follow_up = client.get(f'/articles/{article["id"]}')
        assert follow_up.status_code == 404

    def test_delete_article_not_found(self, client):
        response = client.delete('/articles/99999')
        assert response.status_code == 404
        assert "error" in json.loads(response.data)

    def test_article_content_type_validation(self, client):
        article_data = {
            "title": "No Content Type",
            "content": "This request lacks a content type header."
        }

        response = client.post(
            '/articles',
            data=json.dumps(article_data)
        )

        assert response.status_code == 400
        assert "error" in json.loads(response.data)
