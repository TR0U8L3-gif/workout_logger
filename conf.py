# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django
sys.path.insert(0, os.path.abspath('../workout_logger'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'workout_logger.settings'
django.setup()

project = 'workout Logger'
copyright = '2024, Radosław Sienkiewicz, Mateusz Lewocz, Wojciech Szoda, Jan Rydzewski'
author = 'Radosław Sienkiewicz, Mateusz Lewocz, Wojciech Szoda, Jan Rydzewski'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
