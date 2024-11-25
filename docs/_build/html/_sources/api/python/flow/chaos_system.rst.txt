Chaos System
============

.. module:: flow.chaos_system

The Chaos System module introduces controlled randomness into neural entrainment parameters
to prevent habituation and maintain optimal stimulation levels.

Key Features
-----------

* Global chaos level control (0.0 - 1.0)
* Parameter-specific chaos injection
* Multiple chaos generators (Logistic, Hénon, Lorenz maps)
* Pattern learning and effectiveness tracking

Classes
-------

ChaosSystem
~~~~~~~~~~

.. autoclass:: ChaosSystem
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

ChaosGenerator
~~~~~~~~~~~~

.. autoclass:: ChaosGenerator
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Functions
--------

.. autofunction:: apply_chaos
.. autofunction:: generate_chaos_sequence
.. autofunction:: calculate_lyapunov_exponent

Usage Example
-----------

.. code-block:: python

    # Create a chaos system with default parameters
    chaos = ChaosSystem(global_chaos_level=0.3)

    # Generate a chaotic sequence
    sequence = chaos.generate_sequence(length=100)

    # Apply chaos to a parameter
    original_value = 440  # Hz
    chaotic_value = chaos.apply_chaos(original_value, parameter_name='frequency')

    # Calculate Lyapunov exponent for stability analysis
    lyap = chaos.calculate_lyapunov_exponent()
