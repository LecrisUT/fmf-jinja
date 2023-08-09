from __future__ import annotations

# -- Project information -----------------------------------------------------

project = "FMF-Jinja"
author = "Cristian Le"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

source_suffix = [".md"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

linkcheck_anchors_ignore = [
    # This seems to be broken on GitHub readmes
    "default-versioning-scheme",
    "git-archives",
]
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"


# -- Extension configuration -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "substitution",
    "deflist",
]
