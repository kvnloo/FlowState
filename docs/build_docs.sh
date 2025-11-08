#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define the paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
DOCS_DIR="$ROOT_DIR/docs"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Navigate to the docs directory to use its Pipfile
cd "$DOCS_DIR"
echo -e "${YELLOW}Installing documentation dependencies...${NC}"
pipenv install

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf "$DOCS_DIR/_build"
rm -rf "$DOCS_DIR/api/*.rst"

# Generate API documentation from backend docstrings
echo -e "${YELLOW}Generating backend API documentation...${NC}"
pipenv run sphinx-apidoc -f -o api "$BACKEND_DIR" \
    --implicit-namespaces \
    --separate \
    --module-first \
    --no-toc \
    "$BACKEND_DIR/venv" \
    "$BACKEND_DIR/.venv" \
    "$BACKEND_DIR/tests" \
    "$BACKEND_DIR/__pycache__"

# TODO: Generate frontend documentation (if needed)
# echo -e "${YELLOW}Generating frontend documentation...${NC}"
# Additional frontend doc generation can be added here

# Build the Sphinx HTML documentation
echo -e "${YELLOW}Building HTML documentation...${NC}"
pipenv run sphinx-build -b html "$DOCS_DIR" "$DOCS_DIR/_build/html"

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Documentation built successfully!${NC}"
    echo -e "${GREEN}View documentation at: file://$DOCS_DIR/_build/html/index.html${NC}"

    # Optional: Open in browser (uncomment if desired)
    # if command -v xdg-open > /dev/null 2>&1; then
    #     xdg-open "$DOCS_DIR/_build/html/index.html"
    # elif command -v open > /dev/null 2>&1; then
    #     open "$DOCS_DIR/_build/html/index.html"
    # fi
else
    echo -e "${RED}❌ Documentation build failed!${NC}"
    exit 1
fi
