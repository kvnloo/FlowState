Realtime EEG Processor
======================

The Realtime EEG Processor module handles real-time processing and analysis of
EEG signals for neural entrainment and flow state detection.

Key Features
------------

* Real-time signal processing
* Frequency band decomposition
* Artifact rejection
* Phase synchronization tracking
* Power spectrum analysis

Classes
-------

EEGProcessor
~~~~~~~~~~~~

.. autoclass:: eeg.realtime_processor.EEGProcessor
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

SignalQuality
~~~~~~~~~~~~~

.. autoclass:: eeg.realtime_processor.SignalQuality
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

BandPowers
~~~~~~~~~~

.. autoclass:: eeg.realtime_processor.BandPowers
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from eeg.realtime_processor import EEGProcessor, BandPowers

    # Initialize the processor
    processor = EEGProcessor()

    # Process incoming EEG data
    band_powers = processor.process_data(eeg_data)

    # Get specific band power
    alpha_power = band_powers.alpha
    beta_power = band_powers.beta
