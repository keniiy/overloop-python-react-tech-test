from functools import lru_cache
from sqlalchemy.orm import Session

from repositories.article_repository import ArticleRepository
from repositories.author_repository import AuthorRepository
from repositories.region_repository import RegionRepository
from services.article_service import ArticleService
from services.author_service import AuthorService
from services.region_service import RegionService


class DIContainer:
    """Dependency Injection Container for managing service dependencies"""
    
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._services = {}
        self._repositories = {}
    
    # Repository Layer
    
    @lru_cache(maxsize=None)
    def get_article_repository(self) -> ArticleRepository:
        """Get Article repository instance"""
        if 'article_repo' not in self._repositories:
            self._repositories['article_repo'] = ArticleRepository(self._db_session)
        return self._repositories['article_repo']
    
    @lru_cache(maxsize=None)
    def get_author_repository(self) -> AuthorRepository:
        """Get Author repository instance"""
        if 'author_repo' not in self._repositories:
            self._repositories['author_repo'] = AuthorRepository(self._db_session)
        return self._repositories['author_repo']
    
    @lru_cache(maxsize=None)
    def get_region_repository(self) -> RegionRepository:
        """Get Region repository instance"""
        if 'region_repo' not in self._repositories:
            self._repositories['region_repo'] = RegionRepository(self._db_session)
        return self._repositories['region_repo']
    
    # Service Layer
    
    @lru_cache(maxsize=None)
    def get_article_service(self) -> ArticleService:
        """Get Article service instance with all dependencies"""
        if 'article_service' not in self._services:
            self._services['article_service'] = ArticleService(
                self.get_article_repository(),
                self.get_author_repository(),
                self.get_region_repository()
            )
        return self._services['article_service']
    
    @lru_cache(maxsize=None)
    def get_author_service(self) -> AuthorService:
        """Get Author service instance"""
        if 'author_service' not in self._services:
            self._services['author_service'] = AuthorService(
                self.get_author_repository()
            )
        return self._services['author_service']
    
    @lru_cache(maxsize=None)
    def get_region_service(self) -> RegionService:
        """Get Region service instance"""
        if 'region_service' not in self._services:
            self._services['region_service'] = RegionService(
                self.get_region_repository()
            )
        return self._services['region_service']
    
    def clear_cache(self):
        """Clear all cached instances (useful for testing)"""
        self._services.clear()
        self._repositories.clear()
        # Clear lru_cache
        self.get_article_repository.cache_clear()
        self.get_author_repository.cache_clear()
        self.get_region_repository.cache_clear()
        self.get_article_service.cache_clear()
        self.get_author_service.cache_clear()
        self.get_region_service.cache_clear()


# Global container factory
def create_container(db_session: Session) -> DIContainer:
    """Factory function to create DI container"""
    return DIContainer(db_session)