Skeleton app structure
======================
The project structure looks like this::

    flask_api
    ├── /app
    │   ├── /blueprints
    │   │   └── ...
    │   ├── /celery
    │   │   └── ...
    │   ├── /models
    │   │   └── ...
    │   ├── /templates
    │   │   └── ...
    │   ├── /utils
    │   │   └── ...
    │   ├── __init__.py
    │   ├── extensions.py
    │   └── middleware.py
    ├── /database
    │   ├── factories
    │   │   └── ...
    │   ├── migrations
    │   │   └── ...
    │   ├── seeds
    │   │   └── ...
    │   └── __init__.py
    ├── /log
    │   └── ...
    ├── /storage
    │   └── ...
    ├── /tests
    │   └── ...
    ├── config.py
    ├── manage.py
    └── requirements.txt

.. autosummary::
   :caption: Skeleton app structure
   :recursive:
   :toctree: _autosummary

   app
   database
   tests
   config
   manage
