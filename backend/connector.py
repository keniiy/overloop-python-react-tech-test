from contextlib import contextmanager
import functools
import os
from datetime import datetime, date
from typing import TYPE_CHECKING, Dict, Optional

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

if TYPE_CHECKING:
    from sqlalchemy import Table


DEFAULT_DATABASE_URL = 'postgresql://techtest_user:techtest_password@localhost:5432/overloop_techtest'


class SerializableMixin:
    """Mixin to add JSON serialization capabilities to SQLAlchemy models"""

    if TYPE_CHECKING:
        __table__: "Table"

    def asdict(self, follow=None):
        """Convert model instance to dictionary"""
        follow = follow or []
        result = {}

        # Get all column values
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Handle datetime/date serialization
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value

        # Follow relationships if specified
        for relationship_name in follow:
            if hasattr(self, relationship_name):
                relationship_value = getattr(self, relationship_name)
                if relationship_value is not None:
                    if isinstance(relationship_value, list):
                        result[relationship_name] = [
                            item.asdict() if hasattr(item, 'asdict') else str(item)
                            for item in relationship_value
                        ]
                    else:
                        result[relationship_name] = (
                            relationship_value.asdict()
                            if hasattr(relationship_value, 'asdict')
                            else str(relationship_value)
                        )

        return result


def _get_configured_database_url() -> str:
    """Resolve database URL from Flask config or environment."""
    try:
        config_url = current_app.config.get('DATABASE_URL')  # type: ignore[attr-defined]
        if config_url:
            return config_url
    except RuntimeError:
        # No active application context; fall back to environment/default
        pass

    return os.getenv('DATABASE_URL', DEFAULT_DATABASE_URL)


_ENGINE_CACHE: Dict[str, Engine] = {}
_SESSION_FACTORY_CACHE: Dict[str, sessionmaker] = {}


def get_engine(database_url: Optional[str] = None) -> Engine:
    """Return (and cache) SQLAlchemy engine for the requested database URL."""
    db_url = database_url or _get_configured_database_url()
    if db_url not in _ENGINE_CACHE:
        _ENGINE_CACHE[db_url] = create_engine(db_url, echo=True)
    return _ENGINE_CACHE[db_url]


def _get_session_factory(database_url: Optional[str] = None) -> sessionmaker:
    """Return session factory bound to the resolved engine."""
    db_url = database_url or _get_configured_database_url()
    if db_url not in _SESSION_FACTORY_CACHE:
        _SESSION_FACTORY_CACHE[db_url] = sessionmaker(bind=get_engine(db_url))
    return _SESSION_FACTORY_CACHE[db_url]


BaseModel = declarative_base(cls=SerializableMixin)


@contextmanager
def db_session(database_url: Optional[str] = None):
    """Provide a transactional scope around operations for the selected database."""
    session_factory = _get_session_factory(database_url)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex
    finally:
        session.close()


def db_session_wrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = kwargs.pop('session', None)
        if session:
            return func(*args, session=session, **kwargs)
        else:
            with db_session() as session:
                return func(*args, session=session, **kwargs)

    return wrapper


# Expose a convenient default engine for scripts (uses env/default URL)
engine = get_engine()
