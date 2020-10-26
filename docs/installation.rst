Installation
============

1. Linux packages
-------------------------
These packages are required for the project installation:

.. code-block:: console

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install autoconf build-essential cmake libcap-dev libffi-dev libpcre3-dev librabbitmq-dev libreoffice-writer libtool libxml2-dev libxslt1-dev libxslt1.1 pkg-config magic nginx python3-distutils python3.7 python3.7-dev python3.7-venv rabbitmq-server uuid-dev uwsgi uwsgi-src
    sudo reboot

2. RabbitMQ configuration
-------------------------
Required plugins for monitoring our brokers in Flower:

.. code-block:: console

    sudo rabbitmq-plugins enable rabbitmq_management
    sudo service rabbitmq-server restart

3. Python dependencies
----------------------
Install Python dependencies:

.. code-block:: console

    python3.7 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --no-cache-dir

4. Domain configuration
-----------------------
Add local domain to our */etc/hosts* file:

.. code-block:: console

    127.0.0.1 flask-api.prod

5. Environment configuration
----------------------------
Create a new **.env** file based on *.env.example* file.

6. uWSGI configuration
----------------------
| Create a new **uwsgi.ini** file based on *uwsgi.ini.example*.
|
| *username* and *project_path* must to be filled with appropiate values.
|
| *www-data* group must to be added to your user:

.. code-block:: console

    sudo usermod -a -G www-data username

7. Nginx configuration
----------------------
| Create a new **flask_api** file based on *docs/examples/flask_api.nginx.example* file.
|
| Replace *uwsgi_pass* variable with the value in *socket* variable from **uwsgi.ini** file.
|
| Move **flask_api** file to */etc/nginx/sites-available* directory:

.. code-block:: console

    sudo mv docs/examples/flask_api /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/flask_api /etc/nginx/sites-enabled/flask_api
    sudo systemctl restart nginx

8. Supervisor configuration
---------------------------

8.1 Main configuration
~~~~~~~~~~~~~~~~~~~~~~
| Create a new **supervisord.conf** file based on *docs/examples/supervisor/supervisord.conf.example* file in the root project.
|
| *command*, *directory* and *username* variables must to be filles with appropriate values. These variables are below *Mr Developer* comment.

8.2 Other configurations
~~~~~~~~~~~~~~~~~~~~~~~~
Create a new directory named *supervisor* in the root path and create next files
based on *docs/examples/supervisor* example files:

1. celery.conf
2. flower.conf
3. uwsgi.conf

*username* and *path* variables must to be replaced with appropriate values.

9. Log directories
------------------
Create next log directories:

1. log/app
2. log/celery
3. log/flower
4. log/uwsgi

10. Supervisor systemd unit file
--------------------------------
| Create a new **flask_api_supervisor.service** file based on *docs/examples/flask_api_supervisor.service.example* file.
|
| *username*, *usergroup* and *path* variables must to be filled with appropiate values.
|
| Move file to */etc/systemd/system* directory and we run next commands:

.. code-block:: console

    sudo systemctl enable flask_api_supervisor.service
    sudo systemctl daemon-reload
    sudo systemctl start flask_api_supervisor.service

| The systemd unit file start up the project if the system is reboot or shutdown.
|
| For checking process status in command line:

.. code-block:: console

    sudo systemctl status flask_api_supervisor.service

For restart all processes in command line:

.. code-block:: console

    sudo systemctl restart flask_api_supervisor.service

This command reread the supervisor configuration files, stop all processes and
start them again.


How to usage
------------

The setup is finished, we only need to create the database tables and fill
them with fake data. We open a terminal in the root project and run next commands:

.. code-block:: console

    ./venv/bin/flask init-db
    ./venv/bin/flask migrate
    ./venv/bin/flask seed

| You can use an API client such as Insomnia or Postman and starting to consume the API!
|
| You can see the processes status here: http://flask-api.prod/supervisor
|
| The credentials are user:123 by default, you can change the credentials in supervisord.conf file in *inet_http_server* section.
|
| You can management the Celery tasks status here: http://flask-api.prod:5555/flower/


Optional installation
---------------------

This project use |logrotate| for logging configuration. The config file is
already defined you only need to do these steps:

1. Create new **flask_api.logrotate** file based on *docs/examples/flask_api.logrotate.example*.
2. *path*, *username* and *usergroup* variables must to be filled with appropiate values.
3. Move flask_api_logrotate to */etc/logrotate.d*:

.. code-block:: console

    sudo mv docs/examples/flask_api.logrotate /etc/logrotate.d

4. Restart logrotate service:

.. code-block:: console

    sudo service log rotate restart

A new log file will be created every day.


.. |logrotate| raw:: html

   <a href="https://linux.die.net/man/8/logrotate" target="_blank">logrotate</a>
