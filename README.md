# flask-api

First maybe you need to install next external applications for trying
the application:
- sudo apt-get update
- sudo apt-get install libreoffice-writer libxml2-dev libxslt1-dev
  libxslt1.1 libffi-dev librabbitmq-dev rabbitmq-server

flask_api.service is a systemd unit file will allow Ubuntu’s init system
to automatically start uWSGI and serve the Flask application whenever
the server boots.
