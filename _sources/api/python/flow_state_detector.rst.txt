Flow State Detector
===================

The Flow State Detector module provides real-time detection and analysis of flow states
based on neural activity patterns and biometric data.

Key Features
------------

* Real-time flow state detection
* Multi-modal data integration
* Adaptive thresholding
* State transition tracking
* Confidence scoring

Classes
-------

FlowState
~~~~~~~~~

.. autoclass:: flow_state_detector.FlowState
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FlowFeatures
~~~~~~~~~~~~

.. autoclass:: flow_state_detector.FlowFeatures
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FlowMetrics
~~~~~~~~~~~

.. autoclass:: flow_state_detector.FlowMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FlowStateDetector
~~~~~~~~~~~~~~~~~

.. autoclass:: flow_state_detector.FlowStateDetector
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from flow_state_detector import FlowStateDetector

    # Initialize the detector
    detector = FlowStateDetector()

    # Process real-time data
    flow_state = detector.process_data(eeg_data, biometric_data)
    
    # Get flow state probability
    probability = flow_state.probability
    print(f"Flow state probability: {probability:.2f}")
