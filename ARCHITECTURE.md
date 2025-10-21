# Overloop Tech Test - System Architecture

## Entity Relationship Diagram

```text
     +------------------+
     |      AUTHOR      |
     |------------------|
     | id (PK)          |
     | first_name       |
     | last_name        |
     +--------+---------+
              |
              | 1 (One Author)
              |
              | M (Many Articles)
              |
              v
     +------------------+         +------------------+
     |     ARTICLE      |         |      REGION      |
     |------------------|         |------------------|
     | id (PK)          |         | id (PK)          |
     | title            |         | code (UNIQUE)    |
     | content          |    M:N  | name             |
     | author_id (FK)   |<------->|                  |
     +--------+---------+         +---------+--------+
              |                             |
              |                             |
              +-----------------------------+
                           |
                           v
              +---------------------------+
              |      article_region       |
              |   (Association Table)     |
              |---------------------------|
              | article_id (FK)           |
              | region_id (FK)            |
              | PRIMARY KEY (both)        |
              +---------------------------+

Relationships:
- Author -> Article: One-to-Many (1:M)
- Article <-> Region: Many-to-Many (M:N) via article_region table
- No region_id stored in Article table (M:N uses association table)
```

## Database Schema

```sql
CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
);
```

### Articles Table (Updated)

```sql
CREATE TABLE article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    author_id INTEGER REFERENCES author(id)  -- One-to-Many with Author
    -- Note: No region_id - regions handled via association table
);
```

### Regions Table (Existing)

```sql
CREATE TABLE region (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code STRING(2) UNIQUE,
    name TEXT
);
```

### Article-Region Association Table (Existing)

```sql
CREATE TABLE article_region (
    article_id INTEGER REFERENCES article(id),
    region_id INTEGER REFERENCES region(id),
    PRIMARY KEY (article_id, region_id)  -- Composite primary key
);
```

## Relationship Patterns Explained

**One-to-Many (Author → Article):**

- `author_id` foreign key stored in `article` table
- One author can write many articles
- Article must reference an author (or nullable for optional)

**Many-to-Many (Article ↔ Region):**

- NO foreign keys in `article` or `region` tables
- Association table `article_region` stores relationships
- One article can belong to multiple regions
- One region can contain multiple articles

## API Endpoints

### Authors

- `GET /authors` - List all authors
- `POST /authors` - Create new author
- `GET /authors/{id}` - Get specific author
- `PUT /authors/{id}` - Update author
- `DELETE /authors/{id}` - Delete author

### Articles (Enhanced)

- `GET /articles` - List all articles with author and regions
- `POST /articles` - Create article (with author and region selection)
- `GET /articles/{id}` - Get specific article
- `PUT /articles/{id}` - Update article
- `DELETE /articles/{id}` - Delete article

### Regions (Complete CRUD)

- `GET /regions` - List all regions ✓
- `POST /regions` - Create new region
- `GET /regions/{id}` - Get specific region
- `PUT /regions/{id}` - Update region
- `DELETE /regions/{id}` - Delete region

## Sample JSON Responses

### Article with Author and Regions

```json
{
  "id": 1,
  "title": "Understanding Climate Change",
  "content": "Climate change refers to long-term shifts...",
  "author_id": 1,
  "author": {
    "id": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith"
  },
  "regions": [
    {
      "id": 1,
      "code": "US",
      "name": "United States"
    },
    {
      "id": 3,
      "code": "EU",
      "name": "European Union"
    }
  ]
}
```

### Author Response

```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Region Response

```json
{
  "id": 1,
  "code": "US",
  "name": "United States"
}
```

## Implementation Plan

1. **Models Layer**
   - Create `Author` model
   - Update `Article` model with author relationship
   - Update model imports

2. **Routes Layer**
   - Create `authors.py` with full CRUD
   - Enhance `articles.py` with author support
   - Complete `regions.py` with missing CRUD operations

3. **Testing Layer**
   - Unit tests for all models
   - Integration tests for all endpoints
   - Test relationship integrity

## Database Implementation Examples

### SQLite Implementation (Current)

```sql
-- Table Creation
CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    author_id INTEGER REFERENCES author(id)
);

CREATE TABLE region (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT
);

CREATE TABLE article_region (
    article_id INTEGER REFERENCES article(id),
    region_id INTEGER REFERENCES region(id),
    PRIMARY KEY (article_id, region_id)
);
```

**Sample Data:**

```sql
-- Authors
INSERT INTO author VALUES (1, 'John', 'Doe');
INSERT INTO author VALUES (2, 'Jane', 'Smith');

-- Articles
INSERT INTO article VALUES (1, 'Tech Trends 2024', 'AI is transforming...', 1);
INSERT INTO article VALUES (2, 'Climate Solutions', 'Green tech innovations...', 1);
INSERT INTO article VALUES (3, 'Food Culture', 'Global cuisine evolution...', 2);

-- Regions
INSERT INTO region VALUES (1, 'US', 'United States');
INSERT INTO region VALUES (2, 'CA', 'Canada');
INSERT INTO region VALUES (3, 'EU', 'European Union');

-- Article-Region Relationships
INSERT INTO article_region VALUES (1, 1); -- Tech Trends -> US
INSERT INTO article_region VALUES (1, 3); -- Tech Trends -> EU
INSERT INTO article_region VALUES (2, 1); -- Climate -> US
INSERT INTO article_region VALUES (2, 2); -- Climate -> CA
INSERT INTO article_region VALUES (2, 3); -- Climate -> EU
INSERT INTO article_region VALUES (3, 2); -- Food Culture -> CA
```

### PostgreSQL Implementation (Enhanced)

```sql
-- Table Creation with Better Constraints
CREATE TABLE author (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (author_id) REFERENCES author(id) ON DELETE CASCADE
);

