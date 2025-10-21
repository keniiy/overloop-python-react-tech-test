import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from techtest.services.author_service import AuthorService
from techtest.schemas.author_schemas import CreateAuthorRequest, UpdateAuthorRequest, AuthorResponse
from techtest.models.author import Author
from techtest.core.exceptions import NotFoundError


@pytest.mark.unit
class TestAuthorService:
    """Unit tests for AuthorService"""
    
    def test_create_author_success(self, author_service, sample_author_data):
        """Test successful author creation"""
        create_request = CreateAuthorRequest(**sample_author_data)
        
        result = author_service.create_author(create_request)
        
        assert isinstance(result, AuthorResponse)
        assert result.first_name == sample_author_data["first_name"]
        assert result.last_name == sample_author_data["last_name"]
        assert result.full_name == f"{sample_author_data['first_name']} {sample_author_data['last_name']}"
        assert result.id is not None
    
    def test_create_author_validation_error_empty_first_name(self, author_service):
        """Test author creation with empty first name"""
        with pytest.raises(ValidationError) as exc_info:
            CreateAuthorRequest(first_name="", last_name="Doe")
        
        assert "String should have at least" in str(exc_info.value)
    
    def test_create_author_validation_error_empty_last_name(self, author_service):
        """Test author creation with empty last name"""
        with pytest.raises(ValidationError) as exc_info:
            CreateAuthorRequest(first_name="John", last_name="")
        
        assert "String should have at least" in str(exc_info.value)
    
    def test_create_author_strips_whitespace(self, author_service):
        """Test author creation strips whitespace from names"""
        data_with_whitespace = CreateAuthorRequest(
            first_name="  John  ",
            last_name="  Doe  "
        )
        
        result = author_service.create_author(data_with_whitespace)
        
        assert result.first_name == "John"
        assert result.last_name == "Doe"
    
    def test_get_all_authors(self, author_service, created_author):
        """Test getting all authors"""
        authors = author_service.get_all_authors()
        
        assert len(authors) >= 1
        assert any(author.id == created_author.id for author in authors)
        assert all(isinstance(author, AuthorResponse) for author in authors)
    
    def test_get_author_by_id_success(self, author_service, created_author):
        """Test getting author by valid ID"""
        result = author_service.get_author_by_id(created_author.id)
        
        assert result is not None
        assert isinstance(result, AuthorResponse)
        assert result.id == created_author.id
        assert result.first_name == created_author.first_name
        assert result.last_name == created_author.last_name
    
    def test_get_author_by_id_not_found(self, author_service):
        """Test getting author by non-existent ID"""
        result = author_service.get_author_by_id(999999)
        
        assert result is None
    
    def test_update_author_success(self, author_service, created_author):
        """Test successful author update"""
        update_data = UpdateAuthorRequest(
            first_name="Jane",
            last_name="Smith"
        )
        
        result = author_service.update_author(created_author.id, update_data)
        
        assert result is not None
        assert isinstance(result, AuthorResponse)
        assert result.first_name == "Jane"
        assert result.last_name == "Smith"
        assert result.full_name == "Jane Smith"
    
    def test_update_author_not_found(self, author_service):
        """Test updating non-existent author"""
        update_data = UpdateAuthorRequest(
            first_name="Jane",
            last_name="Smith"
        )
        
        result = author_service.update_author(999999, update_data)
        
        assert result is None
    
    def test_update_author_validation_error(self, author_service, created_author):
        """Test updating author with invalid data"""
        with pytest.raises(ValidationError) as exc_info:
            UpdateAuthorRequest(
                first_name="",
                last_name="Smith"
            )
        
        assert "String should have at least" in str(exc_info.value)
    
    def test_delete_author_success(self, author_service, created_author):
        """Test successful author deletion"""
        result = author_service.delete_author(created_author.id)
        
        assert result is True
    
    def test_delete_author_not_found(self, author_service):
        """Test deleting non-existent author"""
        result = author_service.delete_author(999999)
        
        assert result is False
    
    def test_delete_author_with_articles(self, author_service, created_article):
        """Test deleting author who has articles"""
        # created_article fixture creates an author with an article
        author_id = created_article.author_id
        
        with pytest.raises(ValueError) as exc_info:
            author_service.delete_author(author_id)
        
        assert "Cannot delete author who has written articles" in str(exc_info.value)
    
    def test_search_authors_empty_term(self, author_service, created_author):
        """Test searching with empty term returns all authors"""
        result = author_service.search_authors("")
        
        assert len(result) >= 1
        assert any(author.id == created_author.id for author in result)
    
    def test_search_authors_whitespace_term(self, author_service, created_author):
        """Test searching with whitespace term returns all authors"""
        result = author_service.search_authors("   ")
        
        assert len(result) >= 1
        assert any(author.id == created_author.id for author in result)
    
    def test_search_authors_by_first_name(self, author_service, created_author):
        """Test searching authors by first name"""
        result = author_service.search_authors(created_author.first_name)
        
        assert len(result) >= 1
        assert any(author.id == created_author.id for author in result)
    
    def test_search_authors_by_last_name(self, author_service, created_author):
        """Test searching authors by last name"""
        result = author_service.search_authors(created_author.last_name)
        
        assert len(result) >= 1
        assert any(author.id == created_author.id for author in result)
    
    def test_get_authors_with_article_count_no_articles(self, author_service, created_author):
        """Test getting authors with article count when author has no articles"""
        result = author_service.get_authors_with_article_count()
        
        author_with_count = next((a for a in result if a.id == created_author.id), None)
        assert author_with_count is not None
        assert author_with_count.article_count == 0
    
    def test_get_authors_with_article_count_with_articles(self, author_service, created_article):
        """Test getting authors with article count when author has articles"""
        result = author_service.get_authors_with_article_count()
        
        author_with_count = next((a for a in result if a.id == created_article.author_id), None)
        assert author_with_count is not None
        assert author_with_count.article_count >= 1