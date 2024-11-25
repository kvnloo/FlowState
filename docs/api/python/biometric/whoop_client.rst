WHOOP Client
============

The WHOOP Client module integrates with the WHOOP API to collect and analyze
biometric data for flow state optimization.

Key Features
------------

* Real-time biometric data collection
* Recovery score tracking
* Strain analysis
* Sleep quality monitoring
* Historical data analysis

Classes
-------

WhoopClient
~~~~~~~~~~~

.. autoclass:: biometric.whoop_client.WhoopClient
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

WhoopMetrics
~~~~~~~~~~~~

.. autoclass:: biometric.whoop_client.WhoopMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

Example Usage
-------------

.. code-block:: python

    from biometric.whoop_client import WhoopClient

    # Initialize WHOOP client
    client = WhoopClient(api_key='your_whoop_api_key')

    # Get current metrics
    metrics = client.get_current_metrics()
    print(f"Recovery: {metrics.recovery_score}%")
    print(f"Strain: {metrics.day_strain}")
    print(f"Sleep Performance: {metrics.sleep_performance}%")

    # Get optimal training windows
    windows = client.get_optimal_training_windows()
    for window in windows:
        print(f"Optimal training time: {window.start_time} - {window.end_time}")
        print(f"Expected performance: {window.performance_score}%")
