# noqa: D100
from __future__ import annotations

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
    "fmf": ("https://fmf.readthedocs.io/en/stable", None),
    "jinja": ("https://jinja.palletsprojects.com/en/stable", None),
}
tippy_rtd_urls = [
    # Only works with RTD hosted intersphinx
    "https://tmt.readthedocs.io/en/stable",
    "https://fmf.readthedocs.io/en/stable",
    "https://jinja.palletsprojects.com/en/stable",
]
autodoc_member_order = "bysource"
# TODO: Make extlinks git reference aware
extlinks = {
    "issue": ("https://github.com/LecrisUT/fmf-jinja/issues/%s", "issue %s"),
    "path": ("https://github.com/LecrisUT/fmf-jinja/tree/main/%s", "%s"),
    "user": ("https://github.com/%s", "%s"),
}
