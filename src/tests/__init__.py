"""Package for testing the application.

The tests package storages the application's tests that them are
executed for ensuring the proper behaviour of the application.

You can get report coverage stadistics with coverage package.

Notes
-----
There are three kinds of tests created:

1. Unit testing
    Unit testing means testing individual modules of an application in
    isolation (without any interaction with dependencies) to confirm
    that the code is doing things right.

2. Integration testing
    Integration testing means checking if different modules are working
    fine when combined together as a group.

3. Functional testing
    Functional testing means testing a slice of functionality in the
    system (may interact with dependencies) to confirm that the code
    is doing the right things.

Let us understand these three types of testing with an oversimplified
example.

E.g. For a functional mobile phone, the main parts required are
“battery” and “sim card”.

Unit testing Example – The battery is checked for its life, capacity
and other parameters. Sim card is checked for its activation.

Integration Testing Example – Battery and sim card are integrated i.e.
assembled in order to start the mobile phone.

Functional Testing Example – The functionality of a mobile phone is
checked in terms of its features and battery usage as well as sim
card facilities.

References
----------
`The Differences Between Unit Testing, Integration Testing and
Functional Testing
<https://www.softwaretestinghelp.com/the-difference-between-unit-integration-and-functional-testing/>`_.  # noqa

Examples
--------
How to usage::

    source venv/bin/activate
    pytest

How to call a specific test::

    source venv/bin/activate
    pytest tests/blueprints/test_base.py

How to call a specific test function::

    source venv/bin/activate
    pytest -k test_welcome_api

You can use coverage package for running tests as well::

    source venv/bin/activate
    coverage run -m pytest

And get a report coverage stadistics on modules::

    source venv/bin/activate
    coverage report -m

For a nicer presentation, use coverage html to get annotated HTML
listings detailing missed lines::

    source venv/bin/activate
    coverage html

References
----------
How can I test Celery tasks?

Depends on what exactly you want to be testing.

    - Test the task code directly. Don't call "task.delay(...)" just call "task(...)" from your unit tests.  # noqa
    - Use CELERY_ALWAYS_EAGER. This will cause your tasks to be called immediately at the point you say "task.delay(...)", so you can test the whole path (but not any asynchronous behavior).  # noqa

https://stackoverflow.com/questions/12078667/how-do-you-unit-test-a-celery-task  # noqa

"""
