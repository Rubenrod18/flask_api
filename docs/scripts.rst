Flask command line
==================
Flask command line allow run scripts for managing database,
start up task queues, etc.

You don't need to start up the server for running these scripts but you must
activate your virtual environment.

.. click:: manage:db
   :prog: flask init-db
   :nested: full

.. click:: manage:migrations
   :prog: flask migrate
   :nested: full

.. click:: manage:migration_rollback
   :prog: flask migrate-rollback
   :nested: full

.. click:: manage:seeds
   :prog: flask seeds
   :nested: full

.. click:: manage:celery
   :prog: flask celery
   :nested: full
