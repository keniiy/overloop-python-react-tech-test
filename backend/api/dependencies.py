from functools import wraps
from flask import g

from connector import db_session
from core.dependencies import create_container


def with_services(func):
    """Decorator to inject services into Flask route handlers"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create DI container with current session
        with db_session() as session:
            container = create_container(session)
            
            # Add container to Flask's g object for access in routes
            g.container = container
            g.session = session
            
            try:
                result = func(*args, **kwargs)
                session.commit()  # Commit if everything went well
                return result
            except Exception as e:
                session.rollback()  # Rollback on error
                raise e
    
    return wrapper


def get_author_service():
    """Get author service from current request context"""
    if not hasattr(g, 'container'):
        raise RuntimeError("Services not available. Use @with_services decorator.")
    return g.container.get_author_service()


def get_article_service():
    """Get article service from current request context"""
    if not hasattr(g, 'container'):
        raise RuntimeError("Services not available. Use @with_services decorator.")
    return g.container.get_article_service()


def get_region_service():
    """Get region service from current request context"""
    if not hasattr(g, 'container'):
        raise RuntimeError("Services not available. Use @with_services decorator.")
    return g.container.get_region_service()