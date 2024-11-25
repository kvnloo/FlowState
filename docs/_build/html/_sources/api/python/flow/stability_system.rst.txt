Stability System
================

The Stability System module maintains stable neural entrainment by monitoring
and adjusting parameters to prevent unwanted state transitions.

Key Features
------------

* State stability monitoring
* Parameter drift detection
* Automatic stabilization
* Transition prevention
* Historical stability analysis

Classes
-------

StabilitySystem
~~~~~~~~~~~~~~~

.. autoclass:: flow.stability_system.StabilitySystem
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

StabilityMetrics
~~~~~~~~~~~~~~~~

.. autoclass:: flow.stability_system.StabilityMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from flow.stability_system import StabilitySystem

    # Initialize the stability system
    stability = StabilitySystem()

    # Monitor current stability
    metrics = stability.monitor_stability(
        current_state={
            'alpha': 0.7,
            'theta': 0.4,
            'beta': 0.3,
            'gamma': 0.2
        }
    )

    # Apply stabilization if needed
    if metrics.requires_stabilization:
        stability.apply_stabilization()
