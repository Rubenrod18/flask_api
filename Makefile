.PHONY: run component shell migrate migrate-rollback linter coverage coverage-html test test-parallel
VENV := venv

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make COMMAND\033[36m\033[0m\n\n  A general utility script.\n\n  Provides commands to run the application, database migrations, tests, etc.\n  Next command start up the application:\n\n    \44 make run\n\nCommands:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m \t%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# =============================
# ==== DOCKER COMMANDS ========
# =============================
build:  ## Build Docker app
	docker compose build --no-cache

run:  ## Run web server
	docker compose up

# ================================
# ==== APPLICATION COMMANDS ======
# ================================
shell:  ## Shell context for an interactive shell for this application
	docker compose exec app flask shell

# =============================
# ==== DATABASE COMMANDS ======
# =============================
init-db:  ## Create database tables
	docker compose exec app flask init-db

migrate:  ## Upgrade to a later database migration
	docker compose exec app flask migrate

migrate-rollback:  ## Revert to a previous database migration
	docker compose exec app flask migrate-rollback

seed:  ## Fill database with fake data
	docker compose exec app flask seed

# ==============================================
# ==== COVERAGE, LINTER AND TEST COMMANDS ======
# ==============================================
coverage: ## Report coverage statistics on modules
	docker compose exec app coverage report -m

coverage-html: ## Create an HTML report of the coverage of the files
	docker compose exec app coverage html

linter:  ## Analyzes code and detects various errors
	docker compose exec app pre-commit run flake8 --all-files

test: ## Run tests
	docker compose exec app coverage run -m pytest

test-one: ## Run only one test by name
	docker compose exec app coverage run -m pytest -k '$(test)'

test-path: ## Run only one test by path
	docker compose exec app coverage run -m pytest '$(path)'

# TODO: this command is not available yet
# test-parallel:  ## Run tests in parallel
#	docker compose exec app nosetests -w app --processes=-1
