# FlowState Documentation

This directory contains the unified documentation for the FlowState project, covering both Python backend and JavaScript frontend components.

## Building Documentation

### Prerequisites

1. Python dependencies:
```bash
  python -m pip install --upgrade pip
  pip install pipenv
  pipenv install
```

### Viewing Documentation

After building, open `_build/html/index.html` in your browser to view the documentation.

## Documentation Structure

- `/docs/`: Main documentation source
  - `index.rst`: Main entry point for documentation
  - `conf.py`: Sphinx configuration file
  - `Makefile`: Build automation
  - `build_docs.sh`: Documentation build script
  - `fix_rst_underlines.py`: RST formatting utility
  - `/api/`: API Documentation
    - `index.rst`: API documentation entry point
    - `/python/`: Python API documentation
      - `adaptive_audio_engine.rst`: Audio engine documentation
      - `ai_advisor.rst`: AI advisor system
      - `flow_state_detector.rst`: Flow state detection
      - `health_tracking.rst`: Health tracking system
      - `/attention/`: Attention system documentation
        - `attention_maximizer.rst`: Attention optimization
      - `/biometric/`: Biometric tracking
        - `tobii_tracker.rst`: Eye tracking
        - `whoop_client.rst`: Whoop integration
      - `/eeg/`: EEG processing
        - `realtime_processor.rst`: Real-time EEG processing
      - `/flow/`: Flow state algorithms
        - `chaos_system.rst`: Chaos system
        - `recovery_system.rst`: Recovery system
        - `stability_system.rst`: Stability system
      - `/hardware/`: Hardware integration
        - `strobe_glasses.rst`: Strobe glasses control
      - `/research/`: Research system
        - `research_system.rst`: Research framework
      - `/visual/`: Visual processing
        - `visual_processor.rst`: Visual processing system
  - `/architecture/`: System architecture
    - `index.rst`: Architecture overview
    - `algorithm_design.md`: Algorithm specifications
    - `api_integration.md`: API integration details
    - `data_flow.mermaid`: Data flow diagrams
    - `entropy-chaos-algorithm.md`: Entropy system
    - `flow_system_diagram.mermaid`: System architecture diagrams
    - `flowstate_optimization_algorithms.md`: Optimization algorithms
    - `health_tracking.rst`: Health tracking architecture
    - `initial_feedback_loop.md`: Feedback system
    - `quantum.md`: Quantum computing integration
    - `variables.md`: System variables
  - `/development/`: Development guides
    - `index.rst`: Development documentation entry
    - `completed.md`: Completed features
    - `FEATURES.md`: Feature specifications
    - `implementation_status.md`: Implementation status
    - `in-line-docs-template.md`: Documentation templates
    - `llm_workflow.md`: LLM integration workflow
    - `planned.md`: Planned features
    - `priority_queue.md`: Development priorities
    - `priority_queue_2.md`: Additional priorities
  - `/research/`: Research documentation
    - `index.rst`: Research overview
    - `/findings/`: Research findings
      - `index.rst`: Findings overview
    - `/papers/`: Research papers
  - `/inspo/`: Design inspiration assets
    - Various image assets (*.jpg)
  - `/_static/`: Static assets
  - `/_build/`: Generated documentation

## Linking to Documentation Pages

### In Markdown Files (.md)
```markdown
<!-- Link to a page in the same directory -->
[Implementation Status](implementation_status.md)

<!-- Link to a page in another directory -->
[API Documentation](api/index.rst)
[Flow State Detection](api/python/flow_state_detector.rst)

<!-- Link to the deployed version (GitHub Pages) -->
[Online Documentation](https://flowstate.github.io/flowstate/)
[Architecture Overview](https://flowstate.github.io/flowstate/architecture/index.html)
```

### In RST Files (.rst)
```rst
.. Link to another RST file
:doc:`/api/index`

.. Link with custom text
:doc:`API Documentation </api/index>`

.. Link to a section in any document
:ref:`implementation-status`

.. External link
`FlowState Online Docs <https://flowstate.github.io/flowstate/>`_
```

### Quick Links
- [Main Index](https://flowstate.github.io/flowstate/_build/html/index.html)

## Contributing

1. Follow the established documentation format for both Python and JavaScript files
2. Update implementation status with dates
3. Include dependencies and integration points
4. Provide clear examples
5. Run `make all` locally to verify changes

## Automated Building

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch. See `.github/workflows/docs.yml` for details.

[View Documentation](https://flowstate.github.io/flowstate/)
