# noqa: D100
from __future__ import annotations

import os

project = "FMF-Jinja"
author = "Cristian Le"
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx_tippy",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx_autodoc_typehints",
    "sphinx_click",
]
templates_path = []
source_suffix = [".md"]
html_theme = "furo"


myst_enable_extensions = [
    "colon_fence",
    "substitution",
    "deflist",
    "attrs_block",
    "dollarmath",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.13/", None),
    "tmt": ("https://tmt.readthedocs.io/en/stable", None),
    "fmf": ("https://fmf--257.org.readthedocs.build/en/257", None),
    "jinja": ("https://jinja.palletsprojects.com/en/stable", None),
}
tippy_rtd_urls = [
    # Only works with RTD hosted intersphinx
    "https://tmt.readthedocs.io/en/stable",
    "https://fmf--257.org.readthedocs.build/en/257",
    "https://jinja.palletsprojects.com/en/stable",
]
autodoc_member_order = "bysource"

repo_slug = os.getenv("GITHUB_REPOSITORY", "LecrisUT/fmf-jinja")
# Using `GITHUB_REF` is not reliable for the `path` links
git_ref = os.getenv("GITHUB_SHA", "main")

extlinks = {
    "issue": ("https://github.com/LecrisUT/fmf-jinja/issues/%s", "issue %s"),
    "path": (f"https://github.com/{repo_slug}/tree/{git_ref}/%s", "%s"),
    "user": ("https://github.com/%s", "%s"),
}
