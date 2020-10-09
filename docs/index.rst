.. flask_api documentation master file, created by
   sphinx-quickstart on Sat Sep 26 17:38:13 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask Api
=========

Flask-api is a small API project for creating users and files (Microsoft Word and PDF). These files contain data about users registered in the project.

The project is developed in Python 3.7 and use next main libraries:

* |flask|: microframework.
* |sqlite|: SQL database engine.
* |peewee|: simple and small ORM.
* |celery|: asynchronous task queue/job.
* |rabbitmq|: message broker.
* |nginx|: web server, reverse proxy, etc.
* |uwsgi|: Web Server Gateway Interface (WSGI) server implementation.
* |flower|: monitoring and administrating Celery clusters.
* |supervisor|: client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems.


.. toctree::
   :maxdepth: 2
   :glob:
   :hidden:

   installation
   skeleton_app_structure
   scripts

.. toctree::
   :caption: Documentation
   :hidden:

   changelog

Note
====

If you find any bugs, odd behavior, or have an idea for a new feature please
don't hesitate to |github_issue_link| on GitHub.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |flask| raw:: html

   <a href="https://flask.palletsprojects.com" target="_blank">Flask</a>

.. |sqlite| raw:: html

   <a href="https://www.sqlite.org" target="_blank">Sqlite</a>

.. |peewee| raw:: html

   <a href="http://docs.peewee-orm.com/en/latest" target="_blank">Peewee</a>

.. |celery| raw:: html

   <a href="http://www.celeryproject.org" target="_blank">Celery</a>

.. |rabbitmq| raw:: html

   <a href="https://www.rabbitmq.com" target="_blank">RabbitMQ</a>

.. |nginx| raw:: html

   <a href="https://www.nginx.com" target="_blank">NGINX</a>

.. |uwsgi| raw:: html

   <a href="https://uwsgi-docs.readthedocs.io" target="_blank">UWSGI</a>

.. |flower| raw:: html

   <a href="https://flower.readthedocs.io/en/latest" target="_blank">Flower</a>

.. |supervisor| raw:: html

   <a href="http://supervisord.org" target="_blank">Supervisor</a>

.. |github_issue_link| raw:: html

   <a href="https://github.com/Rubenrod18/flask_api/issues?state=open" target="_blank">open an issue</a>
