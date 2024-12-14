#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
DOCS_DIR="$ROOT_DIR/docs"
BACKEND_DIR="$ROOT_DIR/backend"

# Navigate to the backend directory
cd "$BACKEND_DIR"
echo "Installing dependencies with pipenv..."
pipenv install

# Build the Sphinx documentation
echo "Building the documentation with Sphinx..."
pipenv run sphinx-build -b html "$DOCS_DIR" "$DOCS_DIR/_build/html"

echo "Documentation successfully built!"
# open "$DOCS_DIR"/_build/html/index.html
