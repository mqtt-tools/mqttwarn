# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mqttwarn'
copyright = '2014-2023, Jan-Piet Mens, Ben Jones, Andreas Motl'
author = 'Jan-Piet Mens, Ben Jones, Andreas Motl'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # https://github.com/executablebooks/MyST-Parser
    "myst_parser",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for MyST -------------------------------------------------

# https://github.com/executablebooks/MyST-Parser/issues/519
myst_heading_anchors = 3


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_logo = "mqttwarn-logo.png"
