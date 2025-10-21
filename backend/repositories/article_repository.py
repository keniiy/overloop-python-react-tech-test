from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models.article import Article
from models.author import Author
from models.region import Region
from repositories.base import BaseRepository


class ArticleRepository(BaseRepository):
    """Repository for Article entity with relationship handling"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Article)
    
    def get_all_with_relations(self) -> List[Article]:
        """Get all articles with author and regions loaded"""
        return self.db_session.query(Article)\
            .options(joinedload(Article.author))\
            .options(joinedload(Article.regions))\
            .order_by(Article.id)\
            .all()
    
    def get_by_id_with_relations(self, article_id: int) -> Optional[Article]:
        """Get article by ID with author and regions loaded"""
        return self.db_session.query(Article)\
            .options(joinedload(Article.author))\
            .options(joinedload(Article.regions))\
            .filter(Article.id == article_id)\
            .first()
    
    def get_by_author(self, author_id: int) -> List[Article]:
        """Get all articles by specific author"""
        return self.db_session.query(Article)\
            .options(joinedload(Article.regions))\
            .filter(Article.author_id == author_id)\
            .all()
    
    def get_by_region(self, region_id: int) -> List[Article]:
        """Get all articles in specific region"""
        return self.db_session.query(Article)\
            .options(joinedload(Article.author))\
            .join(Article.regions)\
            .filter(Region.id == region_id)\
            .all()
    
    def search(self, search_term: str) -> List[Article]:
        """Search articles by title or content"""
        search_pattern = f"%{search_term}%"
        return self.db_session.query(Article)\
            .options(joinedload(Article.author))\
            .options(joinedload(Article.regions))\
            .filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern)
                )
            ).all()
    
    def create_with_regions(self, title: str, content: str, author_id: int = None, region_ids: List[int] = None) -> Article:
        """Create article with author and regions"""
        article = Article(
            title=title,
            content=content,
            author_id=author_id
        )
        
        # Add regions if provided
        if region_ids:
            regions = self.db_session.query(Region).filter(Region.id.in_(region_ids)).all()
            article.regions = regions
        
        self.db_session.add(article)
        self.db_session.flush()
        return article
    
    def update_regions(self, article_id: int, region_ids: List[int]) -> Optional[Article]:
        """Update article regions"""
        article = self.get_by_id(article_id)
        if article:
            regions = self.db_session.query(Region).filter(Region.id.in_(region_ids)).all()
            article.regions = regions
            self.db_session.flush()
        return article