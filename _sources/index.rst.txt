FlowState Documentation
=====================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   features/index
   architecture/index
   api/python/index
   api/javascript/index
   algorithms/index

Implementation Status
-------------------

.. include:: features/implementation_status.md
   :parser: myst_parser.sphinx_

Core Components
-------------

.. mermaid::

   graph TD
       A[Frontend UI] --> B[Flow State Detector]
       B --> C[Biometric Integration]
       B --> D[Audio Engine]
       C --> E[Whoop Client]
       C --> F[Tobii Tracker]
       D --> G[Binaural Beats]
       D --> H[Visual Strobing]
