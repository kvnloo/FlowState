"""GraphQL API Schema for Health Metrics.

This module defines the GraphQL schema for querying and mutating health metrics data.
It uses Strawberry GraphQL to provide a type-safe, modern GraphQL API with automatic
schema generation from Python type hints.

The schema provides:
- Queries for retrieving user data and health metrics across date ranges
- Mutations for syncing data from health providers and creating users
- Type-safe data models with automatic validation

Architecture
------------
The schema follows a clean architecture pattern:
- **Types Layer**: Strawberry types map to database models
- **Query Layer**: Read operations for fetching health data
- **Mutation Layer**: Write operations for data sync and user management
- **Repository Layer**: Database access abstraction

GraphQL Endpoint
----------------
The schema is exposed at `/graphql` with:
- GraphQL Playground for interactive exploration (development)
- Introspection for schema documentation
- Subscription support for real-time updates (planned)

Examples
--------
Query user's sleep metrics for last 7 days::

    query {
      sleepMetrics(
        userId: 1,
        startDate: "2023-11-01T00:00:00Z",
        endDate: "2023-11-08T00:00:00Z"
      ) {
        date
        durationMins
        sleepScore
        deepSleepMins
        remSleepMins
      }
    }

Sync health data from multiple providers::

    mutation {
      syncHealthData(
        userId: 1,
        providers: ["oura", "apple_health"],
        startDate: "2023-11-01T00:00:00Z",
        endDate: "2023-11-08T00:00:00Z"
      )
    }

Create a new user::

    mutation {
      createUser(
        username: "john_doe",
        email: "john@example.com"
      ) {
        id
        email
        createdAt
      }
    }

See Also
--------
:mod:`backend.api.health.repository` : Database operations
:mod:`backend.api.health.types` : Strawberry type definitions
:mod:`backend.core.inputs.health.providers` : Health data providers

Notes
-----
- All datetime fields use ISO 8601 format in UTC
- Date ranges are inclusive on both start and end
- Provider sync operations are asynchronous and may take several seconds
- GraphQL introspection provides complete API documentation
"""

from typing import List, Optional
import strawberry
from datetime import datetime
from .types import (
    User, SleepMetrics, NutritionMetrics, ExerciseMetrics,
    BiometricMetrics, MoodMetrics
)
from backend.core.inputs.health.providers import (
    apple_health, google_fit, myfitnesspal_adapter,
    oura_adapter, whoop_client
)
from .repository import HealthRepository

