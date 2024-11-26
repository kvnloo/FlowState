from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import pandas as pd
from .base import HealthDataProvider
from .shimmer_client import ShimmerClient, ShimmerEndpoint, ShimmerCredentials, ShimmerDataType

class MyFitnessPalAdapter(HealthDataProvider):
    """Adapter for MyFitnessPal data using Shimmer for normalization."""
    
    def __init__(self, shimmer_base_url: str, client_id: str, client_secret: str):
        """Initialize MyFitnessPal adapter with Shimmer client."""
        self.client = ShimmerClient(
            base_url=shimmer_base_url,
            credentials={
                ShimmerEndpoint.MYFITNESSPAL: ShimmerCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
            }
        )
    
    def get_nutrition_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch nutrition data from MyFitnessPal through Shimmer."""
        # Get calories data
        calories_df = self.client.get_data(
            endpoint=ShimmerEndpoint.MYFITNESSPAL,
            data_type=ShimmerDataType.CALORIES_BURNED,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get body weight data for tracking
        weight_df = self.client.get_data(
            endpoint=ShimmerEndpoint.MYFITNESSPAL,
            data_type=ShimmerDataType.BODY_WEIGHT,
            start_date=start_date,
            end_date=end_date
        )
        
        # Merge nutrition and weight data
        nutrition_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            next_date = date + timedelta(days=1)
            
            # Get daily calories
            day_calories = calories_df[
                (calories_df['timestamp'] >= date) & 
                (calories_df['timestamp'] < next_date)
            ]['calories'].sum() if not calories_df.empty and 'calories' in calories_df.columns else 0
            
            # Get daily weight if available
            day_weight = weight_df[
                (weight_df['timestamp'] >= date) & 
                (weight_df['timestamp'] < next_date)
            ]['weight'].mean() if not weight_df.empty and 'weight' in weight_df.columns else None
            
            nutrition_data.append({
                'date': date,
                'calories_consumed': day_calories,
                'weight': day_weight
            })
        
        return pd.DataFrame(nutrition_data)
    
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity data from MyFitnessPal through Shimmer."""
        return self.client.get_data(
            endpoint=ShimmerEndpoint.MYFITNESSPAL,
            data_type=ShimmerDataType.PHYSICAL_ACTIVITY,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate readiness score using MyFitnessPal data."""
        # Get nutrition and activity data
        nutrition_df = self.get_nutrition_data(start_date, end_date)
        activity_df = self.get_activity_data(start_date, end_date)
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            next_date = date + timedelta(days=1)
            
            # Get daily nutrition metrics
            day_nutrition = nutrition_df[nutrition_df['date'] == date].iloc[0] \
                if not nutrition_df.empty and len(nutrition_df[nutrition_df['date'] == date]) > 0 else None
            
            # Get daily activity
            day_activity = activity_df[
                (activity_df['timestamp'] >= date) & 
                (activity_df['timestamp'] < next_date)
            ]
            
            # Calculate nutrition score (based on meeting calorie goals)
            target_calories = 2000  # This could be personalized based on user profile
            if day_nutrition is not None and 'calories_consumed' in day_nutrition:
                calories_consumed = day_nutrition['calories_consumed']
                # Score based on how close to target calories (within ±20% is good)
                calories_score = max(0, 100 - abs(calories_consumed - target_calories) / target_calories * 100)
            else:
                calories_score = 50  # Default score if no data
            
            # Calculate activity score
            activity_score = min(100, day_activity['duration'].sum() / 60 * 100) \
                if not day_activity.empty and 'duration' in day_activity.columns else 0
            
            # Calculate weight trend score if available
            weight_score = 50  # Default score
            if day_nutrition is not None and 'weight' in day_nutrition and day_nutrition['weight'] is not None:
                # Look back 7 days to calculate weight trend
                week_ago = date - timedelta(days=7)
                week_weight = nutrition_df[
                    (nutrition_df['date'] >= week_ago) & 
                    (nutrition_df['date'] < date)
                ]['weight'].mean()
                
                if week_weight is not None:
                    # Score based on weight stability (within ±0.5kg is good)
                    weight_change = abs(day_nutrition['weight'] - week_weight)
                    weight_score = max(0, 100 - weight_change * 20)  # 20 points per kg change
            
            # Calculate weighted readiness score
            readiness_score = (
                calories_score * 0.4 +
                activity_score * 0.4 +
                weight_score * 0.2
            )
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'calories_score': calories_score,
                'activity_score': activity_score,
                'weight_score': weight_score,
                'calories_consumed': day_nutrition['calories_consumed'] if day_nutrition is not None else None,
                'weight': day_nutrition['weight'] if day_nutrition is not None else None,
                'activity_duration': day_activity['duration'].sum() if not day_activity.empty and 'duration' in day_activity.columns else 0
            })
        
        return pd.DataFrame(readiness_data)
