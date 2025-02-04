.PHONY: help run component shell migration migrate migrate-rollback seed linter coverage coverage-html test test-one test-path test-parallel

# Flask-migrate
MIGRATIONS_DIRECTORY ?= /flask-api-docker-dir/src/migrations
# Pytest
PARALLEL_TEST ?= auto
MAX_FAIL_TEST ?= 5


help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make COMMAND\033[36m\033[0m\n\n  A general utility script.\n\n  Provides commands to run the application, database migrations, tests, etc.\n  Next command start up the application:\n\n    \44 make run\n\nCommands:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m \t%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ================================
# ==== APPLICATION COMMANDS ======
# ================================
component:  ## Create a component scaffolding
	docker compose exec app flask component --name ${name}

shell:  ## Shell context for an interactive shell for this application
	docker compose exec app flask shell

# =============================
# ==== DATABASE COMMANDS ======
# =============================
migration:  ## Create a new migration based in new changes from database models
	docker compose exec app flask db migrate -m '$(msg)' --directory "${MIGRATIONS_DIRECTORY}"

migrate:  ## Upgrade to a later database migration
	docker compose exec app flask db upgrade --directory "${MIGRATIONS_DIRECTORY}"

migrate-rollback:  ## Revert to a previous database migration
	docker compose exec app flask db downgrade --directory "${MIGRATIONS_DIRECTORY}"

seed:  ## Fill database with fake data
	docker compose exec app flask seed

# ==============================================
# ==== COVERAGE, LINTER AND TEST COMMANDS ======
# ==============================================
coverage: ## Report coverage statistics on modules
	coverage run -m pytest && coverage report -m

coverage-html: ## Create an HTML report of the coverage of the files
	coverage run -m pytest && coverage html

test: ## Run tests
	pytest

test-parallel:  ## Run tests in parallel
	pytest --numprocesses=$(PARALLEL_TEST) --maxfail=$(MAX_FAIL_TEST)
