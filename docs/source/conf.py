# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
# Add project's root directory to the sys.path to enable autodoc to find your modules.
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'quicpro'
copyright = '2025, Jochen Schultz'
author = 'Jochen Schultz'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',    # Automatically document your API from docstrings.
    'sphinx.ext.napoleon',   # Support for Google and NumPy style docstrings.
    'sphinx.ext.viewcode',   # Add links to highlighted source code.
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'venv', '**/__pycache__']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']