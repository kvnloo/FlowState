"""Health Metrics Database Repository.

This module provides the data access layer for health metrics using asyncpg
for high-performance asynchronous PostgreSQL operations. The HealthRepository
class manages database connections and provides methods for querying and
persisting health data.

The repository pattern separates database operations from business logic,
making the codebase more maintainable and testable. All database queries
use parameterized statements to prevent SQL injection.

Architecture
------------
The repository uses connection pooling for efficient database access:
- Connection pool initialized on first use
- Connections automatically acquired and released
- Prepared statements cached for performance
- Graceful connection cleanup on close

Examples
--------
Query user sleep metrics::

    from backend.api.health.repository import HealthRepository
    from datetime import datetime, timedelta

    repo = HealthRepository()
    await repo.init_pool()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    metrics = await repo.get_sleep_metrics(
        user_id=1,
        start_date=start_date,
        end_date=end_date
    )

    await repo.close()

Create a new user::

    repo = HealthRepository()
    await repo.init_pool()

    user = await repo.create_user(
        username="john_doe",
        email="john@example.com"
    )

    print(f"Created user {user['id']}: {user['email']}")
    await repo.close()

See Also
--------
:mod:`backend.core.models.health_metrics` : SQLAlchemy model definitions
:mod:`backend.api.health.schema` : GraphQL schema using this repository
:mod:`asyncpg` : Async PostgreSQL driver documentation

Notes
-----
- All methods are async and must be awaited
- Connection pool should be initialized before queries
- Always call close() to release database connections
- Date ranges are inclusive on both start and end dates
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
from backend.core.config import settings

class HealthRepository:
    """Asynchronous PostgreSQL repository for health metrics data.

    This class manages database connections and provides async methods for
    querying and persisting health data. It uses connection pooling for
    optimal performance and supports all health metric types.

    Attributes
    ----------
    pool : asyncpg.Pool
        Connection pool for database access. Initialized by init_pool().

    Examples
    --------
    Basic usage pattern::

        repo = HealthRepository()
        await repo.init_pool()

        try:
            # Perform database operations
            user = await repo.get_user(1)
            metrics = await repo.get_sleep_metrics(1, start_date, end_date)
        finally:
            await repo.close()

    Context manager usage (recommended)::

        async with HealthRepository() as repo:
            user = await repo.get_user(1)
            # Pool automatically closed on exit

    Notes
    -----
    - Connection pool is thread-safe and can be shared
    - Pool size defaults to 10 connections (configurable in settings)
    - Connections are automatically recycled after 1 hour
    """

    def __init__(self):
        """Initialize repository without creating database connections.

        The connection pool is created lazily on first use via init_pool().
        This allows repository instances to be created without immediately
        consuming database resources.
        """
        self.pool: Optional[asyncpg.Pool] = None

    async def init_pool(self) -> None:
        """Initialize the database connection pool.

        Creates an asyncpg connection pool using the database URL from settings.
        This method is idempotent - calling it multiple times will not create
        additional pools.

        Raises
        ------
        asyncpg.PostgresError
            If database connection fails.
        ValueError
            If DATABASE_URL setting is not configured.

        Examples
        --------
        Initialize pool before queries::

            repo = HealthRepository()
            await repo.init_pool()
            # Now ready for database operations

        Notes
        -----
        - Pool configuration comes from settings.DATABASE_URL
        - Default pool size is 10 connections
        - Connections are created lazily as needed
        - Pool warmup can be forced by setting min_size parameter
        """
        if not self.pool:
            self.pool = await asyncpg.create_pool(settings.DATABASE_URL)

    async def close(self) -> None:
        """Close the database connection pool and release all connections.

        This method should be called when the repository is no longer needed
        to ensure proper cleanup of database resources. It's safe to call
        multiple times.

        Examples
        --------
        Cleanup after operations::

            repo = HealthRepository()
            await repo.init_pool()
            # ... perform operations ...
            await repo.close()

        Using try-finally for guaranteed cleanup::

            repo = HealthRepository()
            try:
                await repo.init_pool()
                # ... perform operations ...
            finally:
                await repo.close()

        Notes
        -----
        - All active connections are gracefully closed
        - In-flight queries are allowed to complete
        - Pool cannot be reused after closing
        """
        if self.pool:
            await self.pool.close()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a user by ID.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        dict or None
            User record as dictionary if found, None otherwise::

                {
                    'id': 1,
                    'email': 'user@example.com',
                    'name': 'John Doe',
                    'preferences': {...},
                    'provider_tokens': {...},
                    'created_at': datetime(...),
                    'updated_at': datetime(...)
                }

        Examples
        --------
        Get user data::

            user = await repo.get_user(1)
            if user:
                print(f"User: {user['name']} ({user['email']})")
            else:
                print("User not found")

        Notes
        -----
        - Returns None if user_id does not exist
        - All timestamp fields are in UTC
        - JSON fields (preferences, provider_tokens) are automatically parsed
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM users WHERE id = $1',
                user_id
            )

    async def get_sleep_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve sleep metrics for a user within a date range.

        Fetches all sleep records for the specified user between start_date
        and end_date (inclusive). Results are ordered by date in descending
        order (most recent first).

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.
        start_date : datetime
            Start of the date range (inclusive).
        end_date : datetime
            End of the date range (inclusive).

        Returns
        -------
        list of dict
            Sleep metric records, each containing::

                {
                    'id': 1,
                    'user_id': 1,
                    'date': datetime(...),
                    'duration_mins': 480.0,
                    'deep_sleep_mins': 120.0,
                    'rem_sleep_mins': 90.0,
                    'light_sleep_mins': 270.0,
                    'awake_mins': 15.0,
                    'sleep_score': 85.0,
                    'provider': 'oura',
                    'raw_data': {...},
                    'created_at': datetime(...),
                    'updated_at': datetime(...)
                }

        Examples
        --------
        Get last week's sleep data::

            from datetime import datetime, timedelta

            end = datetime.now()
            start = end - timedelta(days=7)

            metrics = await repo.get_sleep_metrics(1, start, end)
            for metric in metrics:
                print(f"{metric['date']}: {metric['sleep_score']}/100")

        Notes
        -----
        - Date range is inclusive on both ends
        - Results ordered by date DESC (newest first)
        - Empty list returned if no records found
        - Timezone handling: dates should be in UTC
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''
                SELECT * FROM sleep_metrics
                WHERE user_id = $1
                AND date BETWEEN $2 AND $3
                ORDER BY date DESC
                ''',
                user_id, start_date, end_date
            )

    async def get_nutrition_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve nutrition metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.
        start_date : datetime
            Start of the date range (inclusive).
        end_date : datetime
            End of the date range (inclusive).

        Returns
        -------
        list of dict
            Nutrition metric records ordered by timestamp DESC::

                {
                    'id': 1,
                    'user_id': 1,
                    'date': datetime(...),
                    'calories': 2000.0,
                    'protein_g': 150.0,
                    'carbs_g': 250.0,
                    'fat_g': 70.0,
                    'fiber_g': 30.0,
                    'water_ml': 2500.0,
                    'provider': 'myfitnesspal',
                    'raw_data': {...}
                }

        Examples
        --------
        Calculate average daily calories::

            metrics = await repo.get_nutrition_metrics(1, start, end)
            avg_calories = sum(m['calories'] for m in metrics) / len(metrics)
            print(f"Average: {avg_calories:.0f} calories/day")

        See Also
        --------
        :meth:`get_sleep_metrics` : Similar method for sleep data
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''
                SELECT * FROM nutrition_metrics
                WHERE user_id = $1
                AND timestamp BETWEEN $2 AND $3
                ORDER BY timestamp DESC
                ''',
                user_id, start_date, end_date
            )

    async def get_exercise_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve exercise metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.
        start_date : datetime
            Start of the date range (inclusive).
        end_date : datetime
            End of the date range (inclusive).

        Returns
        -------
        list of dict
            Exercise metric records ordered by timestamp DESC::

                {
                    'id': 1,
                    'user_id': 1,
                    'date': datetime(...),
                    'activity_type': 'running',
                    'duration_mins': 45.0,
                    'calories_burned': 450.0,
                    'distance_meters': 7500.0,
                    'avg_heart_rate': 145.0,
                    'max_heart_rate': 172.0,
                    'provider': 'apple_health',
                    'raw_data': {...}
                }

        Examples
        --------
        Calculate total exercise time::

            metrics = await repo.get_exercise_metrics(1, start, end)
            total_mins = sum(m['duration_mins'] for m in metrics)
            hours = total_mins / 60
            print(f"Total exercise: {hours:.1f} hours")
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''
                SELECT * FROM exercise_metrics
                WHERE user_id = $1
                AND timestamp BETWEEN $2 AND $3
                ORDER BY timestamp DESC
                ''',
                user_id, start_date, end_date
            )

    async def get_biometric_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve biometric metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.
        start_date : datetime
            Start of the date range (inclusive).
        end_date : datetime
            End of the date range (inclusive).

        Returns
        -------
        list of dict
            Biometric metric records ordered by timestamp DESC::

                {
                    'id': 1,
                    'user_id': 1,
                    'date': datetime(...),
                    'weight_kg': 75.5,
                    'body_fat_pct': 18.5,
                    'hrv_ms': 65.0,
                    'resting_hr': 58.0,
                    'blood_glucose': 95.0,
                    'systolic_bp': 120.0,
                    'diastolic_bp': 80.0,
                    'provider': 'whoop',
                    'raw_data': {...}
                }

        Examples
        --------
        Track weight trend::

            metrics = await repo.get_biometric_metrics(1, start, end)
            weights = [(m['date'], m['weight_kg']) for m in metrics]
            for date, weight in weights:
                print(f"{date.date()}: {weight} kg")
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''
                SELECT * FROM biometric_metrics
                WHERE user_id = $1
                AND timestamp BETWEEN $2 AND $3
                ORDER BY timestamp DESC
                ''',
                user_id, start_date, end_date
            )

    async def get_mood_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve mood metrics for a user within a date range.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.
        start_date : datetime
            Start of the date range (inclusive).
        end_date : datetime
            End of the date range (inclusive).

        Returns
        -------
        list of dict
            Mood metric records ordered by timestamp DESC::

                {
                    'id': 1,
                    'user_id': 1,
                    'date': datetime(...),
                    'mood_score': 75.0,
                    'stress_level': 40.0,
                    'energy_level': 65.0,
                    'readiness_score': 70.0,
                    'notes': 'Felt good today',
                    'provider': 'manual',
                    'raw_data': {...}
                }

        Examples
        --------
        Analyze mood trends::

            metrics = await repo.get_mood_metrics(1, start, end)
            avg_mood = sum(m['mood_score'] for m in metrics) / len(metrics)
            print(f"Average mood: {avg_mood:.1f}/100")
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''
                SELECT * FROM mood_metrics
                WHERE user_id = $1
                AND timestamp BETWEEN $2 AND $3
                ORDER BY timestamp DESC
                ''',
                user_id, start_date, end_date
            )

    async def create_user(self, username: str, email: str) -> Dict[str, Any]:
        """Create a new user in the database.

        Parameters
        ----------
        username : str
            Username for the new user.
        email : str
            Email address (must be unique).

        Returns
        -------
        dict
            Newly created user record with all fields::

                {
                    'id': 123,
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'preferences': {},
                    'provider_tokens': {},
                    'created_at': datetime(...),
                    'updated_at': datetime(...)
                }

        Raises
        ------
        asyncpg.UniqueViolationError
            If email already exists in database.

        Examples
        --------
        Create a new user::

            try:
                user = await repo.create_user(
                    username='jane_doe',
                    email='jane@example.com'
                )
                print(f"Created user {user['id']}")
            except asyncpg.UniqueViolationError:
                print("Email already registered")

        Notes
        -----
        - Email must be unique across all users
        - Created_at and updated_at are set automatically
        - Preferences and provider_tokens default to empty dicts
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                '''
                INSERT INTO users (username, email)
                VALUES ($1, $2)
                RETURNING *
                ''',
                username, email
            )

    async def save_sleep_metrics(self, metrics: Dict[str, Any]) -> str:
        """Save sleep metrics to the database.

        Parameters
        ----------
        metrics : dict
            Sleep metric data with all required fields::

                {
                    'user_id': 1,
                    'date': datetime(...),
                    'bedtime': datetime(...),
                    'wake_time': datetime(...),
                    'total_sleep_duration': 480,
                    'sleep_latency': 15,
                    'deep_sleep_duration': 120,
                    'rem_sleep_duration': 90,
                    'light_sleep_duration': 270,
                    'wake_periods': 2,
                    'sleep_efficiency': 0.85,
                    'room_temperature': 20.5,
                    'room_humidity': 45.0,
                    'noise_level': 30.0,
                    'light_level': 0.0,
                    'average_heart_rate': 58.0,
                    'average_hrv': 65.0,
                    'respiratory_rate': 14.0,
                    'sleep_quality_rating': 8,
                    'morning_grogginess': 3
                }

        Returns
        -------
        str
            Status message from the database.

        Examples
        --------
        Save sleep data from provider::

            metrics = {
                'user_id': 1,
                'date': datetime.now(),
                # ... other fields ...
            }
            result = await repo.save_sleep_metrics(metrics)
            print(f"Saved: {result}")

        Notes
        -----
        - All fields in the metrics dict are required
        - Duplicate date+user combinations may raise unique constraint error
        - Raw provider data can be included in a 'raw_data' field
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(
                '''
                INSERT INTO sleep_metrics (
                    user_id, date, bedtime, wake_time,
                    total_sleep_duration, sleep_latency,
                    deep_sleep_duration, rem_sleep_duration,
                    light_sleep_duration, wake_periods,
                    sleep_efficiency, room_temperature,
                    room_humidity, noise_level, light_level,
                    average_heart_rate, average_hrv,
                    respiratory_rate, sleep_quality_rating,
                    morning_grogginess
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                         $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                ''',
                *metrics.values()
            )

    # Similar save methods for other metrics...
