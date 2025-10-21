# 🚀 Overloop Tech Test - Senior Engineering Implementation Guide

## 📊 Project Overview

A full-stack application implementing Article-Author-Region management with React frontend and Flask backend. This guide follows enterprise-level standards with proper dependency injection, testing strategies, and architectural patterns.

## 🏗️ Recommended Project Structure

### Backend Structure (Clean Architecture + Dependency Injection)

```text
backend/
├── app.py                          # Application entry point
├── requirements.txt                # Dependencies
├── requirements-dev.txt            # Development dependencies
├── pytest.ini                      # Test configuration
├── .env.example                    # Environment template
├── Dockerfile                      # Container configuration
├── techtest/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Configuration management
│   │   └── database.py             # Database configuration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── validators.py           # Input validation
│   │   └── dependencies.py         # Dependency injection container
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base model with common fields
│   │   ├── article.py              # Article model with Author FK
│   │   ├── author.py               # Author model (NEW)
│   │   └── region.py               # Region model
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base repository pattern
│   │   ├── article_repository.py   # Article data access
│   │   ├── author_repository.py    # Author data access (NEW)
│   │   └── region_repository.py    # Region data access
│   ├── services/
│   │   ├── __init__.py
│   │   ├── article_service.py      # Business logic for articles
│   │   ├── author_service.py       # Business logic for authors (NEW)
│   │   └── region_service.py       # Business logic for regions
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py         # API dependency injection
│   │   ├── middleware.py           # Request/response middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── articles.py         # Article endpoints
│   │       ├── authors.py          # Author endpoints (NEW)
│   │       └── regions.py          # Region endpoints
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # Test fixtures & dependency injection
│       ├── unit/
│       │   ├── test_services/
│       │   ├── test_repositories/
│       │   └── test_models/
│       └── integration/
│           ├── test_api/
│           └── test_database/
```

### Frontend Structure (Feature-Based Architecture + Custom Hooks)

```text
frontend/
├── package.json
├── .env.example                    # Environment template
├── jest.config.js                  # Test configuration
├── .eslintrc.js                    # Code quality
├── public/
├── src/
│   ├── index.js                    # Application entry point
│   ├── App.js                      # Root component with providers
│   ├── config/
│   │   ├── constants.js            # Application constants
│   │   └── api.js                  # API configuration
│   ├── contexts/                   # React Context providers
│   │   ├── AppContext.js           # Global state management
│   │   └── NotificationContext.js  # Toast notifications
│   ├── hooks/                      # Custom hooks (dependency injection)
│   │   ├── useApi.js               # API hook with error handling
│   │   ├── useArticles.js          # Article business logic
│   │   ├── useAuthors.js           # Author business logic (NEW)
│   │   └── useRegions.js           # Region business logic
│   ├── services/                   # External service interfaces
│   │   ├── api/
│   │   │   ├── client.js           # Axios configuration
│   │   │   ├── articles.js         # Article API calls
│   │   │   ├── authors.js          # Author API calls (NEW)
│   │   │   └── regions.js          # Region API calls
│   │   └── validation/
│   │       ├── articleSchema.js    # Article validation rules
│   │       └── authorSchema.js     # Author validation rules (NEW)
│   ├── components/                 # Reusable components
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Modal/
│   │   │   └── ErrorBoundary/
│   │   ├── layout/
│   │   │   ├── Header/
│   │   │   ├── Navigation/
│   │   │   └── Footer/
│   │   └── forms/
│   │       ├── ArticleForm/
│   │       └── AuthorForm/         # (NEW)
│   ├── pages/                      # Feature pages
│   │   ├── Articles/
│   │   │   ├── ArticleList/
│   │   │   ├── ArticleDetail/
│   │   │   ├── ArticleCreate/
│   │   │   └── ArticleEdit/
│   │   ├── Authors/                # (NEW)
│   │   │   ├── AuthorList/
│   │   │   ├── AuthorCreate/
│   │   │   └── AuthorEdit/
│   │   └── Dashboard/
│   ├── utils/
│   │   ├── helpers.js              # Utility functions
│   │   ├── formatters.js           # Data formatting
│   │   └── constants.js            # Shared constants
│   └── __tests__/                  # Test files
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── pages/
│       └── utils/
```

