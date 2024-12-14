Health Tracking API
================

This section documents the Health Tracking API components.

Data Models
----------

.. module:: backend.models.health_metrics

User
~~~~

.. autoclass:: User
   :members:
   :undoc-members:
   :show-inheritance:

SleepMetrics
~~~~~~~~~~~

.. autoclass:: SleepMetrics
   :members:
   :undoc-members:
   :show-inheritance:

NutritionMetrics
~~~~~~~~~~~~~~

.. autoclass:: NutritionMetrics
   :members:
   :undoc-members:
   :show-inheritance:

ExerciseMetrics
~~~~~~~~~~~~~

.. autoclass:: ExerciseMetrics
   :members:
   :undoc-members:
   :show-inheritance:

BiometricMetrics
~~~~~~~~~~~~~~

.. autoclass:: BiometricMetrics
   :members:
   :undoc-members:
   :show-inheritance:

MoodMetrics
~~~~~~~~~~

.. autoclass:: MoodMetrics
   :members:
   :undoc-members:
   :show-inheritance:

GraphQL API
---------

.. module:: backend.api.health.schema

Queries
~~~~~~~

.. autoclass:: Query
   :members:
   :undoc-members:
   :show-inheritance:

Mutations
~~~~~~~~

.. autoclass:: Mutation
   :members:
   :undoc-members:
   :show-inheritance:

Data Providers
------------

.. module:: backend.core.inputs.health.providers

Base Provider
~~~~~~~~~~~

.. autoclass:: HealthDataProvider
   :members:
   :undoc-members:
   :show-inheritance:

Apple Health
~~~~~~~~~~

.. autoclass:: AppleHealthProvider
   :members:
   :undoc-members:
   :show-inheritance:

Google Fit
~~~~~~~~

.. autoclass:: GoogleFitProvider
   :members:
   :undoc-members:
   :show-inheritance:

MyFitnessPal
~~~~~~~~~~

.. autoclass:: MyFitnessPalProvider
   :members:
   :undoc-members:
   :show-inheritance:

Oura
~~~~

.. autoclass:: OuraProvider
   :members:
   :undoc-members:
   :show-inheritance:

Whoop
~~~~~

.. autoclass:: WhoopProvider
   :members:
   :undoc-members:
   :show-inheritance:

Sync Service
----------

.. module:: backend.core.inputs.health.sync_service

.. autoclass:: HealthDataSyncService
   :members:
   :undoc-members:
   :show-inheritance:
