"""Sphinx configuration for FlowState documentation."""

import os
import sys
sys.path.insert(0, os.path.abspath('../backend'))

project = 'FlowState'
copyright = '2024, FlowState Team'
author = 'FlowState Team'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_js',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme configuration
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# JavaScript documentation settings
js_source_path = '../frontend/src'
jsdoc_config_path = '../frontend/jsdoc.json'

# Markdown support
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Auto-generate API documentation
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Support for Mermaid diagrams
myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'dollarmath',
    'amsmath',
    'html_image',
]
