from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from techtest.config.settings import settings


def create_database_engine():
    """Create database engine with configuration"""
    return create_engine(
        settings.get_database_url(),
        echo=settings.DATABASE_ECHO,
        # SQLite specific optimizations
        connect_args={"check_same_thread": False} if "sqlite" in settings.get_database_url() else {}
    )


def create_session_factory(engine):
    """Create session factory"""
    return sessionmaker(bind=engine)


# Global engine and session factory
engine = create_database_engine()
SessionFactory = create_session_factory(engine)