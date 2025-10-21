import pytest
from techtest.repositories.author_repository import AuthorRepository
from techtest.models.author import Author


@pytest.mark.unit
class TestAuthorRepository:
    """Unit tests for AuthorRepository"""
    
    def test_create_author_success(self, author_repository, sample_author_data):
        """Test successful author creation"""
        author = author_repository.create(
            first_name=sample_author_data["first_name"],
            last_name=sample_author_data["last_name"]
        )
        
        assert author is not None
        assert isinstance(author, Author)
        assert author.first_name == sample_author_data["first_name"]
        assert author.last_name == sample_author_data["last_name"]
        assert author.id is not None
    
    def test_get_all_authors(self, author_repository, created_author):
        """Test getting all authors"""
        authors = author_repository.get_all()
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
        assert all(isinstance(author, Author) for author in authors)
    
    def test_get_by_id_success(self, author_repository, created_author):
        """Test getting author by valid ID"""
        author = author_repository.get_by_id(created_author.id)
        
        assert author is not None
        assert isinstance(author, Author)
        assert author.id == created_author.id
        assert author.first_name == created_author.first_name
        assert author.last_name == created_author.last_name
    
    def test_get_by_id_not_found(self, author_repository):
        """Test getting author by non-existent ID"""
        author = author_repository.get_by_id(999999)
        
        assert author is None
    
    def test_update_author_success(self, author_repository, created_author):
        """Test successful author update"""
        updated_author = author_repository.update(
            created_author.id,
            first_name="Jane",
            last_name="Smith"
        )
        
        assert updated_author is not None
        assert updated_author.first_name == "Jane"
        assert updated_author.last_name == "Smith"
        assert updated_author.id == created_author.id
    
    def test_update_author_not_found(self, author_repository):
        """Test updating non-existent author"""
        updated_author = author_repository.update(
            999999,
            first_name="Jane",
            last_name="Smith"
        )
        
        assert updated_author is None
    
    def test_delete_author_success(self, author_repository, created_author):
        """Test successful author deletion"""
        result = author_repository.delete(created_author.id)
        
        assert result is True
        
        # Verify author is deleted
        deleted_author = author_repository.get_by_id(created_author.id)
        assert deleted_author is None
    
    def test_delete_author_not_found(self, author_repository):
        """Test deleting non-existent author"""
        result = author_repository.delete(999999)
        
        assert result is False
    
    def test_exists_true(self, author_repository, created_author):
        """Test exists returns True for existing author"""
        result = author_repository.exists(created_author.id)
        
        assert result is True
    
    def test_exists_false(self, author_repository):
        """Test exists returns False for non-existent author"""
        result = author_repository.exists(999999)
        
        assert result is False
    
    def test_search_by_first_name(self, author_repository, created_author):
        """Test searching by first name"""
        authors = author_repository.search(created_author.first_name)
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
    
    def test_search_by_last_name(self, author_repository, created_author):
        """Test searching by last name"""
        authors = author_repository.search(created_author.last_name)
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
    
    def test_search_by_partial_name(self, author_repository, created_author):
        """Test searching by partial name"""
        # Search for first few characters of first name
        partial_name = created_author.first_name[:3]
        authors = author_repository.search(partial_name)
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
    
    def test_search_case_insensitive(self, author_repository, created_author):
        """Test search is case insensitive"""
        lowercase_name = created_author.first_name.lower()
        authors = author_repository.search(lowercase_name)
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
    
    def test_search_no_results(self, author_repository):
        """Test search with no matching results"""
        authors = author_repository.search("NonExistentName")
        
        assert len(authors) == 0
    
    def test_validate_author_data_valid(self, author_repository):
        """Test validation with valid data"""
        errors = author_repository.validate_author_data("John", "Doe")
        
        assert len(errors) == 0
    
    def test_validate_author_data_empty_first_name(self, author_repository):
        """Test validation with empty first name"""
        errors = author_repository.validate_author_data("", "Doe")
        
        assert len(errors) > 0
        assert any("First name is required" in error for error in errors)
    
    def test_validate_author_data_empty_last_name(self, author_repository):
        """Test validation with empty last name"""
        errors = author_repository.validate_author_data("John", "")
        
        assert len(errors) > 0
        assert any("Last name is required" in error for error in errors)
    
    def test_validate_author_data_whitespace_only(self, author_repository):
        """Test validation with whitespace-only names"""
        errors = author_repository.validate_author_data("   ", "   ")
        
        assert len(errors) >= 2
    
    def test_validate_author_data_too_long(self, author_repository):
        """Test validation with names that are too long"""
        long_name = "a" * 101  # Assuming max length is 100
        errors = author_repository.validate_author_data(long_name, long_name)
        
        # Should have errors for both first and last name if they exceed max length
        assert len(errors) >= 1