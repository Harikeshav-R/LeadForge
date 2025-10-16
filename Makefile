# ====================================================================================
# Commands are separated into Development, Production, and General Utility sections.
# ====================================================================================

# Use bash for better scripting
SHELL := /bin/bash

# Define compose files to avoid repetition
DEV_COMPOSE_FILE := -f docker-compose.dev.yml
PROD_COMPOSE_FILE := -f docker-compose.prod.yml

# Default command to run when 'make' is called without arguments
.DEFAULT_GOAL := help

# Phony targets prevent conflicts with files of the same name
.PHONY: help dev build up down stop restart logs logs-backend logs-frontend shell-backend shell-db prod prod-build prod-down prod-stop prune

# --- General Utility Commands ---

help:
	@echo "================================================================"
	@echo "  Makefile for HackOHIO Project				       "
	@echo "================================================================"
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

prune: down ## 🧹 Clean up the system by removing all stopped containers, unused networks, and dangling images.
	@echo "Pruning Docker system..."
	@docker system prune -af

# --- Development Environment Commands ---

dev: up ## Start the development environment with hot-reloading (alias for 'up').

up: ## Start the development environment with hot-reloading.
	@echo "Starting development containers (with hot-reloading)..."
	@docker-compose $(DEV_COMPOSE_FILE) up --build

build: ## Force a rebuild of all development images without starting containers.
	@echo "Building development images..."
	@docker-compose $(DEV_COMPOSE_FILE) build

down: ## Stop and remove all development and production containers, networks, and volumes.
	@echo "Stopping all containers..."
	@docker-compose $(DEV_COMPOSE_FILE) down -v --remove-orphans
	@docker-compose $(PROD_COMPOSE_FILE) down -v --remove-orphans

stop: ## Stop running development containers without removing them.
	@echo "Stopping development containers..."
	@docker-compose $(DEV_COMPOSE_FILE) stop

restart: ## Restart all development services.
	@echo "Restarting development containers..."
	@make stop && make up

logs: ## View and follow logs for all running development services.
	@echo "Following logs for all development services..."
	@docker-compose $(DEV_COMPOSE_FILE) logs -f

logs-backend: ## View and follow logs for the backend service only.
	@echo "Following backend logs..."
	@docker-compose $(DEV_COMPOSE_FILE) logs -f backend

logs-frontend: ## View and follow logs for the frontend service only.
	@echo "Following frontend logs..."
	@docker-compose $(DEV_COMPOSE_FILE) logs -f frontend

shell-backend: ## Open a bash shell inside the running backend container.
	@echo "Opening bash shell in backend container..."
	@docker-compose $(DEV_COMPOSE_FILE) exec backend /bin/bash

shell-frontend: ## Open a bash shell inside the running backend container.
	@echo "Opening bash shell in frontend container..."
	@docker-compose $(DEV_COMPOSE_FILE) exec frontend /bin/bash

shell-db: ## Open a psql shell to interact with the PostgreSQL database.
	@echo "Opening psql shell in db container..."
	@docker-compose $(DEV_COMPOSE_FILE) exec db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2)


# --- Production Environment Commands ---

prod: ## Build and start the production environment in detached mode.
	@echo "Starting production containers in detached mode..."
	@docker-compose $(PROD_COMPOSE_FILE) up --build -d

prod-build: ## Build production images without starting containers.
	@echo "Building production images..."
	@docker-compose $(PROD_COMPOSE_FILE) build

prod-down: ## Stop and remove production containers, networks, and volumes.
	@echo "Stopping production containers..."
	@docker-compose $(PROD_COMPOSE_FILE) down -v --remove-orphans

prod-stop: ## Stop running production containers without removing them.
	@echo "Stopping production containers..."
	@docker-compose $(PROD_COMPOSE_FILE) stop
