from typing import List, Optional, Dict, Any
from repositories.article_repository import ArticleRepository
from repositories.author_repository import AuthorRepository
from repositories.region_repository import RegionRepository


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
        return [self._serialize_article(article) for article in articles]
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get article by ID with relationships"""
        article = self.article_repository.get_by_id_with_relations(article_id)
        return self._serialize_article(article) if article else None
    
    def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new article with author and regions"""
        title = article_data.get('title', '').strip()
        content = article_data.get('content', '').strip()
        author_id = article_data.get('author_id')
        region_ids = article_data.get('region_ids', [])
        
        # Validate article data
        errors = self._validate_article_data(title, content, author_id, region_ids)
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
        article = self.article_repository.get_by_id_with_relations(article.id)
        return self._serialize_article(article)
    
    def update_article(self, article_id: int, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing article"""
        if not self.article_repository.exists(article_id):
            return None
        
        title = article_data.get('title', '').strip()
        content = article_data.get('content', '').strip()
        author_id = article_data.get('author_id')
        region_ids = article_data.get('region_ids', [])
        
        # Validate article data
        errors = self._validate_article_data(title, content, author_id, region_ids)
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
    
    def _serialize_article(self, article) -> Dict[str, Any]:
        """Convert article to dictionary with relationships"""
        if not article:
            return None
        
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
    
    def _validate_article_data(self, title: str, content: str, author_id: int, region_ids: List[int]) -> List[str]:
        """Validate article data"""
        errors = []
        
        # Validate title
        if not title:
            errors.append("Title is required")
        elif len(title) < 5:
            errors.append("Title must be at least 5 characters")
        elif len(title) > 500:
            errors.append("Title must be less than 500 characters")
        
        # Validate content
        if not content:
            errors.append("Content is required")
        elif len(content) < 10:
            errors.append("Content must be at least 10 characters")
        
        # Validate author (optional)
        if author_id is not None and not self.author_repository.exists(author_id):
            errors.append(f"Author with ID {author_id} does not exist")
        
        # Validate regions (optional)
        if region_ids:
            for region_id in region_ids:
                if not self.region_repository.exists(region_id):
                    errors.append(f"Region with ID {region_id} does not exist")
        
        return errors