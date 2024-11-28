"""Base Health Data Provider.

This module defines the base interface for health data providers. All provider
implementations must inherit from this base class and implement its methods.

The base provider ensures consistent data retrieval and normalization across
different data sources, making it easy to add new providers while maintaining
compatibility with the existing system.

Provider Implementations:
    - AppleHealthProvider: Native iOS HealthKit integration
    - OuraAdapter: Oura Ring via Shimmer normalization
    - WhoopClient: Real-time Whoop biometrics
    - GoogleFitProvider: Google Fit integration
    - MyFitnessPalAdapter: Nutrition tracking
    - TobiiTracker: Eye tracking metrics

Data Types:
    - Sleep: Duration, stages, quality metrics
    - Activity: Workouts, steps, energy expenditure
    - HRV: Heart rate variability measurements
    - Readiness: Recovery and preparedness scores
    - Nutrition: Dietary intake and macronutrients

Example:
    >>> class MyProvider(HealthDataProvider):
    ...     async def get_sleep_data(self, start_date, end_date):
    ...         # Provider-specific implementation
    ...         return normalized_sleep_data
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class HealthDataProvider(ABC):
    """Abstract base class for health data providers.
    
    This class defines the interface that all health data providers must implement.
    It ensures consistent data retrieval and normalization across different sources.
    
    Each provider should implement methods to retrieve various types of health data
    and normalize it to match the system's standardized format.
    
    Attributes:
        name (str): Provider name for identification
        supported_metrics (List[str]): List of supported metric types
    """
    
    @abstractmethod
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep-related metrics.
        
        Args:
            start_date: Start of the date range
            end_date: Optional end of date range, defaults to current time
            
        Returns:
            DataFrame with normalized sleep metrics:
                - timestamp: Time of measurement
                - duration: Total sleep duration in minutes
                - deep_sleep: Deep sleep duration in minutes
                - rem_sleep: REM sleep duration in minutes
                - light_sleep: Light sleep duration in minutes
                - awake: Time awake in minutes
                - efficiency: Sleep efficiency percentage
                - latency: Time to fall asleep in minutes
                - raw_data: Original provider data
        """
        pass
    
    @abstractmethod
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity-related metrics.
        
        Args:
            start_date: Start of the date range
            end_date: Optional end of date range, defaults to current time
            
        Returns:
            DataFrame with normalized activity metrics:
                - timestamp: Time of measurement
                - activity_type: Type of activity/exercise
                - duration: Duration in minutes
                - calories: Energy expenditure
                - distance: Distance in meters
                - steps: Step count
                - heart_rate: Average heart rate
                - intensity: Activity intensity level
                - raw_data: Original provider data
        """
        pass
    
    @abstractmethod
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch Heart Rate Variability data.
        
        Args:
            start_date: Start of the date range
            end_date: Optional end of date range, defaults to current time
            
        Returns:
            DataFrame with normalized HRV metrics:
                - timestamp: Time of measurement
                - rmssd: Root mean square of successive differences
                - sdnn: Standard deviation of NN intervals
                - lf_hf_ratio: Low-frequency to high-frequency ratio
                - heart_rate: Associated heart rate
                - raw_data: Original provider data
        """
        pass
    
    @abstractmethod
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch readiness/recovery metrics.
        
        Args:
            start_date: Start of the date range
            end_date: Optional end of date range, defaults to current time
            
        Returns:
            DataFrame with normalized readiness metrics:
                - timestamp: Time of measurement
                - readiness_score: Overall readiness (0-100)
                - recovery_score: Recovery level (0-100)
                - strain_score: Accumulated strain (0-100)
                - sleep_score: Sleep quality contribution
                - hrv_score: HRV contribution
                - raw_data: Original provider data
        """
        pass
    
    def get_nutrition_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch nutrition metrics if supported by provider.
        
        Default implementation returns empty DataFrame. Override if provider
        supports nutrition tracking.
        
        Args:
            start_date: Start of the date range
            end_date: Optional end of date range, defaults to current time
            
        Returns:
            DataFrame with normalized nutrition metrics:
                - timestamp: Time of measurement
                - calories: Total calories
                - protein: Protein in grams
                - carbs: Carbohydrates in grams
                - fat: Fat in grams
                - fiber: Fiber in grams
                - water: Water intake in ml
                - raw_data: Original provider data
        """
        return pd.DataFrame()
    
    def normalize_timestamp(self, timestamp: datetime) -> datetime:
        """Convert timestamp to UTC datetime.
        
        Args:
            timestamp: Input timestamp in any format
            
        Returns:
            Normalized UTC datetime
        """
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        return pd.Timestamp(timestamp).tz_localize(None)
    
    def normalize_duration(self, duration: float, unit: str = 'minutes') -> float:
        """Convert duration to minutes.
        
        Args:
            duration: Duration value
            unit: Input unit ('seconds', 'minutes', 'hours')
            
        Returns:
            Duration in minutes
        """
        conversions = {
            'seconds': 1/60,
            'minutes': 1,
            'hours': 60
        }
        return float(duration) * conversions.get(unit, 1)
