# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FranKGraphbench'
copyright = '2026, Alvaro Jose Lopes and Paulo do Carmo'
author = 'Alvaro Jose Lopes and Paulo do Carmo'
release = '0.2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# logo conf
html_logo = "_static/frank-favicon.svg"
html_theme_options = {
    "logo_only": False, 
    "collapse_navigation": True,
    "style_nav_header_background": "#619B54",
}

html_css_files = [
    "frank.css",
]