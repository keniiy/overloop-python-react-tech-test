import os
import tempfile

import pytest
from sqlalchemy import create_engine

from app import app as flask_app
from connector import BaseModel


@pytest.fixture(scope="function")
def app():
    """Create a Flask test app with isolated SQLite database."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    flask_app.config.update({
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{temp_file.name}'
    })

    engine = create_engine(flask_app.config['DATABASE_URL'])
    BaseModel.metadata.create_all(engine)

    try:
        with flask_app.app_context():
            yield flask_app
    finally:
        os.unlink(temp_file.name)


@pytest.fixture
def client(app):
    """Provide a test client for API requests."""
    return app.test_client()
