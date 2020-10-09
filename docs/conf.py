# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'flask_api'
copyright = '2020, Rubén Rodríguez Ramírez'
author = 'Rubén Rodríguez Ramírez'
version = '1.3.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'm2r2',  # Convert md to rst files at build time
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',  # Core library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    'sphinx.ext.napoleon',
    'celery.contrib.sphinx',
    'sphinx_click',  # Support documentation from a click-based application
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

autosummary_generate = True  # Turn on sphinx.ext.autosummary

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

""" TODO: usage for showing private elements
def hide_non_private(app, what, name, obj, skip, options):
    # if private-members is set, show only private members
    if 'private-members' in options and not name.startswith('_'):
        # skip public methods
        return True
    else:
        # do not modify skip - private methods will be shown
        return None


def setup(app):
    app.connect('autodoc-skip-member', hide_non_private)
"""