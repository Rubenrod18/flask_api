# ============================================
# Dockerfile for Production Environment
# ============================================
# This Dockerfile sets up a lightweight Python environment optimized for production.

# -------------------------------------------
# Base Image Configuration
# -------------------------------------------
# Use the official Python 3.13 slim image as the base image.
# The slim variant is minimal and avoids unnecessary components, reducing image size.
FROM python:3.13-slim

# -------------------------------------------
# Environment Variable Setup
# -------------------------------------------
# Define key environment variables to configure paths and Python behavior:
# - HOMEDIR: Specifies the directory where the application will reside within the container.
# - PYTHONPATH: Ensures /src is included in Python's module search path, simplifying imports.
ENV HOMEDIR=/flask-api-docker-dir/ \
    PYTHONPATH=/src

# Accept an argument for the environment (e.g., "prod" or "local").
ARG ENVIRONMENT

# -------------------------------------------
# Set Working Directory
# -------------------------------------------
# Define the working directory for subsequent commands to ensure all file paths are relative to it.
WORKDIR $HOMEDIR

# -------------------------------------------
# Copy Application Source Code
# -------------------------------------------
# Copy the application source code from the host machine's 'src' directory to the container's HOMEDIR.
COPY ../src $HOMEDIR

# -------------------------------------------
# Install System-Level Dependencies
# -------------------------------------------
RUN apt-get update && apt-get install --assume-yes \
  build-essential gcc \
  libmagic-dev \
  git \
  python3-dev default-libmysqlclient-dev pkg-config \
  libreoffice-writer \
  && rm -rf /var/lib/apt/lists/*

# -------------------------------------------
# Install Python Dependencies
# -------------------------------------------
RUN pip install -r requirements-dev.txt

# -------------------------------------------
# Initialize Git Repository (Optional)
# -------------------------------------------
# Create a Git repository within the container.
# This step is optional but useful if tools like pre-commit hooks or versioning rely on Git.
RUN git init

# -------------------------------------------
# Expose Application Port
# -------------------------------------------
# Expose port 5000 to allow external access to the Flask application running in the container.
EXPOSE 5000

# -------------------------------------------
# Copy Custom Executable Scripts
# -------------------------------------------
# Copy executable scripts and configuration files from the host to standard locations in the container.
# These scripts may include commands for running, building, or debugging the application.
COPY docker/bin/* /usr/local/bin/
COPY docker/etc/* /usr/local/etc/

# -------------------------------------------
# Default Command
# -------------------------------------------
# Define the command to run when the container starts.
# Use a production-ready server like Gunicorn for better performance and scalability.
CMD ["/usr/local/bin/gunicorn.sh"]
