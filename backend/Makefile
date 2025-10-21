# Overloop Tech Test Backend - Makefile

.PHONY: install install-dev run run-prod test lint format compose-up compose-down

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


# Environment Setup

install:
	poetry install --only main

install-dev:
	poetry install

setup: install-dev setup-db ## Complete project setup
	@echo "$(GREEN)✓ Project setup complete!$(RESET)"

setup-db: ## Setup and seed database
	@echo "$(BLUE)Setting up database...$(RESET)"
	$(PYTHON) setup_and_seed.py
	@echo "$(GREEN)✓ Database setup complete$(RESET)"


# Development

run:
	poetry run python app.py

run-prod:
	FLASK_ENV=production poetry run python app.py

# Testing

test:
	poetry run pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(PYTEST) -v -m unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTEST) -v -m integration

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTEST) --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(RESET)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	$(POETRY) run ptw

# Code Quality

lint:
	poetry run flake8 . --max-line-length=120 --exclude=tests,htmlcov,.git,__pycache__,.pytest_cache

format:
	poetry run isort .
	poetry run black .

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(BLACK) . --check
	$(ISORT) . --check-only

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(RESET)"
	$(POETRY) run mypy . --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking complete$(RESET)"

check: lint format-check type-check test ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed!$(RESET)"

# API Testing

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

compose-up:
	docker-compose up -d

compose-up-build: ## Build and start all services
	docker-compose up -d --build

compose-down:
	docker-compose down

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
dev-setup: install-dev setup-db

dev-check: format lint type-check test ## Quick development check
	@echo "$(GREEN)✓ Development check complete!$(RESET)"

# CI/CD helpers

# Documentation

# Info
