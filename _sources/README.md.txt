# FlowState Documentation

This directory contains the unified documentation for the FlowState project, covering both Python backend and JavaScript frontend components.

## Building Documentation

### Prerequisites

1. Python dependencies:
```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-js
```

2. Node.js dependencies:
```bash
npm install -g jsdoc jsdoc-mermaid
```

### Building Locally

To build all documentation:
```bash
make all
```

To build only Python documentation:
```bash
make html
```

To build only JavaScript documentation:
```bash
make js
```

### Viewing Documentation

After building, open `_build/html/index.html` in your browser to view the documentation.

## Documentation Structure

- `/docs/`: Main documentation source
  - `index.rst`: Main entry point
  - `features/`: Feature documentation
  - `architecture/`: System architecture
  - `api/`: API documentation
    - `python/`: Python API docs
    - `javascript/`: JavaScript API docs
  - `algorithms/`: Algorithm documentation

## Contributing

1. Follow the established documentation format for both Python and JavaScript files
2. Update implementation status with dates
3. Include dependencies and integration points
4. Provide clear examples
5. Run `make all` locally to verify changes

## Automated Building

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch. See `.github/workflows/docs.yml` for details.