## 🔧 Implementation Steps

### Step 1: Backend Setup & Dependency Injection

#### 1.1 Create Author Model (Missing Implementation)

```python
# techtest/models/author.py
from sqlalchemy import Column, Integer, String
from techtest.connector import BaseModel

class Author(BaseModel):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

#### 1.2 Update Article Model (Add Author Foreign Key)

```python
# Update techtest/models/article.py
author_id = Column(Integer, ForeignKey('author.id'), nullable=True)
author = relationship('Author', backref='articles')
```

#### 1.3 Dependency Injection Container

```python
# techtest/core/dependencies.py
from functools import lru_cache
from techtest.repositories.article_repository import ArticleRepository
from techtest.repositories.author_repository import AuthorRepository
from techtest.services.article_service import ArticleService
from techtest.services.author_service import AuthorService

class DIContainer:
    def __init__(self, db_session):
        self._db_session = db_session
        self._services = {}
        self._repositories = {}

    @lru_cache(maxsize=None)
    def get_article_repository(self):
        if 'article_repo' not in self._repositories:
            self._repositories['article_repo'] = ArticleRepository(self._db_session)
        return self._repositories['article_repo']

    @lru_cache(maxsize=None)
    def get_author_repository(self):
        if 'author_repo' not in self._repositories:
            self._repositories['author_repo'] = AuthorRepository(self._db_session)
        return self._repositories['author_repo']

    @lru_cache(maxsize=None)
    def get_article_service(self):
        if 'article_service' not in self._services:
            self._services['article_service'] = ArticleService(
                self.get_article_repository(),
                self.get_author_repository()
            )
        return self._services['article_service']

    @lru_cache(maxsize=None)
    def get_author_service(self):
        if 'author_service' not in self._services:
            self._services['author_service'] = AuthorService(
                self.get_author_repository()
            )
        return self._services['author_service']
```

### Step 2: Frontend Custom Hooks (React Dependency Injection)

#### 2.1 Custom Hook for Authors

```javascript
// src/hooks/useAuthors.js
import { useState, useCallback } from 'react';
import { authorsApi } from '../services/api/authors';
import { useNotification } from '../contexts/NotificationContext';

