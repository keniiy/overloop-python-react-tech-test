from contextlib import contextmanager
import functools
from datetime import datetime, date

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class SerializableMixin:
    """Mixin to add JSON serialization capabilities to SQLAlchemy models"""
    
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


import os

# Get database URL from environment, fallback to PostgreSQL default
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://techtest_user:techtest_password@localhost:5432/overloop_techtest'
)

engine = create_engine(DATABASE_URL, echo=True)
_db_session = sessionmaker(bind=engine)

BaseModel = declarative_base(cls=SerializableMixin)


@contextmanager
def db_session():
    """Provide a transactional scope around a series of operations.
    Taken from http://docs.sqlalchemy.org/en/latest/orm/session_basics.html.
    This handles rollback and closing of session, so there is no need
    to do that throughout the code.
    Usage:
        with db_session() as session:
            session.execute(query)
    """
    session = _db_session()
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
