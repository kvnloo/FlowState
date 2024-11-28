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
    
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch normalized sleep data from all configured sources."""
        return self.fetcher.get_sleep_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch normalized activity data from all configured sources."""
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
    
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch normalized HRV data from all configured sources."""
        return self.fetcher.get_hrv_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score using normalized data from all sources."""
        # Fetch all required metrics
        sleep_df = self.get_sleep_data(start_date, end_date)
        activity_df = self.get_activity_data(start_date, end_date)
        hrv_df = self.get_hrv_data(start_date, end_date)
        
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