CREATE TABLE region (
    id SERIAL PRIMARY KEY,
    code CHAR(2) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE article_region (
    article_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (article_id, region_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (region_id) REFERENCES region(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX idx_article_author ON article(author_id);
CREATE INDEX idx_article_region_article ON article_region(article_id);
CREATE INDEX idx_article_title ON article USING gin(to_tsvector('english', title));
```

**Same Data, Better Queries:**

```sql
-- Full-text search (PostgreSQL feature)
SELECT a.*, au.first_name, au.last_name
FROM article a
JOIN author au ON a.author_id = au.id
WHERE to_tsvector('english', a.title) @@ plainto_tsquery('english', 'tech');

-- Complex relationship query with timestamps
SELECT
    a.title,
    au.first_name || ' ' || au.last_name as author_name,
    array_agg(r.code) as region_codes,
    a.created_at
FROM article a
JOIN author au ON a.author_id = au.id
LEFT JOIN article_region ar ON a.id = ar.article_id
LEFT JOIN region r ON ar.region_id = r.id
GROUP BY a.id, a.title, au.first_name, au.last_name, a.created_at
ORDER BY a.created_at DESC;
```

### PostgreSQL Alternative (Array Approach)

```sql
-- Using PostgreSQL arrays (MongoDB-like)
CREATE TABLE article_with_arrays (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author_id INTEGER NOT NULL REFERENCES author(id),
    region_ids INTEGER[] DEFAULT '{}',  -- Array of region IDs
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data with arrays
INSERT INTO article_with_arrays VALUES
(1, 'Tech Trends 2024', 'AI is transforming...', 1, '{1,3}'),
(2, 'Climate Solutions', 'Green tech innovations...', 1, '{1,2,3}'),
(3, 'Food Culture', 'Global cuisine evolution...', 2, '{2}');

-- Array queries
SELECT * FROM article_with_arrays WHERE 1 = ANY(region_ids);        -- Contains US
SELECT * FROM article_with_arrays WHERE region_ids && ARRAY[1,2];   -- Overlaps US or CA
SELECT * FROM article_with_arrays WHERE array_length(region_ids,1) > 2; -- Multiple regions
```

### MySQL Implementation (Production-Ready)

```sql
-- Table Creation with InnoDB
CREATE TABLE author (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (first_name, last_name)
) ENGINE=InnoDB;

CREATE TABLE article (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES author(id) ON DELETE CASCADE,
    INDEX idx_author (author_id),
    FULLTEXT INDEX idx_content (title, content)
) ENGINE=InnoDB;

CREATE TABLE region (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code CHAR(2) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE article_region (
    article_id INT NOT NULL,
    region_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (article_id, region_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (region_id) REFERENCES region(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**MySQL-Specific Queries:**

```sql
-- Full-text search (MySQL feature)
SELECT a.*, au.first_name, au.last_name,
       MATCH(a.title, a.content) AGAINST('tech innovation' IN NATURAL LANGUAGE MODE) as relevance
FROM article a
JOIN author au ON a.author_id = au.id
WHERE MATCH(a.title, a.content) AGAINST('tech innovation' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC;

-- JSON aggregation (MySQL 5.7+)
SELECT
    a.id,
    a.title,
    JSON_OBJECT('id', au.id, 'name', CONCAT(au.first_name, ' ', au.last_name)) as author,
    JSON_ARRAYAGG(JSON_OBJECT('code', r.code, 'name', r.name)) as regions
FROM article a
JOIN author au ON a.author_id = au.id
LEFT JOIN article_region ar ON a.id = ar.article_id
LEFT JOIN region r ON ar.region_id = r.id
GROUP BY a.id, a.title, au.id, au.first_name, au.last_name;
```

## Data Retrieval Examples

### Query: "Get Tech Trends article with author and regions"

**SQLite Result:**

```txt
| id | title          | author_name | regions    |
|----|----------------|-------------|------------|
| 1  | Tech Trends 2024 | John Doe   | US,EU      |
```

**PostgreSQL Result (with timestamps):**

```txt
| id | title          | author_name | regions | created_at          |
|----|----------------|-------------|---------|---------------------|
| 1  | Tech Trends 2024 | John Doe   | {US,EU} | 2024-01-15 10:30:00 |
```

**MySQL Result (JSON format):**

```json
{
  "id": 1,
  "title": "Tech Trends 2024",
  "author": {"id": 1, "name": "John Doe"},
  "regions": [
    {"code": "US", "name": "United States"},
    {"code": "EU", "name": "European Union"}
  ]
}
```

### Performance Comparison

| Database   | Association Table | Array Approach | Full-text Search | JSON Support |
|------------|------------------|----------------|------------------|--------------|
| SQLite     | ✅ Basic         | ❌ No          | ❌ Limited       | ❌ No        |
| PostgreSQL | ✅ Advanced      | ✅ Native      | ✅ Excellent     | ✅ Native    |
| MySQL      | ✅ Advanced      | ❌ JSON only   | ✅ Good          | ✅ Native    |

## Technology Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: SQLite (dev) → PostgreSQL/MySQL (prod)
- **ORM**: SQLAlchemy with DictableModel
- **Session Management**: Custom decorator pattern
- **JSON Serialization**: Built-in with DictableModel.
