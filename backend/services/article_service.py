from typing import List, Optional, Dict, Any, Tuple, cast
from repositories.article_repository import ArticleRepository
from repositories.author_repository import AuthorRepository
from repositories.region_repository import RegionRepository
from schemas.article_schemas import CreateArticleRequest, UpdateArticleRequest


class ArticleService:
    """Service layer for Article business logic with relationship handling"""

    def __init__(self,
                 article_repository: ArticleRepository,
                 author_repository: AuthorRepository,
                 region_repository: RegionRepository):
        self.article_repository = article_repository
        self.author_repository = author_repository
        self.region_repository = region_repository

    def get_all_articles(self) -> List[Dict[str, Any]]:
        """Get all articles with author and regions"""
        articles = self.article_repository.get_all_with_relations()
        return [self._serialize_article(article) for article in articles if article]

    def get_all_articles_paginated(self, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get all articles with pagination"""
        articles, total = self.article_repository.get_all_paginated(offset, limit)
        article_data = [self._serialize_article(article) for article in articles]
        return article_data, total

    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get article by ID with relationships"""
        article = self.article_repository.get_by_id_with_relations(article_id)
        return self._serialize_article(article) if article else None

    def create_article(self, article_request: CreateArticleRequest) -> Dict[str, Any]:
        """Create new article with author and regions"""
        title = article_request.title
        content = article_request.content
        author_id = article_request.author_id
        region_ids = article_request.region_ids or []

        # Validate related entities
        errors = self._validate_article_relations(author_id, region_ids)
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")

        # Create article
        article = self.article_repository.create_with_regions(
            title=title,
            content=content,
            author_id=author_id,
            region_ids=region_ids
        )

        # Reload with relationships
        reloaded_article = self.article_repository.get_by_id_with_relations(cast(int, article.id))
        if not reloaded_article:
            raise ValueError("Failed to reload created article")
        return self._serialize_article(reloaded_article)

    def update_article(self, article_id: int, article_request: UpdateArticleRequest) -> Optional[Dict[str, Any]]:
        """Update existing article"""
        if not self.article_repository.exists(article_id):
            return None

        title = article_request.title
        content = article_request.content
        author_id = article_request.author_id
        region_ids = article_request.region_ids

        # Validate related entities
        errors = self._validate_article_relations(author_id, region_ids or [])
        if errors:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")

        # Update article
        article = self.article_repository.update(
            article_id,
            title=title,
            content=content,
            author_id=author_id
        )

        # Update regions
        if article and region_ids is not None:
            article = self.article_repository.update_regions(article_id, region_ids)

        # Reload with relationships
        article = self.article_repository.get_by_id_with_relations(article_id)
        return self._serialize_article(article) if article else None

    def delete_article(self, article_id: int) -> bool:
        """Delete article"""
        return self.article_repository.delete(article_id)

    def get_articles_by_author(self, author_id: int) -> List[Dict[str, Any]]:
        """Get all articles by specific author"""
        if not self.author_repository.exists(author_id):
            raise ValueError(f"Author with ID {author_id} does not exist")

        articles = self.article_repository.get_by_author(author_id)
        return [self._serialize_article(article) for article in articles]

    def get_articles_by_region(self, region_id: int) -> List[Dict[str, Any]]:
        """Get all articles in specific region"""
        if not self.region_repository.exists(region_id):
            raise ValueError(f"Region with ID {region_id} does not exist")

        articles = self.article_repository.get_by_region(region_id)
        return [self._serialize_article(article) for article in articles]

    def search_articles(self, search_term: str) -> List[Dict[str, Any]]:
        """Search articles by title or content"""
        if not search_term or not search_term.strip():
            return self.get_all_articles()

        articles = self.article_repository.search(search_term.strip())
        return [self._serialize_article(article) for article in articles]

    def search_articles_paginated(self, search_term: str, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Search articles with pagination"""
        if not search_term or not search_term.strip():
            return self.get_all_articles_paginated(offset, limit)

        articles, total = self.article_repository.search_paginated(search_term.strip(), offset, limit)
        article_data = [self._serialize_article(article) for article in articles]
        return article_data, total

    def get_articles_by_author_paginated(self, author_id: int, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get articles by author with pagination"""
        if not self.author_repository.exists(author_id):
            raise ValueError(f"Author with ID {author_id} does not exist")

        articles, total = self.article_repository.get_by_author_paginated(author_id, offset, limit)
        article_data = [self._serialize_article(article) for article in articles]
        return article_data, total

    def get_articles_by_region_paginated(self, region_id: int, offset: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """Get articles by region with pagination"""
        if not self.region_repository.exists(region_id):
            raise ValueError(f"Region with ID {region_id} does not exist")

        articles, total = self.article_repository.get_by_region_paginated(region_id, offset, limit)
        article_data = [self._serialize_article(article) for article in articles]
        return article_data, total

    def _serialize_article(self, article: Any) -> Dict[str, Any]:
        """Convert article to dictionary with relationships"""
        result = article.asdict()

        # Add author information
        if hasattr(article, 'author') and article.author:
            result['author'] = article.author.asdict()

        # Add regions information
        if hasattr(article, 'regions') and article.regions:
            result['regions'] = [region.asdict() for region in article.regions]
        else:
            result['regions'] = []

        return result

    def _validate_article_relations(self, author_id: Optional[int], region_ids: List[int]) -> List[str]:
        """Validate article relationships that require database access"""
        errors = []

        # Validate author (optional)
        if author_id is not None and not self.author_repository.exists(author_id):
            errors.append(f"Author with ID {author_id} does not exist")

        # Validate regions (optional)
        for region_id in region_ids or []:
            if not self.region_repository.exists(region_id):
                errors.append(f"Region with ID {region_id} does not exist")

        return errors
