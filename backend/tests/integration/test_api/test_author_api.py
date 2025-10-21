import pytest
import json


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
    
    def test_get_all_authors_structure(self, client):
        """Test getting all authors returns correct structure"""
        response = client.get('/authors')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert isinstance(response_data, dict)
        assert 'data' in response_data
        assert 'pagination' in response_data
        assert isinstance(response_data['data'], list)
        
        # Check pagination structure
        pagination = response_data['pagination']
        assert 'current_page' in pagination
        assert 'per_page' in pagination
        assert 'total_items' in pagination
        assert 'total_pages' in pagination
        assert 'has_next' in pagination
        assert 'has_prev' in pagination
    
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
        assert isinstance(response_data, dict)
        assert 'data' in response_data
        assert 'pagination' in response_data
        assert isinstance(response_data['data'], list)
        assert len(response_data['data']) >= 1
        
        # Check that our created author is in the list
        created_author = json.loads(create_response.data)
        assert any(author["id"] == created_author["id"] for author in response_data['data'])
    
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
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'message' in response_data
        
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
        
        # Search for "John" using new pagination endpoint
        response = client.get('/authors?search=John')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert isinstance(response_data, dict)
        assert 'data' in response_data
        assert 'pagination' in response_data
        assert isinstance(response_data['data'], list)
        assert len(response_data['data']) >= 1
        
        # Should find both "John Doe" and "Bob Johnson"
        found_names = [f"{author['first_name']} {author['last_name']}" for author in response_data['data']]
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
    
    def test_pagination_parameters(self, client):
        """Test pagination parameters work correctly"""
        # Create multiple authors
        for i in range(5):
            author_data = {
                "first_name": f"Author{i}",
                "last_name": f"Test{i}"
            }
            client.post(
                '/authors',
                data=json.dumps(author_data),
                content_type='application/json'
            )
        
        # Test page size limit
        response = client.get('/authors?limit=2')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert len(response_data['data']) <= 2
        assert response_data['pagination']['per_page'] == 2
        assert response_data['pagination']['current_page'] == 1
        
        # Test page 2
        response = client.get('/authors?page=2&limit=2')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['pagination']['current_page'] == 2
        assert response_data['pagination']['per_page'] == 2
    
    def test_pagination_metadata(self, client):
        """Test pagination metadata is correct"""
        # Create exactly 3 authors
        for i in range(3):
            author_data = {
                "first_name": f"Test{i}",
                "last_name": f"Author{i}"
            }
            client.post(
                '/authors',
                data=json.dumps(author_data),
                content_type='application/json'
            )
        
        response = client.get('/authors?limit=2')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        pagination = response_data['pagination']
        
        assert pagination['total_items'] == 3
        assert pagination['per_page'] == 2
        assert pagination['total_pages'] == 2
        assert pagination['current_page'] == 1
        assert pagination['has_next'] == True
        assert pagination['has_prev'] == False
        assert pagination['next_page'] == 2
        assert pagination['prev_page'] is None
