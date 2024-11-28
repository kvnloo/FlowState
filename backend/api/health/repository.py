from typing import List, Optional
from datetime import datetime
import asyncpg
from backend.core.config import settings

class HealthRepository:
    def __init__(self):
        self.pool = None

    async def init_pool(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(settings.DATABASE_URL)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def get_user(self, user_id: int):
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
    ):
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
    ):
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
    ):
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
    ):
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
    ):
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

    async def create_user(self, username: str, email: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                '''
                INSERT INTO users (username, email)
                VALUES ($1, $2)
                RETURNING *
                ''',
                username, email
            )

    async def save_sleep_metrics(self, metrics: dict):
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
