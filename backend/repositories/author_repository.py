from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.author import Author
from repositories.base import BaseRepository


class AuthorRepository(BaseRepository):
    """Repository for Author entity with specific business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Author)
    
    def find_by_name(self, first_name: str = None, last_name: str = None) -> List[Author]:
        """Find authors by first name and/or last name"""
        query = self.db_session.query(Author)
        
        if first_name and last_name:
            query = query.filter(
                Author.first_name.ilike(f"%{first_name}%"),
                Author.last_name.ilike(f"%{last_name}%")
            )
        elif first_name:
            query = query.filter(Author.first_name.ilike(f"%{first_name}%"))
        elif last_name:
            query = query.filter(Author.last_name.ilike(f"%{last_name}%"))
        
        return query.all()
    
    def search(self, search_term: str) -> List[Author]:
        """Search authors by name (first or last name)"""
        search_pattern = f"%{search_term}%"
        return self.db_session.query(Author).filter(
            or_(
                Author.first_name.ilike(search_pattern),
                Author.last_name.ilike(search_pattern)
            )
        ).all()
    
    def get_all_paginated(self, offset: int = 0, limit: int = 20) -> Tuple[List[Author], int]:
        """Get all authors with pagination"""
        query = self.db_session.query(Author)
        total = query.count()
        authors = query.offset(offset).limit(limit).all()
        return authors, total
    
    def search_paginated(self, search_term: str, offset: int = 0, limit: int = 20) -> Tuple[List[Author], int]:
        """Search authors with pagination"""
        search_pattern = f"%{search_term}%"
        query = self.db_session.query(Author).filter(
            or_(
                Author.first_name.ilike(search_pattern),
                Author.last_name.ilike(search_pattern)
            )
        )
        total = query.count()
        authors = query.offset(offset).limit(limit).all()
        return authors, total
    
    def get_authors_with_articles(self) -> List[Author]:
        """Get all authors who have written articles"""
        return self.db_session.query(Author).filter(
            Author.articles.any()
        ).all()
    
    def validate_author_data(self, first_name: str, last_name: str) -> List[str]:
        """Validate author data and return list of errors"""
        errors = []
        
        if not first_name or not first_name.strip():
            errors.append("First name is required")
        elif len(first_name.strip()) < 2:
            errors.append("First name must be at least 2 characters")
        elif len(first_name.strip()) > 100:
            errors.append("First name must be less than 100 characters")
        
        if not last_name or not last_name.strip():
            errors.append("Last name is required")
        elif len(last_name.strip()) < 2:
            errors.append("Last name must be at least 2 characters")
        elif len(last_name.strip()) > 100:
            errors.append("Last name must be less than 100 characters")
        
        return errors