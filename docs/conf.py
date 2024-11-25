"""Sphinx configuration for FlowState documentation."""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath('..'))

# Add virtualenv site-packages to Python path
virtualenv_path = os.getenv('VIRTUAL_ENV')
if virtualenv_path:
    site_packages = Path(virtualenv_path) / 'lib' / 'python3.11' / 'site-packages'
    sys.path.append(str(site_packages))

project = 'FlowState'
copyright = '2024, FlowState Team'
author = 'FlowState Team'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'myst_parser',
    'sphinxcontrib.mermaid',
]

myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "html_image",
    "linkify",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Mermaid configuration
mermaid_version = ""  # Latest version
mermaid_init_js = "mermaid.initialize({startOnLoad:true});"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme configuration
import revitron_sphinx_theme
html_theme = 'revitron_sphinx_theme'
html_theme_path = [revitron_sphinx_theme.get_html_theme_path()]

if not os.path.exists('_static'):
    os.makedirs('_static')
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'color_scheme': 'dark',
}

html_context = {
    'style': 'default',  # Provide a fallback value
}


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Auto-generate API documentation
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
