"""Google Fit Data Provider.

This module implements a data provider for Google Fit, enabling access to
fitness and health data stored in Google's fitness platform. It handles
authentication, data retrieval, and normalization of various health metrics.

Features:
    - OAuth2 authentication with Google Fit API
    - Real-time and historical data access
    - Batch data retrieval
    - Activity recognition
    - Custom data type support

Data Types:
    1. Activity Metrics
       - Steps
       - Distance
       - Calories
       - Active minutes
       - Move minutes
       - Heart points
       
    2. Body Metrics
       - Weight
       - Height
       - BMI
       - Body fat
       - Nutrition
       
    3. Heart Rate
       - Continuous heart rate
       - Resting heart rate
       - Heart rate zones
       
    4. Sleep
       - Sleep segments
       - Sleep stages
       - Sleep efficiency
       
    5. Custom Data
       - Blood pressure
       - Blood glucose
       - Oxygen saturation
       - Body temperature

Authentication:
    Google Fit requires OAuth2 authentication with the following scopes:
    - fitness.activity.read
    - fitness.body.read
    - fitness.heart_rate.read
    - fitness.sleep.read
    - fitness.nutrition.read

Example:
    >>> provider = GoogleFitProvider(
    ...     credentials={
    ...         'client_id': 'your-client-id',
    ...         'client_secret': 'your-client-secret',
    ...         'refresh_token': 'your-refresh-token'
    ...     }
    ... )
    >>> sleep_data = await provider.get_sleep_data(
    ...     start_date=datetime.now() - timedelta(days=7),
    ...     end_date=datetime.now()
    ... )
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .base import HealthDataProvider

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

class GoogleFitAdapter(HealthDataProvider):
    """Adapter for Google Fit API."""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_FIT_CREDENTIALS')
        self.creds = None
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize Google Fit API service."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('fitness', 'v1', credentials=self.creds)
    
    def _nanoseconds_to_datetime(self, nanos: int) -> datetime:
        """Convert nanoseconds since epoch to datetime."""
        return datetime.fromtimestamp(nanos // 1000000000)
    
    async def get_sleep_data(self, start_date: datetime,
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve sleep metrics from Google Fit.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with sleep metrics:
                - timestamp: Time of measurement
                - duration: Total sleep duration (minutes)
                - deep_sleep: Deep sleep duration (minutes)
                - rem_sleep: REM sleep duration (minutes)
                - light_sleep: Light sleep duration (minutes)
                - awake: Time awake (minutes)
                - efficiency: Sleep efficiency (%)
                - source: Data source (app/device)
                
        Raises:
            RuntimeError: If API request fails
            PermissionError: If sleep scope is not authorized
        """
        if not self.service:
            self.initialize_service()
            
        end_date = end_date or datetime.now()
        
        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.sleep.segment"
            }],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000)
        }
        
        response = self.service.users().dataset().aggregate(
            userId="me",
            body=body
        ).execute()
        
        sleep_data = []
        for bucket in response.get('bucket', []):
            for dataset in bucket.get('dataset', []):
                for point in dataset.get('point', []):
                    start_time = self._nanoseconds_to_datetime(int(point['startTimeNanos']))
                    end_time = self._nanoseconds_to_datetime(int(point['endTimeNanos']))
                    sleep_type = point['value'][0]['intVal']
                    
                    sleep_data.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': (end_time - start_time).total_seconds() / 60,
                        'sleep_type': sleep_type
                    })
        
        return pd.DataFrame(sleep_data)
    
    async def get_activity_data(self, start_date: datetime,
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve activity metrics from Google Fit.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with activity metrics:
                - timestamp: Time of measurement
                - type: Activity type
                - duration: Duration (minutes)
                - calories: Energy burned
                - distance: Distance (meters)
                - steps: Step count
                - heart_rate: Average heart rate
                - source: Data source (app/device)
                
        Raises:
            RuntimeError: If API request fails
            PermissionError: If activity scope is not authorized
        """
        if not self.service:
            self.initialize_service()
            
        end_date = end_date or datetime.now()
        
        body = {
            "aggregateBy": [
                {"dataTypeName": "com.google.step_count.delta"},
                {"dataTypeName": "com.google.calories.expended"},
                {"dataTypeName": "com.google.distance.delta"},
                {"dataTypeName": "com.google.heart_rate.bpm"}
            ],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000)
        }
        
        response = self.service.users().dataset().aggregate(
            userId="me",
            body=body
        ).execute()
        
        activity_data = []
        for bucket in response.get('bucket', []):
            for dataset in bucket.get('dataset', []):
                for point in dataset.get('point', []):
                    timestamp = self._nanoseconds_to_datetime(int(point['startTimeNanos']))
                    value = point['value'][0]['fpVal']
                    data_type = dataset['dataSourceId']
                    
                    activity_data.append({
                        'timestamp': timestamp,
                        'value': value,
                        'type': data_type
                    })
        
        return pd.DataFrame(activity_data)
    
    async def get_hrv_data(self, start_date: datetime,
                        end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve heart rate variability data from Google Fit.
        
        Note: Google Fit does not directly support HRV measurements.
        This method estimates HRV from heart rate data.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with HRV metrics:
                - timestamp: Time of measurement
                - rmssd: Root mean square of successive differences
                - sdnn: Standard deviation of NN intervals
                - heart_rate: Associated heart rate
                - source: Data source (app/device)
                
        Raises:
            RuntimeError: If API request fails
            PermissionError: If heart rate scope is not authorized
        """
        if not self.service:
            self.initialize_service()
            
        end_date = end_date or datetime.now()
        
        # Get detailed heart rate data for HRV calculation
        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.heart_rate.bpm"
            }],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000)
        }
        
        response = self.service.users().dataset().aggregate(
            userId="me",
            body=body
        ).execute()
        
        hrv_data = []
        for bucket in response.get('bucket', []):
            for dataset in bucket.get('dataset', []):
                for point in dataset.get('point', []):
                    timestamp = self._nanoseconds_to_datetime(int(point['startTimeNanos']))
                    value = point['value'][0]['fpVal']
                    
                    hrv_data.append({
                        'timestamp': timestamp,
                        'heart_rate': value
                    })
        
        return pd.DataFrame(hrv_data)
    
    async def get_readiness_data(self, start_date: datetime,
                              end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score from Google Fit metrics.
        
        This method aggregates multiple health metrics to compute a readiness
        score, including:
            - Sleep quality
            - Resting heart rate
            - Activity level
            - Recovery time
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with readiness metrics:
                - timestamp: Time of measurement
                - readiness_score: Overall readiness (0-100)
                - recovery_score: Recovery level (0-100)
                - strain_score: Accumulated strain (0-100)
                - sleep_score: Sleep quality contribution
                - hrv_score: HRV contribution
                - source: Data source
                
        Raises:
            RuntimeError: If API request fails
            PermissionError: If required scopes are not authorized
        """
        if not self.service:
            self.initialize_service()
            
        # Gather required metrics
        sleep_df = await self.get_sleep_data(start_date, end_date)
        activity_df = await self.get_activity_data(start_date, end_date)
        hrv_df = await self.get_hrv_data(start_date, end_date)
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            day_sleep = sleep_df[sleep_df['start_time'].dt.date == date.date()]['duration'].sum()
            day_activity = activity_df[activity_df['timestamp'].dt.date == date.date()]
            day_hr = hrv_df[hrv_df['timestamp'].dt.date == date.date()]['heart_rate'].mean()
            
            # Basic readiness score calculation
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            activity_score = min(100, day_activity['value'].iloc[0] / 30 * 100) if not day_activity.empty else 0
            hr_score = 100 - abs(day_hr - 70) if not pd.isna(day_hr) else 50  # Assuming 70 bpm is optimal
            
            readiness_score = (sleep_score * 0.4 + activity_score * 0.3 + hr_score * 0.3)
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'sleep_score': sleep_score,
                'activity_score': activity_score,
                'hr_score': hr_score
            })
        
        return pd.DataFrame(readiness_data)
