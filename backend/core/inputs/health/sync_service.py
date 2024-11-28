"""Health Data Synchronization Service.

This module provides a comprehensive service for synchronizing health data from various providers
into a centralized database. It handles data retrieval, normalization, and storage for multiple
types of health metrics including sleep, exercise, nutrition, biometrics, and mood data.

The service supports multiple providers including:
- Apple Health
- Google Fit
- MyFitnessPal
- Oura
- Whoop

Example:
    >>> sync_service = HealthDataSyncService()
    >>> await sync_service.sync_all_data(user_id=1)

Attributes:
    PROVIDERS (dict): Mapping of provider names to their implementation classes
    SYNC_INTERVAL (timedelta): Default time interval between syncs
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
import pandas as pd
import asyncio
from .providers import (
    apple_health,
    google_fit,
    myfitnesspal_adapter,
    oura_adapter,
    whoop_client
)
from backend.api.health.repository import HealthRepository

class HealthDataSyncService:
    """Service for synchronizing health data from multiple providers.
    
    This service manages the synchronization of health data from various providers,
    handling authentication, data retrieval, normalization, and storage.
    
    Attributes:
        providers (dict): Initialized provider instances
        db_pool (asyncpg.Pool): Database connection pool
    """
    
    def __init__(self):
        """Initialize the sync service with configured providers."""
        self.repo = HealthRepository()
        self.providers = {
            'apple_health': apple_health.AppleHealthProvider(),
            'google_fit': google_fit.GoogleFitProvider(),
            'myfitnesspal': myfitnesspal_adapter.MyFitnessPalProvider(),
            'oura': oura_adapter.OuraProvider(),
            'whoop': whoop_client.WhoopProvider()
        }

    async def init_db(self):
        """Initialize the database connection pool."""
        await self.repo.init_pool()

    async def close_db(self):
        """Close the database connection pool."""
        await self.repo.close()

    async def sync_all_data(self, user_id: int, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, bool]:
        """Synchronize all health data from all providers for a user.
        
        Args:
            user_id: The ID of the user to sync data for
            start_date: Optional start date for the sync window
            end_date: Optional end date for the sync window
            
        Returns:
            Dict mapping provider names to sync success status
        """
        if end_date is None:
            end_date = datetime.now()

        results = {}
        for provider_name, provider in self.providers.items():
            try:
                # Sync sleep data
                sleep_data = await self._sync_sleep_data(user_id, provider, start_date, end_date)
                
                # Sync activity/exercise data
                exercise_data = await self._sync_exercise_data(user_id, provider, start_date, end_date)
                
                # Sync biometric data
                biometric_data = await self._sync_biometric_data(user_id, provider, start_date, end_date)
                
                # Sync nutrition data (if available)
                if hasattr(provider, 'get_nutrition_data'):
                    nutrition_data = await self._sync_nutrition_data(user_id, provider, start_date, end_date)
                
                # Sync mood/readiness data
                mood_data = await self._sync_mood_data(user_id, provider, start_date, end_date)
                
                results[provider_name] = True
            except Exception as e:
                print(f"Error syncing {provider_name}: {str(e)}")
                results[provider_name] = False

        return results

    async def _sync_sleep_data(self, user_id: int, provider, start_date: datetime, end_date: datetime) -> bool:
        """Sync sleep metrics from a specific provider.
        
        Args:
            user_id: The ID of the user to sync data for
            provider: The health data provider instance
            start_date: Start date for the sync window
            end_date: End date for the sync window
            
        Returns:
            bool indicating sync success
        """
        try:
            df = provider.get_sleep_data(start_date, end_date)
            if df.empty:
                return False

            for _, row in df.iterrows():
                metrics = {
                    'user_id': user_id,
                    'date': row.get('date') or row.get('timestamp'),
                    'bedtime': row.get('bedtime'),
                    'wake_time': row.get('wake_time'),
                    'total_sleep_duration': row.get('total_sleep_duration'),
                    'sleep_latency': row.get('sleep_latency'),
                    'deep_sleep_duration': row.get('deep_sleep_duration'),
                    'rem_sleep_duration': row.get('rem_sleep_duration'),
                    'light_sleep_duration': row.get('light_sleep_duration'),
                    'wake_periods': row.get('wake_periods'),
                    'sleep_efficiency': row.get('sleep_efficiency'),
                    'average_heart_rate': row.get('average_hr'),
                    'average_hrv': row.get('average_hrv'),
                    'respiratory_rate': row.get('respiratory_rate')
                }
                await self.repo.save_sleep_metrics(metrics)
            return True
        except Exception as e:
            print(f"Error syncing sleep data: {str(e)}")
            return False

    async def _sync_exercise_data(self, user_id: int, provider, start_date: datetime, end_date: datetime) -> bool:
        """Sync exercise metrics from a specific provider.
        
        Args:
            user_id: The ID of the user to sync data for
            provider: The health data provider instance
            start_date: Start date for the sync window
            end_date: End date for the sync window
            
        Returns:
            bool indicating sync success
        """
        try:
            df = provider.get_activity_data(start_date, end_date)
            if df.empty:
                return False

            for _, row in df.iterrows():
                metrics = {
                    'user_id': user_id,
                    'timestamp': row.get('timestamp'),
                    'activity_type': row.get('activity_type'),
                    'duration': row.get('duration'),
                    'distance': row.get('distance'),
                    'average_heart_rate': row.get('average_hr'),
                    'max_heart_rate': row.get('max_hr'),
                    'calories_burned': row.get('calories'),
                    'total_volume': row.get('total_volume'),
                    'perceived_exertion': row.get('perceived_exertion'),
                    'heart_rate_zones': row.get('hr_zones')
                }
                await self.repo.save_exercise_metrics(metrics)
            return True
        except Exception as e:
            print(f"Error syncing exercise data: {str(e)}")
            return False

    async def _sync_biometric_data(self, user_id: int, provider, start_date: datetime, end_date: datetime) -> bool:
        """Sync biometric metrics from a specific provider.
        
        Args:
            user_id: The ID of the user to sync data for
            provider: The health data provider instance
            start_date: Start date for the sync window
            end_date: End date for the sync window
            
        Returns:
            bool indicating sync success
        """
        try:
            # Combine HRV and readiness data for comprehensive biometrics
            hrv_df = provider.get_hrv_data(start_date, end_date)
            readiness_df = provider.get_readiness_data(start_date, end_date)
            
            # Process HRV data
            if not hrv_df.empty:
                for _, row in hrv_df.iterrows():
                    metrics = {
                        'user_id': user_id,
                        'timestamp': row.get('timestamp'),
                        'hrv_score': row.get('hrv'),
                        'resting_heart_rate': row.get('resting_hr')
                    }
                    await self.repo.save_biometric_metrics(metrics)

            # Process readiness data
            if not readiness_df.empty:
                for _, row in readiness_df.iterrows():
                    metrics = {
                        'user_id': user_id,
                        'timestamp': row.get('timestamp'),
                        'body_temperature': row.get('temperature'),
                        'respiratory_rate': row.get('respiratory_rate'),
                        'glucose_level': row.get('glucose'),
                        'ketone_level': row.get('ketones')
                    }
                    await self.repo.save_biometric_metrics(metrics)
            
            return True
        except Exception as e:
            print(f"Error syncing biometric data: {str(e)}")
            return False

    async def _sync_nutrition_data(self, user_id: int, provider, start_date: datetime, end_date: datetime) -> bool:
        """Sync nutrition metrics from a specific provider.
        
        Args:
            user_id: The ID of the user to sync data for
            provider: The health data provider instance
            start_date: Start date for the sync window
            end_date: End date for the sync window
            
        Returns:
            bool indicating sync success
        """
        try:
            if not hasattr(provider, 'get_nutrition_data'):
                return False

            df = provider.get_nutrition_data(start_date, end_date)
            if df.empty:
                return False

            for _, row in df.iterrows():
                metrics = {
                    'user_id': user_id,
                    'timestamp': row.get('timestamp'),
                    'calories': row.get('calories'),
                    'protein': row.get('protein'),
                    'carbohydrates': row.get('carbs'),
                    'fat': row.get('fat'),
                    'fiber': row.get('fiber'),
                    'water_intake': row.get('water'),
                    'meal_type': row.get('meal_type'),
                    'food_items': row.get('foods')
                }
                await self.repo.save_nutrition_metrics(metrics)
            return True
        except Exception as e:
            print(f"Error syncing nutrition data: {str(e)}")
            return False

    async def _sync_mood_data(self, user_id: int, provider, start_date: datetime, end_date: datetime) -> bool:
        """Sync mood metrics from a specific provider.
        
        Args:
            user_id: The ID of the user to sync data for
            provider: The health data provider instance
            start_date: Start date for the sync window
            end_date: End date for the sync window
            
        Returns:
            bool indicating sync success
        """
        try:
            if not hasattr(provider, 'get_readiness_data'):
                return False

            df = provider.get_readiness_data(start_date, end_date)
            if df.empty:
                return False

            for _, row in df.iterrows():
                metrics = {
                    'user_id': user_id,
                    'timestamp': row.get('timestamp'),
                    'energy_level': row.get('energy'),
                    'stress_level': row.get('stress'),
                    'mood_rating': row.get('mood'),
                    'readiness_score': row.get('readiness'),
                    'recovery_score': row.get('recovery')
                }
                await self.repo.save_mood_metrics(metrics)
            return True
        except Exception as e:
            print(f"Error syncing mood data: {str(e)}")
            return False
