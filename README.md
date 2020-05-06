# flask-api

Prerequisites:
- sudo apt-get update
- sudo apt-get install libreoffice-writer libxml2-dev libxslt1-dev
  libxslt1.1 libffi-dev librabbitmq-dev rabbitmq-server


For logging configuration this application use [logrotate](https://linux.die.net/man/8/logrotate). The config
file is defined you only need:
1. Update the path to flask_api project in flask_api.logrotate file
2. Move flask_api_logrotate to /etc/logrotate.d
3. Restart logrotate service: sudo service log rotate restart

A new log file will be created every day in log/app path.

flask_api.service is a systemd unit file will allow Ubuntu’s init system
to automatically start uWSGI and serve the Flask application whenever
the server boots.
