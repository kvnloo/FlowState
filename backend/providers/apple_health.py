import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import healthkit
from .base import HealthDataProvider, HealthMetric

class AppleHealthAdapter(HealthDataProvider):
    """Adapter for Apple HealthKit API."""
    
    def __init__(self):
        self.health_store = healthkit.HealthStore()
        self._request_authorization()
    
    def _request_authorization(self):
        """Request authorization to access HealthKit data."""
        read_types = [
            healthkit.QuantityType.SLEEP_ANALYSIS,
            healthkit.QuantityType.HEART_RATE,
            healthkit.QuantityType.HEART_RATE_VARIABILITY_SDNN,
            healthkit.QuantityType.STEP_COUNT,
            healthkit.QuantityType.ACTIVE_ENERGY_BURNED,
            healthkit.QuantityType.RESTING_HEART_RATE,
            healthkit.QuantityType.RESPIRATORY_RATE,
            healthkit.QuantityType.OXYGEN_SATURATION,
            healthkit.QuantityType.BODY_TEMPERATURE
        ]
        
        self.health_store.request_authorization(read_types, [])
    
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep data from Apple Health."""
        end_date = end_date or datetime.now()
        
        sleep_samples = self.health_store.query(
            healthkit.QuantityType.SLEEP_ANALYSIS,
            start_date,
            end_date
        )
        
        sleep_data = []
        for sample in sleep_samples:
            sleep_data.append({
                'start_time': sample.start_date,
                'end_time': sample.end_date,
                'duration': (sample.end_date - sample.start_date).total_seconds() / 3600,
                'sleep_type': sample.value  # Asleep, InBed, Awake
            })
        
        return pd.DataFrame(sleep_data)
    
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity data from Apple Health."""
        end_date = end_date or datetime.now()
        
        # Get steps data
        steps_samples = self.health_store.query(
            healthkit.QuantityType.STEP_COUNT,
            start_date,
            end_date
        )
        
        # Get active energy data
        energy_samples = self.health_store.query(
            healthkit.QuantityType.ACTIVE_ENERGY_BURNED,
            start_date,
            end_date
        )
        
        # Process data day by day
        activity_data = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Calculate daily steps
            daily_steps = sum(
                sample.value for sample in steps_samples
                if current_date <= sample.start_date < next_date
            )
            
            # Calculate daily active energy
            daily_energy = sum(
                sample.value for sample in energy_samples
                if current_date <= sample.start_date < next_date
            )
            
            activity_data.append({
                'date': current_date,
                'steps': daily_steps,
                'active_energy': daily_energy,
                'active_minutes': daily_energy / 7  # Rough estimate: 7 calories per active minute
            })
            
            current_date = next_date
        
        return pd.DataFrame(activity_data)
    
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch Heart Rate Variability data from Apple Health."""
        end_date = end_date or datetime.now()
        
        # Get HRV samples
        hrv_samples = self.health_store.query(
            healthkit.QuantityType.HEART_RATE_VARIABILITY_SDNN,
            start_date,
            end_date
        )
        
        # Get heart rate samples
        hr_samples = self.health_store.query(
            healthkit.QuantityType.HEART_RATE,
            start_date,
            end_date
        )
        
        hrv_data = []
        for sample in hrv_samples:
            # Find closest heart rate measurement
            closest_hr = min(
                hr_samples,
                key=lambda x: abs(x.start_date - sample.start_date),
                default=None
            )
            
            hrv_data.append({
                'timestamp': sample.start_date,
                'hrv': sample.value,
                'heart_rate': closest_hr.value if closest_hr else None
            })
        
        return pd.DataFrame(hrv_data)
    
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score based on various metrics."""
        end_date = end_date or datetime.now()
        
        # Get additional health metrics
        resting_hr_samples = self.health_store.query(
            healthkit.QuantityType.RESTING_HEART_RATE,
            start_date,
            end_date
        )
        
        respiratory_samples = self.health_store.query(
            healthkit.QuantityType.RESPIRATORY_RATE,
            start_date,
            end_date
        )
        
        oxygen_samples = self.health_store.query(
            healthkit.QuantityType.OXYGEN_SATURATION,
            start_date,
            end_date
        )
        
        # Get base metrics
        sleep_df = self.get_sleep_data(start_date, end_date)
        activity_df = self.get_activity_data(start_date, end_date)
        hrv_df = self.get_hrv_data(start_date, end_date)
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date, freq='D'):
            next_date = date + timedelta(days=1)
            
            # Calculate daily averages
            day_sleep = sleep_df[
                (sleep_df['start_time'] >= date) & 
                (sleep_df['start_time'] < next_date)
            ]['duration'].sum()
            
            day_activity = activity_df[activity_df['date'].date() == date.date()]
            day_hrv = hrv_df[
                (hrv_df['timestamp'] >= date) & 
                (hrv_df['timestamp'] < next_date)
            ]['hrv'].mean()
            
            # Get daily health metrics
            resting_hr = next(
                (s.value for s in resting_hr_samples if date <= s.start_date < next_date),
                None
            )
            respiratory_rate = next(
                (s.value for s in respiratory_samples if date <= s.start_date < next_date),
                None
            )
            oxygen_level = next(
                (s.value for s in oxygen_samples if date <= s.start_date < next_date),
                None
            )
            
            # Calculate component scores
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            activity_score = min(100, day_activity['active_minutes'].iloc[0] / 30 * 100) if not day_activity.empty else 0
            hrv_score = min(100, (day_hrv / 100) * 100) if not pd.isna(day_hrv) else 50
            
            # Additional health scores
            resting_hr_score = 100 - abs(resting_hr - 60) if resting_hr else 50  # Optimal RHR = 60
            respiratory_score = 100 - abs(respiratory_rate - 15) * 5 if respiratory_rate else 50  # Optimal = 15
            oxygen_score = (oxygen_level - 90) * 10 if oxygen_level else 50  # Scale 90-100 to 0-100
            
            # Weighted readiness score
            readiness_score = (
                sleep_score * 0.3 +
                activity_score * 0.2 +
                hrv_score * 0.2 +
                resting_hr_score * 0.1 +
                respiratory_score * 0.1 +
                oxygen_score * 0.1
            )
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'sleep_score': sleep_score,
                'activity_score': activity_score,
                'hrv_score': hrv_score,
                'resting_hr_score': resting_hr_score,
                'respiratory_score': respiratory_score,
                'oxygen_score': oxygen_score,
                'resting_hr': resting_hr,
                'respiratory_rate': respiratory_rate,
                'oxygen_level': oxygen_level
            })
        
        return pd.DataFrame(readiness_data)
