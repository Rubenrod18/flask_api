.PHONY: help prod.build _build local.build local.start local.stop local.down local.logs

# Docker
REGISTRY = rubenrod18/flask_api
CACHE_KEY = cache_python_3.13_pip
LOCAL_VERSION ?= local

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make COMMAND\033[36m\033[0m\n\n  A general utility script.\n\n  Provides commands to run the application, database migrations, tests, etc.\n  Next command start up the application:\n\n    \44 make run\n\nCommands:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m \t%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Builds a Docker image with cache tags.
prod.build:
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

## Build the Docker images without using the cache.
local.build: _build
	docker compose build --no-cache

## Create and start Docker containers in detached mode, rebuilding images if necessary.
local.start:
	docker compose up --build --detach

## Stop running Docker containers without removing them.
local.stop:
	docker compose stop

## Stop and remove Docker containers, networks, volumes, and orphaned containers.
local.down:
	docker compose down --volumes --remove-orphans

## View logs from all Docker containers (following logs in real-time).
local.logs:
	docker compose logs -f
