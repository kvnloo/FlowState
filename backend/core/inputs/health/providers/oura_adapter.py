from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import pandas as pd
from .base import HealthDataProvider
from .shimmer_client import ShimmerClient, ShimmerEndpoint, ShimmerCredentials, ShimmerDataType

class OuraAdapter(HealthDataProvider):
    """Adapter for Oura Ring data using Shimmer for normalization."""
    
    def __init__(self, shimmer_base_url: str, client_id: str, client_secret: str):
        """Initialize Oura adapter with Shimmer client."""
        self.client = ShimmerClient(
            base_url=shimmer_base_url,
            credentials={
                ShimmerEndpoint.OURA: ShimmerCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
            }
        )
    
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep data from Oura through Shimmer."""
        sleep_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.SLEEP_EPISODE,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get additional sleep duration data
        duration_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.SLEEP_DURATION,
            start_date=start_date,
            end_date=end_date
        )
        
        # Merge sleep episode and duration data
        if not sleep_df.empty and not duration_df.empty:
            sleep_df = sleep_df.merge(
                duration_df[['timestamp', 'duration']],
                on='timestamp',
                how='outer'
            )
        
        return sleep_df
    
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity data from Oura through Shimmer."""
        # Get both activity and calories data
        activity_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.PHYSICAL_ACTIVITY,
            start_date=start_date,
            end_date=end_date
        )
        
        calories_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.CALORIES_BURNED,
            start_date=start_date,
            end_date=end_date
        )
        
        # Merge activity and calories data
        if not activity_df.empty and not calories_df.empty:
            activity_df = activity_df.merge(
                calories_df[['timestamp', 'calories']],
                on='timestamp',
                how='outer'
            )
        
        return activity_df
    
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch HRV data from Oura through Shimmer."""
        return self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.HRV,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score using Oura data."""
        # Get all required metrics
        sleep_df = self.get_sleep_data(start_date, end_date)
        activity_df = self.get_activity_data(start_date, end_date)
        hrv_df = self.get_hrv_data(start_date, end_date)
        
        # Get heart rate data
        hr_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.HEART_RATE,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get body temperature data (Oura-specific)
        temp_df = self.client.get_data(
            endpoint=ShimmerEndpoint.OURA,
            data_type=ShimmerDataType.BODY_TEMPERATURE,
            start_date=start_date,
            end_date=end_date
        )
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            next_date = date + timedelta(days=1)
            
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
            
            day_temp = temp_df[
                (temp_df['timestamp'] >= date) & 
                (temp_df['timestamp'] < next_date)
            ]['temperature'].mean() if 'temperature' in temp_df.columns else None
            
            # Calculate component scores
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            
            activity_score = min(100, day_activity['calories'].sum() / 600 * 100) \
                if not day_activity.empty and 'calories' in day_activity.columns else 0
            
            hrv_score = min(100, (day_hrv / 100) * 100) if day_hrv is not None else 50
            hr_score = 100 - abs(day_hr - 70) if day_hr is not None else 50
            
            # Temperature deviation score (Oura-specific)
            temp_score = 100 - abs(day_temp - 37) * 20 if day_temp is not None else 50  # Optimal temp = 37°C
            
            # Calculate weighted readiness score with temperature
            readiness_score = (
                sleep_score * 0.35 +
                activity_score * 0.25 +
                hrv_score * 0.2 +
                hr_score * 0.1 +
                temp_score * 0.1
            )
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'sleep_score': sleep_score,
                'activity_score': activity_score,
                'hrv_score': hrv_score,
                'hr_score': hr_score,
                'temperature_score': temp_score,
                'sleep_duration': day_sleep,
                'calories': day_activity['calories'].sum() if not day_activity.empty and 'calories' in day_activity.columns else 0,
                'hrv': day_hrv,
                'heart_rate': day_hr,
                'temperature': day_temp
            })
        
        return pd.DataFrame(readiness_data)
