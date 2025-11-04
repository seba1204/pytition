# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import re
import sys
from pathlib import Path

import django
from django.conf import settings as dj_settings

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
    "sphinx.ext.intersphinx",  # link to other projects' documentation
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_design",  # for nice admonitions
    "sphinxcontrib.mermaid",
]

# MyST (Markdown)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "attrs_block",
    "attrs_inline",
    "substitution",
    # "linkify",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# Napoleon (docstrings NumPy)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True  # show parameters in the "Parameters" section
napoleon_use_rtype = False  # show return type in the "Returns" section

# Autodoc/Autosummary
autosummary_generate = True
autodoc_member_order = "bysource"  # keep the order in source code
autodoc_typehints = "description"  # show typehints in description, not in signature
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Intersphinx (links to external documentation)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "build"]


# -- Options for HTML output -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = globals().get("html_css_files", [])
html_css_files += ["css/override.css"]
html_js_files = globals().get("html_js_files", [])
html_js_files += ["js/lang-switcher.js"]
html_favicon = "_static/favicon.ico"
html_theme_options = {
    "logo": {
        "text": "Pytition",
        "image_light": "_static/img/logo_light.svg",
        "image_dark": "_static/img/logo_dark.svg",
    },
    "icon_links": [
        {
            "name": "Forgejo",
            "url": "https://git.sebastienpont.fr/seba12/pytition",
            "icon": "_static/img/forgejo.svg",
            "type": "local",
        },
    ],
    "navbar_end": ["theme-switcher", "custom-lang-switcher", "navbar-icon-links"],
    "use_edit_page_button": False,
    # disable Prev/Next buttons
    "show_prev_next": False,
}
html_context = {
    "default_mode": "auto",
}

# --- i18n ---------------------------------------------------------------------
# *.po files are located at docs/locale/<lang>/LC_MESSAGES/*.po
locale_dirs = [str(Path(__file__).parent.parent / "locale")]
gettext_uuid = True  # avoid name clashes
gettext_compact = "messages"
gettext_additional_targets = ["literal-block"]  # also translate les blocs de code

# Default language
language = os.environ.get("SPHINX_LANGUAGE", "en")


# Get the list of available languages from Django settings
AVAILABLE_LANGS = [
    code for code, _name in getattr(dj_settings, "LANGUAGES", [("en", "English")])
]


# Function to get flag emoji for a given language code
def _flag(code):
    return {
        "en": "🇬🇧",
        "fr": "🇫🇷",
        "es": "🇪🇸",
        "de": "🇩🇪",
        "it": "🇮🇹",
        "pt": "🇵🇹",
        "nl": "🇳🇱",
        "pl": "🇵🇱",
        "cs": "🇨🇿",
        "sv": "🇸🇪",
        "fi": "🇫🇮",
        "ru": "🇷🇺",
        "uk": "🇺🇦",
        "tr": "🇹🇷",
        "ja": "🇯🇵",
        "ko": "🇰🇷",
    }.get(code.split("-")[0], "🌐")


html_context = {
    **html_context,
    "i18n_locales": [
        {
            "code": code,
            "name": dict(getattr(dj_settings, "LANGUAGES", [])).get(code, code),
            "flag": _flag(code),
        }
        for code in AVAILABLE_LANGS
    ],
    "default_lang": AVAILABLE_LANGS[0] if AVAILABLE_LANGS else "en",
}

# -- Misc ------------------------------------------------------------------------------
# todo extension (cf. https://www.sphinx-doc.org/en/master/usage/extensions/todo.html)
todo_include_todos = True
