Chaos System
------------

This module implements a chaos-based system for introducing controlled variability in flow state optimization.

Key Features
------------

* Lorenz attractor-based chaos generation
* Controlled entropy injection
* Dynamic system parameter adaptation
* Lyapunov exponent calculation

Classes
-------

ChaosSystem
~~~~~~~~~~~

.. autoclass:: flow.chaos_system.ChaosSystem
   :members:
   :undoc-members:
   :show-inheritance:

ChaosGenerator
~~~~~~~~~~~~~~

.. autoclass:: flow.chaos_system.ChaosGenerator
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: flow.chaos_system.apply_chaos
.. autofunction:: flow.chaos_system.generate_chaos_sequence
.. autofunction:: flow.chaos_system.calculate_lyapunov_exponent

Example Usage
-------------

.. code-block:: python

    from flow.chaos_system import ChaosSystem, generate_chaos_sequence

    # Initialize the chaos system
    chaos_system = ChaosSystem()

    # Generate a chaos sequence
    sequence = generate_chaos_sequence(
        length=1000,
        initial_conditions=[0.1, 0.1, 0.1]
    )

    # Apply chaos to a parameter
    modified_param = chaos_system.apply_chaos(
        param_value=0.5,
        chaos_strength=0.1
    )
