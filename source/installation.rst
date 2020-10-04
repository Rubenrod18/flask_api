Installation
============

1. Install Linux packages: these packages are required for the project installation.

.. code-block:: console

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install autoconf build-essential cmake libcap-dev libffi-dev libpcre3-dev librabbitmq-dev libreoffice-writer libtool libxml2-dev libxslt1-dev libxslt1.1 pkg-config magic nginx python3-distutils python3.7 python3.7-dev python3.7-venv rabbitmq-server uuid-dev uwsgi uwsgi-src
    sudo reboot

2. RabbitMQ configuration: we will enable required plugins for monitoring our brokers in Flower.

.. code-block:: console

    sudo rabbitmq-plugins enable rabbitmq_management
    sudo service rabbitmq-server restart

3. Install project Python dependencies:

.. code-block:: console

    python3.7 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --no-cache-dir

4. Project domain configuration: add local domain to our */etc/hosts* file in guest host.

.. code-block:: console

    127.0.0.1 flask-api.prod

5. Environment configuration: create a new **.env** file based on *.env.example* file in the root project and we fill all variables.

6. uWSGI configuration: create a new **uwsgi.ini** file based on *uwsgi.ini.example* file in the root project and we fill all variables. You must replace "username" and "project_path" values if was required, the "www-data" group must to be added to your user:

.. code-block::

    sudo usermod -a -G www-data username

7. Nginx configuration:  create a new **flask_api** file based on *config/flask_api.nginx.example* file. Replace "uwsgi_pass" variable with the value in "socket" variable from **uwsgi.ini** file:

.. code-block:: console

    sudo mv config/flask_api /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/flask_api /etc/nginx/sites-enabled/flask_api
    sudo systemctl restart nginx

8. Create a new **supervisord.conf** file based on *config/supervisor/supervisord.conf.example* file in the root project. Below "Mr Developer" comment you must replace "username" and "path" variables with appropriate values.

9. Create new **celery.conf**, **flower.conf** and **uwsgi.conf** files based on *config/supervisor/celery.conf.example*, *config/supervisor/flower.conf.example* and *config/supervisor/uwsgi.conf.example* files files in the "config/supervisor" directory. You must replace "username" and "path" variables with appropriate values.

10. We need to create next log directories: "log/app" and "log/supervisor".

11. Create new supervisor systemd unit file, create a new **flask_api_supervisor.service** file based on *config/flask_api_supervisor.service.example* file in the config directory. We fill "username", "usergroup" and "path" variables, move file to "/etc/systemd/system" directory and we run next commands:

.. code-block:: console

    sudo systemctl enable flask_api_supervisor.service
    sudo systemctl daemon-reload
    sudo systemctl start flask_api_supervisor.service

The systemd unit file and supervisor configuration allow us have our project always start up when the system is reboot.

For checking process status in command line:

.. code-block:: console

    sudo systemctl status flask_api_supervisor.service

For restart all processes in command line:

.. code-block:: console

    sudo systemctl restart flask_api_supervisor.service

This command reread the supervisor configuration files, stop all processes and start them again.


How to usage
------------

The setup is finished, we only need to create the database tables and fill them with fake data. We open a terminal in the root project and run next commands:

.. code-block:: console

    ./venv/bin/flask init-db
    ./venv/bin/flask migrate
    ./venv/bin/flask seed

You can use an API client such as Insomnia or Postman and starting to consume the API!

You can see the processes status here: http://flask-api.prod/supervisor.

The credentials are user:123 by default you can change the credentials
as you wish in supervisord.conf file in "inet_http_server" section.

You can management the Celery tasks status here: http://flask-api.prod/flower.


Optional installation
---------------------

This project use `logrotate <https://linux.die.net/man/8/logrotate>`_ for logging configuration. The config file is already defined you only need to do these steps:

1. Create new **flask_api.logrotate** file based on *config/flask_api.logrotate.example* file.
2. Update "path", "username" and "usergroup" variables with appropiate values.
3. Move flask_api_logrotate to "/etc/logrotate.d":

.. code-block:: console

    sudo mv config/flask_api.logrotate /etc/logrotate.d

4. Restart logrotate service:

.. code-block:: console

    sudo service log rotate restart

Now a new log file will be created every day.
