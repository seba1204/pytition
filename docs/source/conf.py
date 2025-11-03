# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import re
import sys
from pathlib import Path

import django

# -- Chemins & Django ------------------------------------------------------------------
sys.path.insert(0, str(Path("..", "..", "src").resolve()))

# Configuring Django to import project modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# -- Project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Pytition"
copyright = "2025, Team Pytition"
author = "Team Pytition"

# The full version, including alpha/beta/rc tags
release = re.sub("^v", "", os.popen("git describe --tags").read().strip())
version = release

# -- General configuration -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # Numpy/Google docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinx_multiversion",
]

# MyST (Markdown)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "attrs_block",
    "attrs_inline",
    "substitution",
    "linkify",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# Napoleon (docstrings NumPy)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = False

# Autodoc/Autosummary
autosummary_generate = True
autodoc_typehints = "description"
autoclass_content = "both"

# Intersphinx (links to external documentation)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

templates_path = ["_templates"]
exclude_patterns = ["_build"]


# -- Options for HTML output -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "logo": {"text": "Pytition"},
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "use_edit_page_button": False,
}
html_context = {
    "default_mode": "auto",
}

# -- Misc ------------------------------------------------------------------------------
# todo extension (cf. https://www.sphinx-doc.org/en/master/usage/extensions/todo.html)
todo_include_todos = True
