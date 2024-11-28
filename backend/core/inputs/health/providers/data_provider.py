from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from .base import HealthDataProvider
from .shimmer_client import ShimmerClient, ShimmerEndpoint, ShimmerDataType, HealthDataFetcher

class ShimmerHealthProvider(HealthDataProvider):
    """Health data provider using Open mHealth Shimmer for data normalization."""
    
    def __init__(self, shimmer_base_url: str, credentials: Dict[ShimmerEndpoint, str]):
        self.fetcher = HealthDataFetcher(
            ShimmerClient(shimmer_base_url, credentials)
        )
        self.endpoints = list(credentials.keys())
    
    async def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve sleep metrics from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized sleep metrics:
                - timestamp: Time of measurement
                - duration: Total sleep duration (minutes)
                - deep_sleep: Deep sleep duration (minutes)
                - rem_sleep: REM sleep duration (minutes)
                - light_sleep: Light sleep duration (minutes)
                - awake: Time awake (minutes)
                - efficiency: Sleep efficiency (%)
                - source: Data source
        """
        return self.fetcher.get_sleep_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve activity metrics from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized activity metrics:
                - timestamp: Time of measurement
                - type: Activity type
                - duration: Duration (minutes)
                - calories: Energy burned
                - distance: Distance (meters)
                - steps: Step count
                - heart_rate: Average heart rate
                - source: Data source
        """
        # Get both physical activity and step count data
        activity_df = self.fetcher.get_activity_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
        
        steps_df = self.fetcher.client.get_data(
            endpoint=self.endpoints[0],  # Use primary source for steps
            data_type=ShimmerDataType.STEP_COUNT,
            start_date=start_date,
            end_date=end_date
        )
        
        # Merge activity and steps data
        if not activity_df.empty and not steps_df.empty:
            activity_df = activity_df.merge(
                steps_df[['timestamp', 'steps']],
                on='timestamp',
                how='outer'
            )
        
        return activity_df
    
    async def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve heart rate variability data from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized HRV metrics:
                - timestamp: Time of measurement
                - rmssd: Root mean square of successive differences
                - sdnn: Standard deviation of NN intervals
                - lf_hf_ratio: Low-frequency to high-frequency ratio
                - heart_rate: Associated heart rate
                - source: Data source
        """
        return self.fetcher.get_hrv_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness metrics from available data.
        
        This method should aggregate multiple health metrics to compute
        readiness and recovery scores, potentially including:
            - Sleep quality
            - HRV trends
            - Resting heart rate
            - Activity levels
            - Recovery time
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized readiness metrics:
                - timestamp: Time of measurement
                - readiness_score: Overall readiness (0-100)
                - recovery_score: Recovery level (0-100)
                - strain_score: Accumulated strain (0-100)
                - sleep_score: Sleep quality contribution
                - hrv_score: HRV contribution
                - source: Data source
        """
        # Fetch all required metrics
        sleep_df = await self.get_sleep_data(start_date, end_date)
        activity_df = await self.get_activity_data(start_date, end_date)
        hrv_df = await self.get_hrv_data(start_date, end_date)
        
        # Get heart rate data
        hr_df = self.fetcher.client.get_data(
            endpoint=self.endpoints[0],  # Use primary source for heart rate
            data_type=ShimmerDataType.HEART_RATE,
            start_date=start_date,
            end_date=end_date
        )
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            next_date = date + pd.Timedelta(days=1)
            
            # Calculate daily metrics
            day_sleep = sleep_df[
                (sleep_df['timestamp'] >= date) & 
                (sleep_df['timestamp'] < next_date)
            ]['duration'].sum() if 'duration' in sleep_df.columns else 0
            
            day_activity = activity_df[
                (activity_df['timestamp'] >= date) & 
                (activity_df['timestamp'] < next_date)
            ]
            
            day_hrv = hrv_df[
                (hrv_df['timestamp'] >= date) & 
                (hrv_df['timestamp'] < next_date)
            ]['hrv'].mean() if 'hrv' in hrv_df.columns else None
            
            day_hr = hr_df[
                (hr_df['timestamp'] >= date) & 
                (hr_df['timestamp'] < next_date)
            ]['heart_rate'].mean() if 'heart_rate' in hr_df.columns else None
            
            # Calculate component scores
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            
            activity_score = min(100, day_activity['steps'].sum() / 10000 * 100) \
                if not day_activity.empty and 'steps' in day_activity.columns else 0
            
            hrv_score = min(100, (day_hrv / 100) * 100) if day_hrv is not None else 50
            hr_score = 100 - abs(day_hr - 70) if day_hr is not None else 50
            
            # Calculate weighted readiness score
            readiness_score = (
                sleep_score * 0.4 +
                activity_score * 0.3 +
                hrv_score * 0.2 +
                hr_score * 0.1
            )
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'sleep_score': sleep_score,
                'activity_score': activity_score,
                'hrv_score': hrv_score,
                'hr_score': hr_score,
                'sleep_duration': day_sleep,
                'steps': day_activity['steps'].sum() if not day_activity.empty and 'steps' in day_activity.columns else 0,
                'hrv': day_hrv,
                'heart_rate': day_hr
            })
        
        return pd.DataFrame(readiness_data)
    
    async def get_nutrition_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve nutrition data from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized nutrition metrics:
                - timestamp: Time of measurement
                - calories: Total calories
                - protein: Protein (g)
                - carbs: Carbohydrates (g)
                - fat: Fat (g)
                - fiber: Fiber (g)
                - water: Water intake (ml)
                - source: Data source
        """
        # TO DO: Implement nutrition data retrieval
        pass
    
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
