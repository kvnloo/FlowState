Strobe Glasses
==============

The Strobe Glasses module controls LED strobe glasses for visual entrainment
and flow state induction.

Key Features
------------

* Frequency control
* Brightness adjustment
* Pattern generation
* Synchronization
* Safety monitoring

Classes
-------

StrobeGlasses
~~~~~~~~~~~~~

.. autoclass:: hardware.strobe_glasses.StrobeGlasses
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

StrobePattern
~~~~~~~~~~~~~

.. autoclass:: hardware.strobe_glasses.StrobePattern
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from hardware.strobe_glasses import StrobeGlasses, StrobePattern

    # Initialize strobe glasses
    glasses = StrobeGlasses()

    # Create strobe pattern
    pattern = StrobePattern(
        frequency=10.0,  # 10 Hz
        duty_cycle=0.5,  # 50% on/off
        brightness=0.7   # 70% brightness
    )

    # Start strobing
    glasses.start_strobe(pattern)

    # Adjust frequency in real-time
    glasses.set_frequency(12.0)  # Change to 12 Hz

    # Stop strobing
    glasses.stop()
