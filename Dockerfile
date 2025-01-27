# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Workspace
ADD . /flask-api-docker-dir
WORKDIR /flask-api-docker-dir

# Linux dependencies
RUN apt-get update && apt-get install --assume-yes \
  build-essential gcc \
  sqlite3 \
  libsqlite3-dev \
  libmagic-dev \
  git

# Python depdendencies
RUN pip install -r requirements-dev.txt

RUN git init

# Enable Flask port
EXPOSE 5000

# Start up the application
# CMD ["python3", "manage.py", "runserver", "--host", "0.0.0.0"] # TODO: pending to define a production Dockerfile
CMD ["flask", "run", "--host", "0.0.0.0"]
