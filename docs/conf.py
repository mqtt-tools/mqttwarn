# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "mqttwarn"
copyright = "2014-2023, Jan-Piet Mens, Ben Jones, Andreas Motl"
author = "Jan-Piet Mens, Ben Jones, Andreas Motl"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_togglebutton",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.ifconfig",
    "sphinxext.opengraph",
]


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "mqttwarn-logo.png"
html_show_sourcelink = True


# == Extension configuration ==========================================

todo_include_todos = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "myst": ("https://myst-parser.readthedocs.io/en/latest", None),
}
linkcheck_ignore = [r"https://www.researchgate.net/publication/.*"]
sphinx_tabs_valid_builders = ["linkcheck"]


# -- Options for MyST -------------------------------------------------
myst_heading_anchors = 3
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
    "strikethrough",
    "tasklist",
]

# -- Options for sphinx-copybutton ------------------------------------
copybutton_remove_prompts = True
copybutton_line_continuation_character = "\\"
copybutton_prompt_text = r">>> |\.\.\. |\$ |sh\$ |PS> |cr> |mysql> |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for sphinxext-opengraph ----------------------------------
ogp_site_url = "https://mqttwarn.readthedocs.io/"
ogp_image = "https://mqttwarn.readthedocs.io/en/latest/_static/mqttwarn-logo.png"
ogp_description_length = 300
ogp_enable_meta_description = True
