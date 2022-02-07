# syntax=docker/dockerfile:1
FROM python:3.8-alpine3.14

# Workspace
ADD . /flask-api-docker-dir
WORKDIR /flask-api-docker-dir

# Linux dependencies
RUN apk add --no-cache sqlite  # Install sqlite3 database
RUN apk add --no-cache gcc libc-dev linux-headers # uwsgi package dependencies
RUN apk add --no-cache libmagic # python-magic package dependency
RUN apk add --no-cache git # pre-commit package dependency

# Python depdendencies
RUN pip install -r requirements-dev.txt

RUN git init

# Enable Flask port
EXPOSE 5000

# Start up the application
# CMD ["python3", "manage.py", "runserver", "--host", "0.0.0.0"] # TODO: pending to define a production Dockerfile
CMD ["flask", "run", "--host", "0.0.0.0"]
