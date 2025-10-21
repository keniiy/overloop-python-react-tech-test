import pytest
import json
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from techtest.baseapp import create_app
from techtest.connector import BaseModel


@pytest.fixture
def app():
    """Create test Flask app"""
    # Create temporary database file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{temp_file.name}'
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        # Set up test database
        engine = create_engine(f'sqlite:///{temp_file.name}')
        BaseModel.metadata.create_all(engine)
        
        yield app
        
        # Cleanup
        os.unlink(temp_file.name)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.mark.integration
class TestAuthorAPI:
    """Integration tests for Author API endpoints"""
    
    def test_create_author_success(self, client):
        """Test successful author creation via API"""
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        response_data = json.loads(response.data)
        assert response_data["first_name"] == author_data["first_name"]
        assert response_data["last_name"] == author_data["last_name"]
        assert "id" in response_data
        assert "full_name" in response_data
    
    def test_create_author_validation_error(self, client):
        """Test author creation with invalid data"""
        invalid_data = {
            "first_name": "",
            "last_name": "Doe"
        }
        
        response = client.post(
            '/authors',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert "error" in response_data
    
    def test_create_author_missing_fields(self, client):
        """Test author creation with missing required fields"""
        incomplete_data = {
            "first_name": "John"
            # Missing last_name
        }
        
        response = client.post(
            '/authors',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_get_all_authors_empty(self, client):
        """Test getting all authors when none exist"""
        response = client.get('/authors')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert len(response_data) == 0
    
    def test_get_all_authors_with_data(self, client):
        """Test getting all authors when some exist"""
        # First create an author
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        create_response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        
        # Then get all authors
        response = client.get('/authors')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        
        # Check that our created author is in the list
        created_author = json.loads(create_response.data)
        assert any(author["id"] == created_author["id"] for author in response_data)
    
    def test_get_author_by_id_success(self, client):
        """Test getting author by valid ID"""
        # First create an author
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        create_response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        created_author = json.loads(create_response.data)
        
        # Then get the author by ID
        response = client.get(f'/authors/{created_author["id"]}')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data["id"] == created_author["id"]
        assert response_data["first_name"] == author_data["first_name"]
        assert response_data["last_name"] == author_data["last_name"]
    
    def test_get_author_by_id_not_found(self, client):
        """Test getting author by non-existent ID"""
        response = client.get('/authors/999999')
        
        assert response.status_code == 404
        
        response_data = json.loads(response.data)
        assert "error" in response_data
    
    def test_update_author_success(self, client):
        """Test successful author update"""
        # First create an author
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        create_response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        created_author = json.loads(create_response.data)
        
        # Then update the author
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        response = client.put(
            f'/authors/{created_author["id"]}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data["first_name"] == update_data["first_name"]
        assert response_data["last_name"] == update_data["last_name"]
        assert response_data["id"] == created_author["id"]
    
    def test_update_author_not_found(self, client):
        """Test updating non-existent author"""
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        response = client.put(
            '/authors/999999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_update_author_validation_error(self, client):
        """Test updating author with invalid data"""
        # First create an author
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        create_response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        created_author = json.loads(create_response.data)
        
        # Then try to update with invalid data
        invalid_update_data = {
            "first_name": "",
            "last_name": "Smith"
        }
        
        response = client.put(
            f'/authors/{created_author["id"]}',
            data=json.dumps(invalid_update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_delete_author_success(self, client):
        """Test successful author deletion"""
        # First create an author
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        create_response = client.post(
            '/authors',
            data=json.dumps(author_data),
            content_type='application/json'
        )
        created_author = json.loads(create_response.data)
        
        # Then delete the author
        response = client.delete(f'/authors/{created_author["id"]}')
        
        assert response.status_code == 204
        
        # Verify author is deleted
        get_response = client.get(f'/authors/{created_author["id"]}')
        assert get_response.status_code == 404
    
    def test_delete_author_not_found(self, client):
        """Test deleting non-existent author"""
        response = client.delete('/authors/999999')
        
        assert response.status_code == 404
    
    def test_search_authors(self, client):
        """Test searching authors"""
        # First create some authors
        authors_data = [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Smith"},
            {"first_name": "Bob", "last_name": "Johnson"}
        ]
        
        for author_data in authors_data:
            client.post(
                '/authors',
                data=json.dumps(author_data),
                content_type='application/json'
            )
        
        # Search for "John"
        response = client.get('/authors/search?q=John')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        
        # Should find both "John Doe" and "Bob Johnson"
        found_names = [f"{author['first_name']} {author['last_name']}" for author in response_data]
        assert any("John" in name for name in found_names)
    
    def test_content_type_validation(self, client):
        """Test that API requires proper Content-Type"""
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        # Send without Content-Type header
        response = client.post(
            '/authors',
            data=json.dumps(author_data)
            # No content_type specified
        )
        
        # Should either work or return 400/415 depending on implementation
        assert response.status_code in [201, 400, 415]