export const useAuthors = () => {
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { showNotification } = useNotification();

  const fetchAuthors = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await authorsApi.getAll();
      setAuthors(data);
    } catch (err) {
      setError(err.message);
      showNotification('Failed to fetch authors', 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const createAuthor = useCallback(async (authorData) => {
    try {
      const newAuthor = await authorsApi.create(authorData);
      setAuthors(prev => [...prev, newAuthor]);
      showNotification('Author created successfully', 'success');
      return newAuthor;
    } catch (err) {
      showNotification('Failed to create author', 'error');
      throw err;
    }
  }, [showNotification]);

  return {
    authors,
    loading,
    error,
    fetchAuthors,
    createAuthor,
    // ... other methods
  };
};
```

## 🧪 Testing Strategy

### Backend Testing (pytest + fixtures)

#### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = techtest/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

#### Test Fixtures with Dependency Injection

```python
# techtest/tests/conftest.py
import pytest
from techtest.core.dependencies import DIContainer
from techtest.connector import get_db

@pytest.fixture
def db_session():
    """Database session fixture"""
    db = get_db()
    try:
        yield db.session
    finally:
        db.session.rollback()
        db.session.close()

@pytest.fixture
def di_container(db_session):
    """Dependency injection container fixture"""
    return DIContainer(db_session)

@pytest.fixture
def author_service(di_container):
    """Author service fixture"""
    return di_container.get_author_service()

@pytest.fixture
def sample_author_data():
    """Sample author data for testing"""
    return {
        'first_name': 'John',
        'last_name': 'Doe'
    }
```

#### Unit Test Examples

```python
# techtest/tests/unit/test_services/test_author_service.py
import pytest
from techtest.services.author_service import AuthorService

@pytest.mark.unit
class TestAuthorService:

    def test_create_author_success(self, author_service, sample_author_data):
        """Test successful author creation"""
        author = author_service.create_author(sample_author_data)
        assert author.first_name == sample_author_data['first_name']
        assert author.last_name == sample_author_data['last_name']
        assert author.full_name == "John Doe"

    def test_create_author_validation_error(self, author_service):
        """Test author creation with invalid data"""
        with pytest.raises(ValueError):
            author_service.create_author({'first_name': ''})
```

### Frontend Testing (React Testing Library + MSW)

#### Test Setup

```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

#### Mock Service Worker Setup

```javascript
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/authors', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, first_name: 'John', last_name: 'Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith' }
      ])
    );
  }),

  rest.post('/api/authors', (req, res, ctx) => {
    return res(
      ctx.json({ id: 3, ...req.body })
    );
  })
];
```

#### Component Testing with Dependency Injection

```javascript
// src/__tests__/hooks/useAuthors.test.js
import { renderHook, act } from '@testing-library/react';
import { useAuthors } from '../../hooks/useAuthors';
import { NotificationProvider } from '../../contexts/NotificationContext';

const wrapper = ({ children }) => (
  <NotificationProvider>{children}</NotificationProvider>
);

describe('useAuthors', () => {
  it('should fetch authors successfully', async () => {
    const { result } = renderHook(() => useAuthors(), { wrapper });

    await act(async () => {
      await result.current.fetchAuthors();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.authors).toHaveLength(2);
    expect(result.current.error).toBeNull();
  });
});
```

## 🚀 Implementation Roadmap

### Phase 1: Backend Foundation (Day 1)

1. ✅ Create Author model with proper relationships
2. ✅ Implement Repository pattern with dependency injection
3. ✅ Create Service layer with business logic
4. ✅ Set up comprehensive error handling
5. ✅ Write unit tests for all services

### Phase 2: Backend API (Day 1)

1. ✅ Implement Author CRUD endpoints
2. ✅ Update Article endpoints to support Author relationship
3. ✅ Add input validation and sanitization
4. ✅ Write integration tests for all endpoints

### Phase 3: Frontend Architecture (Day 2)

1. ✅ Set up custom hooks for state management
2. ✅ Implement Author service layer
3. ✅ Create reusable form components
4. ✅ Set up error boundary and notification system

### Phase 4: Frontend Features (Day 2)

1. ✅ Author List page with search/filter
2. ✅ Author Create/Edit forms with validation
3. ✅ Update Article forms to include Author selection
4. ✅ Display Author information in Article views

### Phase 5: Testing & Quality (Day 3)

1. ✅ Complete unit test coverage (>80%)
2. ✅ Integration tests for all user flows
3. ✅ End-to-end testing with Cypress/Playwright
4. ✅ Performance optimization and accessibility

## 📝 Deliverables Checklist

### ✅ **Must-Have Features**

- [✅] Author entity with first_name and last_name
- [✅] Author CRUD operations (Create, Read, Update, Delete)
- [✅] Author selection in Article create/edit forms
- [✅] Optional Author assignment (can be null)
- [✅] Author display in Article list and detail views
- [✅] Comprehensive unit tests for new functionality

### 🚀 **Senior-Level Additions**

- [✅] Repository pattern with dependency injection
- [✅] Custom React hooks for business logic
- [✅] Comprehensive error handling and validation
- [✅] Integration tests with proper fixtures
- [✅] Performance optimizations (memoization, lazy loading)
- [✅] Accessibility compliance (ARIA labels, keyboard navigation)
- [✅] Responsive design for mobile/tablet
- [✅] API documentation with OpenAPI/Swagger

### 🔧 **Development Commands**

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Create this with pytest, black, flake8

# Run backend with hot reload
python app.py

# Run backend tests
pytest --cov=techtest --cov-report=html

# Frontend setup
cd frontend
npm install

# Run frontend
npm start

# Run frontend tests
npm test -- --coverage --watchAll=false

# Run integration tests
npm run test:integration
```

## 🎯 **Success Criteria**

1. **Functionality**: All Author CRUD operations work seamlessly
2. **Code Quality**: Clean architecture with proper separation of concerns
3. **Testing**: >80% test coverage with meaningful test cases
4. **Performance**: Fast loading times and responsive UI
5. **User Experience**: Intuitive interface with proper error handling
6. **Scalability**: Architecture supports future feature additions

This guide provides a senior-level implementation approach with enterprise patterns, comprehensive testing, and maintainable code architecture. Follow the phases sequentially for best results.
