import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .base import HealthDataProvider, HealthMetric

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
    
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep data from Google Fit."""
        end_date = end_date or datetime.now()
        
        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.sleep.segment"
            }],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000)
        }
        
        response = self.service.users().dataset().aggregate(userId="me", body=body).execute()
        
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
                        'duration': (end_time - start_time).total_seconds() / 3600,
                        'sleep_type': sleep_type
                    })
        
        return pd.DataFrame(sleep_data)
    
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity data from Google Fit."""
        end_date = end_date or datetime.now()
        
        body = {
            "aggregateBy": [
                {"dataTypeName": "com.google.step_count.delta"},
                {"dataTypeName": "com.google.calories.expended"},
                {"dataTypeName": "com.google.active_minutes"}
            ],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000),
            "bucketByTime": {"durationMillis": 86400000}  # Daily buckets
        }
        
        response = self.service.users().dataset().aggregate(userId="me", body=body).execute()
        
        activity_data = []
        for bucket in response.get('bucket', []):
            day_data = {'date': datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000)}
            
            for dataset in bucket.get('dataset', []):
                data_type = dataset['dataSourceId']
                for point in dataset.get('point', []):
                    value = point['value'][0]['intVal' if 'intVal' in point['value'][0] else 'fpVal']
                    if 'step_count' in data_type:
                        day_data['steps'] = value
                    elif 'calories' in data_type:
                        day_data['calories'] = value
                    elif 'active_minutes' in data_type:
                        day_data['active_minutes'] = value
            
            activity_data.append(day_data)
        
        return pd.DataFrame(activity_data)
    
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch Heart Rate Variability data from Google Fit."""
        end_date = end_date or datetime.now()
        
        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.heart_rate.bpm"
            }],
            "startTimeMillis": int(start_date.timestamp() * 1000),
            "endTimeMillis": int(end_date.timestamp() * 1000),
            "bucketByTime": {"durationMillis": 60000}  # 1-minute buckets
        }
        
        response = self.service.users().dataset().aggregate(userId="me", body=body).execute()
        
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
    
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score based on various metrics."""
        # Google Fit doesn't provide readiness scores directly
        # We'll calculate it based on sleep, activity, and heart rate data
        sleep_df = self.get_sleep_data(start_date, end_date)
        activity_df = self.get_activity_data(start_date, end_date)
        hrv_df = self.get_hrv_data(start_date, end_date)
        
        # Simplified readiness calculation
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            day_sleep = sleep_df[sleep_df['start_time'].dt.date == date.date()]['duration'].sum()
            day_activity = activity_df[activity_df['date'].dt.date == date.date()]
            day_hr = hrv_df[hrv_df['timestamp'].dt.date == date.date()]['heart_rate'].mean()
            
            # Basic readiness score calculation
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            activity_score = min(100, day_activity['active_minutes'].iloc[0] / 30 * 100) if not day_activity.empty else 0
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
