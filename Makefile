.PHONY: help install dev test lint format clean docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev: ## Start development environment
	docker-compose -f FusionAI-Companion0/docker-compose.yml up -d
	python FusionAI-Companion0/main.py

test: ## Run tests
	python -m pytest tests/ -v

lint: ## Run linting
	flake8 .
	mypy .

format: ## Format code
	black .
	isort .

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-up: ## Start Docker services
	docker-compose -f FusionAI-Companion0/docker-compose.yml up -d

docker-down: ## Stop Docker services
	docker-compose -f FusionAI-Companion0/docker-compose.yml down

setup: ## Initial setup
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -r requirements-dev.txt
	docker-compose -f FusionAI-Companion0/docker-compose.yml up -d

health-check: ## Check system health
	python FusionAI-Companion0/health_check.py

quickstart: ## Quick start demo
	python FusionAI-Companion0/quickstart.py 