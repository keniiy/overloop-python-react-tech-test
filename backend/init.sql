-- Initialize Overloop Tech Test Database
-- This script sets up the initial database structure

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges to the techtest_user
GRANT ALL PRIVILEGES ON DATABASE overloop_techtest TO techtest_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO techtest_user;

-- Create a simple health check table
CREATE TABLE IF NOT EXISTS _health_check (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'healthy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO _health_check (status) VALUES ('initialized');

-- The actual application tables will be created by SQLAlchemy when the app starts