Recovery System
===============

The Recovery System module provides mechanisms for recovering from suboptimal
flow states and managing transitions between different neural states.

Key Features
------------

* State transition management
* Recovery protocol selection
* Adaptation rate control
* Historical effectiveness tracking
* Real-time protocol adjustment

Classes
-------

RecoverySystem
~~~~~~~~~~~~~~

.. autoclass:: flow.recovery_system.RecoverySystem
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

RecoveryProtocol
~~~~~~~~~~~~~~~~

.. autoclass:: flow.recovery_system.RecoveryProtocol
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from flow.recovery_system import RecoverySystem

    # Initialize the recovery system
    recovery = RecoverySystem()

    # Get recovery protocol for current state
    protocol = recovery.get_protocol(
        current_state={
            'alpha': 0.3,  # Low alpha
            'theta': 0.8,  # High theta
            'beta': 0.6,   # Moderate beta
            'gamma': 0.4   # Normal gamma
        },
        target_state='flow'
    )

    # Apply recovery protocol
    recovery.apply_protocol(protocol)

    # Monitor effectiveness
    effectiveness = recovery.monitor_effectiveness()