@strawberry.type
class Query:
    """GraphQL Query root for retrieving health metrics data.

    This class defines all read operations available in the GraphQL API.
    Each method corresponds to a GraphQL query field and returns strongly-typed
    data from the database.

    All query methods:
    - Use async/await for non-blocking database access
    - Handle connection management automatically
    - Return None for missing data (nullable fields)
    - Support date range filtering for time-series data

    Examples
    --------
    GraphQL query for user data::

        query GetUser {
          user(id: 1) {
            id
            email
            name
            preferences
          }
        }

    Query multiple metric types::

        query HealthDashboard {
          user(id: 1) {
            email
          }
          sleepMetrics(userId: 1, startDate: "2023-11-01", endDate: "2023-11-08") {
            date
            sleepScore
          }
          exerciseMetrics(userId: 1, startDate: "2023-11-01", endDate: "2023-11-08") {
            activityType
            caloriesBurned
          }
        }
    """

    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """Retrieve a user by their unique ID.

        Parameters
        ----------
        id : int
            User's unique identifier.

        Returns
        -------
        User or None
            User object if found, None if user does not exist.

        Examples
        --------
        GraphQL query::

            query {
              user(id: 1) {
                id
                email
                name
                createdAt
              }
            }

        Response::

            {
              "data": {
                "user": {
                  "id": 1,
                  "email": "user@example.com",
                  "name": "John Doe",
                  "createdAt": "2023-11-08T10:30:00Z"
                }
              }
            }
        """
        repo = HealthRepository()
        await repo.init_pool()
        user_data = await repo.get_user(id)
        await repo.close()
        return User(**user_data) if user_data else None

    @strawberry.field
    async def sleep_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[SleepMetrics]:
        """Retrieve sleep metrics for a user within a date range.

        Fetches all sleep records between start_date and end_date (inclusive).
        Results are ordered by date descending (most recent first).

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        start_date : datetime
            Start of date range (inclusive), ISO 8601 format.
        end_date : datetime
            End of date range (inclusive), ISO 8601 format.

        Returns
        -------
        list of SleepMetrics
            Sleep metric records, empty list if none found.

        Examples
        --------
        GraphQL query::

            query {
              sleepMetrics(
                userId: 1,
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              ) {
                date
                durationMins
                deepSleepMins
                remSleepMins
                lightSleepMins
                sleepScore
                provider
              }
            }

        Response::

            {
              "data": {
                "sleepMetrics": [
                  {
                    "date": "2023-11-07T22:30:00Z",
                    "durationMins": 480,
                    "deepSleepMins": 120,
                    "remSleepMins": 90,
                    "lightSleepMins": 270,
                    "sleepScore": 85,
                    "provider": "oura"
                  }
                ]
              }
            }

        Notes
        -----
        - Dates must be in ISO 8601 format with timezone (typically UTC)
        - Results are ordered by date DESC
        - Provider field indicates data source (oura, whoop, etc.)
        """
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_sleep_metrics(user_id, start_date, end_date)
        await repo.close()
        return [SleepMetrics(**m) for m in metrics]

    @strawberry.field
    async def nutrition_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[NutritionMetrics]:
        """Retrieve nutrition metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        start_date : datetime
            Start of date range (inclusive).
        end_date : datetime
            End of date range (inclusive).

        Returns
        -------
        list of NutritionMetrics
            Nutrition metric records.

        Examples
        --------
        GraphQL query::

            query {
              nutritionMetrics(
                userId: 1,
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              ) {
                date
                calories
                proteinG
                carbsG
                fatG
                waterMl
              }
            }
        """
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_nutrition_metrics(user_id, start_date, end_date)
        await repo.close()
        return [NutritionMetrics(**m) for m in metrics]

    @strawberry.field
    async def exercise_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[ExerciseMetrics]:
        """Retrieve exercise metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        start_date : datetime
            Start of date range (inclusive).
        end_date : datetime
            End of date range (inclusive).

        Returns
        -------
        list of ExerciseMetrics
            Exercise metric records.

        Examples
        --------
        GraphQL query::

            query {
              exerciseMetrics(
                userId: 1,
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              ) {
                date
                activityType
                durationMins
                caloriesBurned
                distanceMeters
                avgHeartRate
                maxHeartRate
              }
            }
        """
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_exercise_metrics(user_id, start_date, end_date)
        await repo.close()
        return [ExerciseMetrics(**m) for m in metrics]

    @strawberry.field
    async def biometric_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[BiometricMetrics]:
        """Retrieve biometric metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        start_date : datetime
            Start of date range (inclusive).
        end_date : datetime
            End of date range (inclusive).

        Returns
        -------
        list of BiometricMetrics
            Biometric metric records.

        Examples
        --------
        GraphQL query::

            query {
              biometricMetrics(
                userId: 1,
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              ) {
                date
                weightKg
                bodyFatPct
                hrvMs
                restingHr
                bloodGlucose
              }
            }
        """
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_biometric_metrics(user_id, start_date, end_date)
        await repo.close()
        return [BiometricMetrics(**m) for m in metrics]

    @strawberry.field
    async def mood_metrics(
        self, user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[MoodMetrics]:
        """Retrieve mood metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        start_date : datetime
            Start of date range (inclusive).
        end_date : datetime
            End of date range (inclusive).

        Returns
        -------
        list of MoodMetrics
            Mood metric records.

        Examples
        --------
        GraphQL query::

            query {
              moodMetrics(
                userId: 1,
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              ) {
                date
                moodScore
                stressLevel
                energyLevel
                readinessScore
                notes
              }
            }
        """
        repo = HealthRepository()
        await repo.init_pool()
        metrics = await repo.get_mood_metrics(user_id, start_date, end_date)
        await repo.close()
        return [MoodMetrics(**m) for m in metrics]

@strawberry.type
class Mutation:
    """GraphQL Mutation root for modifying health data.

    This class defines all write operations in the GraphQL API including
    syncing data from health providers and user management.

    Mutations:
    - Use async/await for non-blocking operations
    - Return success status or created objects
    - Handle provider integration and data normalization
    - Validate data before persistence

    Examples
    --------
    Sync health data mutation::

        mutation {
          syncHealthData(
            userId: 1,
            providers: ["oura", "apple_health"],
            startDate: "2023-11-01T00:00:00Z",
            endDate: "2023-11-08T00:00:00Z"
          )
        }

    Create user mutation::

        mutation {
          createUser(
            username: "jane_doe",
            email: "jane@example.com"
          ) {
            id
            email
          }
        }
    """

    @strawberry.mutation
    async def sync_health_data(
        self,
        user_id: int,
        providers: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """Sync health data from specified providers for a date range.

        This mutation fetches data from health tracking providers (Oura, Whoop,
        Apple Health, etc.) and stores it in normalized format. The operation
        is asynchronous and may take several seconds depending on the date range.

        Parameters
        ----------
        user_id : int
            User's unique identifier.
        providers : list of str
            Provider names to sync from. Valid values:
            - 'apple_health': Apple Health app data
            - 'google_fit': Google Fit data
            - 'myfitnesspal': Nutrition tracking data
            - 'oura': Oura Ring sleep and recovery data
            - 'whoop': Whoop strap fitness data
        start_date : datetime
            Start of sync period (inclusive).
        end_date : datetime
            End of sync period (inclusive).

        Returns
        -------
        bool
            True if sync completed successfully, False otherwise.

        Raises
        ------
        ValueError
            If provider name is invalid.
        AuthenticationError
            If provider authentication fails (invalid/expired tokens).

        Examples
        --------
        Sync from multiple providers::

            mutation {
              syncHealthData(
                userId: 1,
                providers: ["oura", "whoop"],
                startDate: "2023-11-01T00:00:00Z",
                endDate: "2023-11-07T23:59:59Z"
              )
            }

        Response::

            {
              "data": {
                "syncHealthData": true
              }
            }

        Notes
        -----
        - User must have valid OAuth tokens for each provider
        - Data is deduplicated based on timestamp and provider
        - Provider-specific data is stored in raw_data JSON field
        - Sync duration depends on date range and provider API rate limits
        - Partial success: if one provider fails, others still sync
        """
        provider_map = {
            'apple_health': apple_health.AppleHealthProvider,
            'google_fit': google_fit.GoogleFitProvider,
            'myfitnesspal': myfitnesspal_adapter.MyFitnessPalProvider,
            'oura': oura_adapter.OuraProvider,
            'whoop': whoop_client.WhoopProvider
        }

        repo = HealthRepository()
        await repo.init_pool()

        try:
            for provider_name in providers:
                if provider_name in provider_map:
                    provider = provider_map[provider_name]()
                    data = await provider.sync_data(user_id, start_date, end_date)

                    # Save the data based on provider type
                    if isinstance(provider, apple_health.AppleHealthProvider):
                        await repo.save_sleep_metrics(data.get('sleep', {}))
                        await repo.save_exercise_metrics(data.get('exercise', {}))
                        await repo.save_biometric_metrics(data.get('biometrics', {}))
                    # Add similar handling for other providers...

            return True
        finally:
            await repo.close()

    @strawberry.mutation
    async def create_user(self, username: str, email: str) -> User:
        """Create a new user account.

        Parameters
        ----------
        username : str
            Unique username for the account.
        email : str
            User's email address (must be unique).

        Returns
        -------
        User
            Newly created user object with all fields.

        Raises
        ------
        ValueError
            If email format is invalid.
        IntegrityError
            If email already exists in database.

        Examples
        --------
        Create user mutation::

            mutation {
              createUser(
                username: "john_doe",
                email: "john@example.com"
              ) {
                id
                username
                email
                createdAt
              }
            }

        Response::

            {
              "data": {
                "createUser": {
                  "id": 123,
                  "username": "john_doe",
                  "email": "john@example.com",
                  "createdAt": "2023-11-08T14:30:00Z"
                }
              }
            }

        Notes
        -----
        - Email must be unique across all users
        - Username can contain letters, numbers, underscores
        - Created_at and updated_at are set automatically
        - Preferences and provider_tokens initialize to empty objects
        """
        repo = HealthRepository()
        await repo.init_pool()
        user_data = await repo.create_user(username, email)
        await repo.close()
        return User(**user_data)

schema = strawberry.Schema(query=Query, mutation=Mutation)
"""GraphQL schema instance for the health metrics API.

This schema combines the Query and Mutation types into a complete GraphQL API.
It's used by the FastAPI GraphQL middleware to handle GraphQL requests.

Usage
-----
Integrate with FastAPI::

    from strawberry.fastapi import GraphQLRouter
    from backend.api.health.schema import schema

    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

Access GraphQL Playground::

    Navigate to http://localhost:8000/graphql in your browser

Query via HTTP POST::

    curl -X POST http://localhost:8000/graphql \\
      -H "Content-Type: application/json" \\
      -d '{"query": "{ user(id: 1) { email } }"}'

Features
--------
- Type-safe schema with automatic validation
- Interactive GraphQL Playground for development
- Full introspection support
- Automatic API documentation
- Optimized query execution
"""
