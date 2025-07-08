import logging
import os

from flask import Flask


def init_logging(app: Flask) -> None:
    _clear_existing_handlers(app)
    handlers = [_create_console_handler(app)]
    _attach_handlers(app, handlers)


def _clear_existing_handlers(app: Flask) -> None:
    """Remove all existing handlers from the Flask app logger to prevent duplicate logs."""
    del app.logger.handlers[:]


def _create_console_handler(app: Flask) -> logging.Handler:
    """Create and configure a console (stream) log handler."""
    console_handler = logging.StreamHandler()
    log_level = app.config.get('LOGGING_LEVEL', logging.INFO)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
        )
    )
    return console_handler


def _attach_handlers(app: Flask, handlers: list) -> None:
    """Attach handlers to the app logger and configure logger properties."""
    logger = app.logger
    for handler in handlers:
        logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(app.config.get('LOGGING_LEVEL', logging.INFO))
    logger.debug(f' Application environment: {os.getenv("FLASK_CONFIG")}')

    if app.config.get('SQLALCHEMY_LOGGING_ENABLED'):
        sa_logger = logging.getLogger('sqlalchemy.engine')
        sa_logger.setLevel(app.config.get('LOGGING_LEVEL', logging.INFO))
        if not sa_logger.hasHandlers():
            sa_logger.addHandler(logging.StreamHandler())
