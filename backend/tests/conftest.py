import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from connector import BaseModel
from core.dependencies import DIContainer
from models.author import Author
from models.article import Article
from models.region import Region


@pytest.fixture(scope="function")
def db_session():
    """Database session fixture for isolated testing"""
    # Create temporary in-memory database for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    test_db_url = f"sqlite:///{temp_file.name}"
    engine = create_engine(test_db_url, echo=False)
    
    # Create all tables
    BaseModel.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    os.unlink(temp_file.name)


@pytest.fixture
def di_container(db_session):
    """Dependency injection container fixture"""
    return DIContainer(db_session)


@pytest.fixture
def author_service(di_container):
    """Author service fixture"""
    return di_container.get_author_service()


@pytest.fixture
def article_service(di_container):
    """Article service fixture"""
    return di_container.get_article_service()


@pytest.fixture
def region_service(di_container):
    """Region service fixture"""
    return di_container.get_region_service()


@pytest.fixture
def author_repository(di_container):
    """Author repository fixture"""
    return di_container.get_author_repository()


@pytest.fixture
def article_repository(di_container):
    """Article repository fixture"""
    return di_container.get_article_repository()


@pytest.fixture
def region_repository(di_container):
    """Region repository fixture"""
    return di_container.get_region_repository()


# Sample data fixtures
@pytest.fixture
def sample_author_data():
    """Sample author data for testing"""
    return {
        "first_name": "John",
        "last_name": "Doe"
    }


@pytest.fixture
def sample_article_data():
    """Sample article data for testing"""
    return {
        "title": "Test Article",
        "content": "This is a test article content.",
        "author_id": None  # Will be set in tests
    }


@pytest.fixture
def sample_region_data():
    """Sample region data for testing"""
    return {
        "code": "US",
        "name": "United States"
    }


@pytest.fixture
def created_author(db_session, sample_author_data):
    """Create and return a test author"""
    author = Author(
        first_name=sample_author_data["first_name"],
        last_name=sample_author_data["last_name"]
    )
    db_session.add(author)
    db_session.commit()
    db_session.refresh(author)
    return author


@pytest.fixture
def created_region(db_session, sample_region_data):
    """Create and return a test region"""
    region = Region(
        code=sample_region_data["code"],
        name=sample_region_data["name"]
    )
    db_session.add(region)
    db_session.commit()
    db_session.refresh(region)
    return region


@pytest.fixture
def created_article(db_session, created_author, sample_article_data):
    """Create and return a test article with author"""
    article = Article(
        title=sample_article_data["title"],
        content=sample_article_data["content"],
        author_id=created_author.id
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article