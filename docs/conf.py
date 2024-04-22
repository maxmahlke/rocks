# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("../rocks"))


# -- Project information -----------------------------------------------------

project = "rocks"
copyright = "2023, Max Mahlke"
author = "Max Mahlke"

# The full version, including alpha/beta/rc tags
release = "0.1"
html_title = "rocks"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "hoverxref.extension",
    "sphinx_design",
    "sphinx_copybutton",
]

# Print out todos in documentation?
todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


graphviz_output_format = "svg"


# ------
# hoverxref_role_types = {
#     "hoverxref": "modal",
#     "ref": "modal",  # for hoverxref_auto_ref config
#     "confval": "tooltip",  # for custom object
#     "mod": "tooltip",  # for Python Sphinx Domain
#     "class": "tooltip",  # for Python Sphinx Domain
#     "term": "tooltip",  # for Python Sphinx Domain
# }

hoverxref_roles = ["numref", "confval", "setting", "term"]

hoverxref_project = "rocks"
hoverxref_version = "latest"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "sphinx_redactor_theme"
# html_theme_path = [sphinx_redactor_theme.get_html_theme_path()]
html_theme = "furo"
html_static_path = ["_static"]
# html_logo = "gfx/logo_rocks.svg"

pygments_style = "monokai"
pygments_dark_style = "monokai"

html_show_copyright = False
html_show_sphinx = False


html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "top_of_page_button": None,
    "light_logo": "logo_rocks.svg",
    "dark_logo": "logo_rocks_light.svg",
    "announcement": "<em>rocks version 2 has landed</em> announcement! Check out the <a href='https://rocks.readthedocs.io/en/latest/v2.html'><font style='color:blue;'>migration guide</font></a> to see what's new.",
    # "logo_only": True,
    # "display_version": True,
    # "prev_next_buttons_location": "bottom",
    # "style_external_links": False,
    # "vcs_pageview_mode": "",
    # # "style_nav_header_background": "white",
    # # Toc options
    # "collapse_navigation": False,
    # "sticky_navigation": False,
    # "navigation_depth": 4,
    # "includehidden": True,
    # "titles_only": False,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_style = "css/custom.css"

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]
