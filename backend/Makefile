# Overloop Tech Test Backend - Makefile
# Professional development workflow automation

.PHONY: help install install-dev setup clean test test-coverage lint format check run docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED    := \033[31m
GREEN  := \033[32m
YELLOW := \033[33m
BLUE   := \033[34m
RESET  := \033[0m

# Project variables
PROJECT_NAME := overloop-tech-test-backend
POETRY := poetry
PYTHON := $(POETRY) run python
PIP := $(POETRY) run pip
PYTEST := $(POETRY) run pytest
BLACK := $(POETRY) run black
FLAKE8 := $(POETRY) run flake8
ISORT := $(POETRY) run isort

help: ## Show this help message
	@echo "$(BLUE)$(PROJECT_NAME) - Available Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Environment Setup
install: ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(POETRY) install --only main
	@echo "$(GREEN)✓ Production dependencies installed$(RESET)"

install-dev: ## Install all dependencies including dev
	@echo "$(BLUE)Installing all dependencies...$(RESET)"
	$(POETRY) install
	@echo "$(GREEN)✓ All dependencies installed$(RESET)"

setup: install-dev setup-db ## Complete project setup
	@echo "$(GREEN)✓ Project setup complete!$(RESET)"

setup-db: ## Setup and seed database
	@echo "$(BLUE)Setting up database...$(RESET)"
	$(PYTHON) setup_and_seed.py
	@echo "$(GREEN)✓ Database setup complete$(RESET)"

poetry-install: ## Install Poetry if not present
	@echo "$(BLUE)Checking Poetry installation...$(RESET)"
	@command -v poetry >/dev/null 2>&1 || { \
		echo "$(YELLOW)Poetry not found. Installing...$(RESET)"; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	}
	@echo "$(GREEN)✓ Poetry ready$(RESET)"

poetry-shell: ## Activate Poetry shell
	@echo "$(BLUE)Activating Poetry shell...$(RESET)"
	$(POETRY) shell

# Development
run: ## Run the Flask development server
	@echo "$(BLUE)Starting Flask development server...$(RESET)"
	$(PYTHON) app.py

run-prod: ## Run in production mode
	@echo "$(BLUE)Starting Flask production server...$(RESET)"
	FLASK_ENV=production $(PYTHON) app.py

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(RESET)"
	$(PYTEST) -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(PYTEST) -v -m unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTEST) -v -m integration

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTEST) --cov=techtest --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(RESET)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	$(POETRY) run ptw

# Code Quality
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(RESET)"
	$(FLAKE8) techtest/ --max-line-length=120
	@echo "$(GREEN)✓ Linting complete$(RESET)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(ISORT) techtest/
	$(BLACK) techtest/
	@echo "$(GREEN)✓ Code formatted$(RESET)"

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(BLACK) techtest/ --check
	$(ISORT) techtest/ --check-only

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(RESET)"
	$(POETRY) run mypy techtest/
	@echo "$(GREEN)✓ Type checking complete$(RESET)"

check: lint format-check type-check test ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed!$(RESET)"

# API Testing
api-test: ## Test API endpoints manually
	@echo "$(BLUE)Testing API endpoints...$(RESET)"
	@echo "$(YELLOW)Testing GET /articles...$(RESET)"
	curl -s http://localhost:5000/articles || echo "$(RED)Server not running$(RESET)"
	@echo ""
	@echo "$(YELLOW)Testing GET /authors...$(RESET)"
	curl -s http://localhost:5000/authors || echo "$(RED)Server not running$(RESET)"
	@echo ""
	@echo "$(YELLOW)Testing GET /regions...$(RESET)"
	curl -s http://localhost:5000/regions || echo "$(RED)Server not running$(RESET)"

api-create-author: ## Create a test author
	@echo "$(BLUE)Creating test author...$(RESET)"
	curl -X POST http://localhost:5000/authors \
		-H "Content-Type: application/json" \
		-d '{"first_name": "Test", "last_name": "Author"}' || \
		echo "$(RED)Failed to create author$(RESET)"

# Docker & Docker Compose
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(PROJECT_NAME) .
	@echo "$(GREEN)✓ Docker image built$(RESET)"

docker-run: docker-build ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -it -p 5000:5000 $(PROJECT_NAME)

docker-clean: ## Clean Docker images
	@echo "$(BLUE)Cleaning Docker images...$(RESET)"
	docker rmi $(PROJECT_NAME) 2>/dev/null || true
	@echo "$(GREEN)✓ Docker images cleaned$(RESET)"

# Docker Compose Commands
compose-up: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(RESET)"

compose-up-build: ## Build and start all services
	@echo "$(BLUE)Building and starting services...$(RESET)"
	docker-compose up -d --build
	@echo "$(GREEN)✓ Services built and started$(RESET)"

compose-down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(RESET)"

compose-logs: ## View logs from all services
	@echo "$(BLUE)Viewing service logs...$(RESET)"
	docker-compose logs -f

compose-logs-backend: ## View backend logs only
	@echo "$(BLUE)Viewing backend logs...$(RESET)"
	docker-compose logs -f backend

compose-restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(RESET)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(RESET)"

compose-clean: ## Stop and remove all containers, networks, and volumes
	@echo "$(BLUE)Cleaning up Docker Compose...$(RESET)"
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✓ Docker Compose cleaned$(RESET)"

# Database Commands
db-start: ## Start only the database
	@echo "$(BLUE)Starting PostgreSQL database...$(RESET)"
	docker-compose up -d postgres postgres-test
	@echo "$(GREEN)✓ Database started$(RESET)"

db-stop: ## Stop the database
	@echo "$(BLUE)Stopping database...$(RESET)"
	docker-compose stop postgres postgres-test
	@echo "$(GREEN)✓ Database stopped$(RESET)"

db-logs: ## View database logs
	@echo "$(BLUE)Viewing database logs...$(RESET)"
	docker-compose logs -f postgres

db-connect: ## Connect to the main database
	@echo "$(BLUE)Connecting to main database...$(RESET)"
	docker-compose exec postgres psql -U techtest_user -d overloop_techtest

db-connect-test: ## Connect to the test database
	@echo "$(BLUE)Connecting to test database...$(RESET)"
	docker-compose exec postgres-test psql -U techtest_user -d overloop_techtest_test

# Database
db-reset: ## Reset database
	@echo "$(BLUE)Resetting database...$(RESET)"
	rm -f database.db
	$(PYTHON) setup_and_seed.py
	@echo "$(GREEN)✓ Database reset complete$(RESET)"

db-migrate: ## Run database migrations (if applicable)
	@echo "$(BLUE)Running database migrations...$(RESET)"
	# Add migration commands here if using Alembic
	@echo "$(YELLOW)No migrations configured yet$(RESET)"

# Cleanup
clean: ## Clean temporary files
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

clean-all: clean docker-clean ## Clean everything including Docker
	@echo "$(GREEN)✓ Complete cleanup finished$(RESET)"

# Development workflow
dev-setup: poetry-install ## Quick development environment setup
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	@echo "$(YELLOW)1. Run: make install-dev$(RESET)"
	@echo "$(YELLOW)2. Run: make setup-db$(RESET)"
	@echo "$(YELLOW)3. Run: make run$(RESET)"
	@echo "$(GREEN)✓ Poetry will automatically manage virtual environment!$(RESET)"

dev-check: format lint type-check test ## Quick development check
	@echo "$(GREEN)✓ Development check complete!$(RESET)"

# CI/CD helpers
ci-install: ## Install dependencies for CI
	$(POETRY) install --only main

ci-test: ## Run tests for CI environment
	$(PYTEST) --junitxml=test-results.xml --cov=techtest --cov-report=xml

# Documentation
docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(RESET)"
	@echo "$(YELLOW)Documentation generation not configured yet$(RESET)"

# Info
info: ## Show project information
	@echo "$(BLUE)Project Information$(RESET)"
	@echo "Name: $(PROJECT_NAME)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Working Directory: $(shell pwd)"
	@echo "Requirements: $(REQUIREMENTS)"