AI Advisor
==========

The AI Advisor module provides intelligent recommendations for neural entrainment
parameters based on user state, historical responses, and flow state metrics.

Key Features
------------

* Personalized frequency recommendations
* Historical response analysis
* Real-time optimization
* Multi-objective parameter selection
* Confidence scoring

Classes
-------

AIAdvisor
~~~~~~~~~

.. autoclass:: ai_advisor.AIAdvisor
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from ai_advisor import AIAdvisor

    # Initialize the advisor
    advisor = AIAdvisor(api_key='your_key')

    # Get frequency recommendations
    recommendation = await advisor.get_frequency_recommendation(
        target_state='flow',
        user_state={
            'fatigue': 2.0,
            'time_of_day': 14,
            'caffeine_level': 1.0
        }
    )

    print(f"Recommended frequencies:")
    print(f"Base: {recommendation.base_freq} Hz")
    print(f"Beat: {recommendation.beat_freq} Hz")
    print(f"Confidence: {recommendation.confidence:.2f}")
