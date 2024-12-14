Tobii Tracker
=============

The Tobii Tracker module integrates with Tobii eye tracking hardware to monitor
visual attention and cognitive load during flow states.

Key Features
------------

* Real-time gaze tracking
* Fixation analysis
* Saccade detection
* Cognitive load estimation
* Attention pattern analysis

Classes
-------

TobiiTracker
~~~~~~~~~~~~

.. autoclass:: biometric.tobii_tracker.TobiiTracker
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

GazeMetrics
~~~~~~~~~~~

.. autoclass:: biometric.tobii_tracker.GazeMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from biometric.tobii_tracker import TobiiTracker

    # Initialize Tobii tracker
    tracker = TobiiTracker()

    # Start tracking
    tracker.start()

    # Get current gaze metrics
    metrics = tracker.get_gaze_metrics()
    print(f"Fixation Duration: {metrics.fixation_duration}ms")
    print(f"Saccade Velocity: {metrics.saccade_velocity}°/s")
    print(f"Cognitive Load: {metrics.cognitive_load}")

    # Stop tracking
    tracker.stop()
