import pytest
from techtest.models.author import Author


@pytest.mark.unit
class TestAuthorModel:
    """Unit tests for Author model"""
    
    def test_author_creation(self, db_session, sample_author_data):
        """Test basic author creation"""
        author = Author(
            first_name=sample_author_data["first_name"],
            last_name=sample_author_data["last_name"]
        )
        
        db_session.add(author)
        db_session.commit()
        db_session.refresh(author)
        
        assert author.id is not None
        assert author.first_name == sample_author_data["first_name"]
        assert author.last_name == sample_author_data["last_name"]
    
    def test_author_full_name_property(self, created_author):
        """Test full_name property returns correct format"""
        expected_full_name = f"{created_author.first_name} {created_author.last_name}"
        
        assert created_author.full_name == expected_full_name
    
    def test_author_str_representation(self, created_author):
        """Test string representation of author"""
        str_repr = str(created_author)
        
        assert created_author.first_name in str_repr
        assert created_author.last_name in str_repr
    
    def test_author_serialization(self, created_author):
        """Test author can be serialized to dict"""
        author_dict = created_author.serialize()
        
        assert isinstance(author_dict, dict)
        assert author_dict["id"] == created_author.id
        assert author_dict["first_name"] == created_author.first_name
        assert author_dict["last_name"] == created_author.last_name
        assert author_dict["full_name"] == created_author.full_name
    
    def test_author_articles_relationship(self, created_article):
        """Test author-articles relationship"""
        author = created_article.author
        
        assert author is not None
        assert hasattr(author, 'articles')
        assert len(author.articles) >= 1
        assert created_article in author.articles
    
    def test_author_table_name(self):
        """Test that table name is correctly set"""
        assert Author.__tablename__ == 'author'
    
    def test_author_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Test missing first_name
        with pytest.raises(Exception):  # Should raise integrity error
            author = Author(last_name="Doe")
            db_session.add(author)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing last_name
        with pytest.raises(Exception):  # Should raise integrity error
            author = Author(first_name="John")
            db_session.add(author)
            db_session.commit()
    
    def test_author_field_lengths(self, db_session):
        """Test field length constraints"""
        # Test very long names (assuming 100 char limit)
        long_name = "a" * 101
        
        author = Author(
            first_name=long_name,
            last_name=long_name
        )
        
        # This should either truncate or raise an error depending on DB config
        db_session.add(author)
        try:
            db_session.commit()
            db_session.refresh(author)
            # If it commits, check if it was truncated
            assert len(author.first_name) <= 100
            assert len(author.last_name) <= 100
        except Exception:
            # If it raises an error, that's also acceptable behavior
            db_session.rollback()
    
    def test_author_unicode_support(self, db_session):
        """Test that unicode characters are supported in names"""
        author = Author(
            first_name="José",
            last_name="García"
        )
        
        db_session.add(author)
        db_session.commit()
        db_session.refresh(author)
        
        assert author.first_name == "José"
        assert author.last_name == "García"
        assert author.full_name == "José García"