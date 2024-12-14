Adaptive Audio Engine
=====================

The Adaptive Audio Engine module provides real-time binaural beat generation with
dynamic frequency adaptation based on neural response and flow state metrics.

Key Features
------------

* Real-time binaural beat generation
* Neural response-based adaptation
* Phase coupling optimization
* Flow state-driven frequency selection
* AI-powered frequency recommendations

Classes
-------

UserState
~~~~~~~~~

.. autoclass:: adaptive_audio_engine.UserState
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FrequencyResponse
~~~~~~~~~~~~~~~~~

.. autoclass:: adaptive_audio_engine.FrequencyResponse
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FrequencyRecommendation
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: adaptive_audio_engine.FrequencyRecommendation
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

PhaseState
~~~~~~~~~~

.. autoclass:: adaptive_audio_engine.PhaseState
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

FrequencyAdaptation
~~~~~~~~~~~~~~~~~~~

.. autoclass:: adaptive_audio_engine.FrequencyAdaptation
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

AdaptiveAudioEngine
~~~~~~~~~~~~~~~~~~~

.. autoclass:: adaptive_audio_engine.AdaptiveAudioEngine
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    import asyncio
    from adaptive_audio_engine import AdaptiveAudioEngine

    async def main():
        # Initialize the engine
        engine = AdaptiveAudioEngine(api_key='your_key')
        
        # Start generating binaural beats for flow state
        strobe_freq = await engine.start(
            target_state='flow',
            user_state={'fatigue': 2.0, 'time_of_day': 14}
        )
        
        # Update with neural response
        engine.update_brainwave_response(
            alpha=0.8,  # Strong alpha
            theta=0.6,  # Moderate theta
            beta=0.4,   # Suppressed beta
            gamma=0.3   # Baseline gamma
        )
        
        # Stop the engine
        await engine.stop()

    asyncio.run(main())
