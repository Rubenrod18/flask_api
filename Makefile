.PHONY: help _build

# Docker
REGISTRY = rubenrod18/flask_api
CACHE_KEY = cache_python_3.13_pip
LOCAL_VERSION ?= local

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make COMMAND\033[36m\033[0m\n\n  A general utility script.\n\n  Provides commands to run the application, database migrations, tests, etc.\n\nCommands:\n"} /^[a-zA-Z_.-]+:.*?##/ { printf "  \033[36m%-14s\033[0m \t%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

prod.build:  # Builds a Docker image with cache tags.
	docker build . \
		--build-arg ENVIRONMENT=production \
		--tag $(REGISTRY):$(LOCAL_VERSION) \
		--tag $(REGISTRY):$(CACHE_KEY) \
		--file docker/Dockerfile \
		--cache-from python:3.13-slim \
		--cache-from $(REGISTRY):$(LOCAL_VERSION) \
		--cache-from $(REGISTRY):$(CACHE_KEY)

## === LOCAL ENVIRONMENT ===

_build:
	docker build . \
		--build-arg ENVIRONMENT=local \
		--tag $(REGISTRY):$(LOCAL_VERSION) \
		--tag $(REGISTRY):$(CACHE_KEY) \
		--file docker/Dockerfile \
		--cache-from python:3.13-slim \
		--cache-from $(REGISTRY):$(LOCAL_VERSION) \
		--cache-from $(REGISTRY):$(CACHE_KEY)

local.build: _build  ## Build the Docker images without using the cache.
	docker compose build --no-cache

local.start:  ## Create and start Docker containers in detached mode, rebuilding images if necessary.
	docker compose up --build --detach

local.stop:  ## Stop running Docker containers without removing them.
	docker compose stop

local.down:  ## Stop and remove Docker containers, networks, volumes, and orphaned containers.
	docker compose down --volumes --remove-orphans

local.logs:  ## View logs from all Docker containers (following logs in real-time).
	docker compose logs -f
