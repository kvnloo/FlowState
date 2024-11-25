Visual Processor
================

The Visual Processor module analyzes visual input and generates optimal visual
entrainment patterns for flow state induction.

Key Features
------------

* Pattern generation
* Visual analysis
* Entrainment optimization
* Safety monitoring
* Pattern adaptation

Classes
-------

VisualProcessor
~~~~~~~~~~~~~~~

.. autoclass:: visual.visual_processor.VisualProcessor
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

VisualPattern
~~~~~~~~~~~~~

.. autoclass:: visual.visual_processor.VisualPattern
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from visual.visual_processor import VisualProcessor

    # Initialize visual processor
    processor = VisualProcessor()

    # Generate entrainment pattern
    pattern = processor.generate_pattern(
        target_frequency=10.0,
        intensity=0.7,
        color_scheme='blue'
    )

    # Analyze visual input
    analysis = processor.analyze_input(visual_data)
    print(f"Pattern Effectiveness: {analysis.effectiveness}")
    print(f"Safety Score: {analysis.safety_score}")

    # Adapt pattern based on analysis
    if analysis.requires_adaptation:
        pattern = processor.adapt_pattern(pattern, analysis)
