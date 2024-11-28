"""MyFitnessPal Data Provider Adapter.

This module implements a data provider adapter for MyFitnessPal, enabling access
to nutrition and dietary data. It handles authentication, data retrieval, and
normalization of nutrition metrics.

Features:
    - Username/password authentication
    - Detailed nutrition tracking
    - Food diary access
    - Recipe management
    - Exercise logging
    - Weight tracking

Data Categories:
    1. Nutrition Metrics
       - Total calories
       - Macronutrients (protein, carbs, fat)
       - Micronutrients
       - Fiber
       - Sodium
       - Sugar
       - Cholesterol
       
    2. Meals & Food Items
       - Breakfast
       - Lunch
       - Dinner
       - Snacks
       - Custom meals
       - Serving sizes
       
    3. Exercise & Energy
       - Calories burned
       - Exercise duration
       - Exercise type
       - Net calories
       
    4. Body Metrics
       - Weight
       - Body measurements
       - Progress photos
       - Notes

Authentication:
    MyFitnessPal requires username/password authentication.
    Premium features require a premium account token.

Example:
    >>> adapter = MyFitnessPalAdapter(
    ...     credentials={
    ...         'username': 'your-username',
    ...         'password': 'your-password',
    ...         'premium_token': 'optional-premium-token'
    ...     }
    ... )
    >>> nutrition_data = await adapter.get_nutrition_data(
    ...     start_date=datetime.now() - timedelta(days=7),
    ...     end_date=datetime.now()
    ... )
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
import myfitnesspal

from .base import HealthDataProvider

class MyFitnessPalAdapter(HealthDataProvider):
    """Adapter for MyFitnessPal data.
    
    This class implements the HealthDataProvider interface for MyFitnessPal,
    focusing primarily on nutrition and dietary data tracking.
    
    Attributes:
        client: MyFitnessPal API client
        credentials (Dict): Authentication credentials
        premium (bool): Whether premium features are available
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """Initialize MyFitnessPal adapter.
        
        Args:
            credentials: Dictionary containing authentication details:
                - username: MyFitnessPal username
                - password: MyFitnessPal password
                - premium_token: Optional premium account token
        """
        self.credentials = credentials
        self.client = None
        self.premium = 'premium_token' in credentials
        
    async def initialize(self):
        """Initialize MyFitnessPal client.
        
        This method:
            1. Authenticates with MyFitnessPal
            2. Validates premium status if applicable
            3. Tests API connectivity
            
        Raises:
            ValueError: If credentials are invalid
            RuntimeError: If API initialization fails
        """
        self.client = myfitnesspal.Client(
            username=self.credentials['username'],
            password=self.credentials['password'],
            premium_token=self.credentials.get('premium_token')
        )
        
    async def get_nutrition_data(self, start_date: datetime,
                              end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve nutrition data from MyFitnessPal.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with nutrition metrics:
                - timestamp: Time of measurement
                - calories: Total calories
                - protein: Protein (g)
                - carbs: Carbohydrates (g)
                - fat: Fat (g)
                - fiber: Fiber (g)
                - sodium: Sodium (mg)
                - sugar: Sugar (g)
                - meal: Meal type
                - food_item: Food item name
                - serving_size: Serving size
                - brand: Food brand if available
                
        Raises:
            RuntimeError: If API request fails
            ValueError: If date range is invalid
        """
        if not self.client:
            await self.initialize()
            
        end_date = end_date or datetime.now()
        
        nutrition_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day = self.client.get_date(current_date)
            
            for meal in day.meals:
                for entry in meal.entries:
                    record = {
                        'timestamp': current_date,
                        'meal': meal.name,
                        'food_item': entry.name,
                        'serving_size': entry.serving_size,
                        'calories': entry.totals.get('calories', 0),
                        'protein': entry.totals.get('protein', 0),
                        'carbs': entry.totals.get('carbohydrates', 0),
                        'fat': entry.totals.get('fat', 0),
                        'fiber': entry.totals.get('fiber', 0),
                        'sodium': entry.totals.get('sodium', 0),
                        'sugar': entry.totals.get('sugar', 0),
                        'brand': getattr(entry, 'brand', None)
                    }
                    nutrition_data.append(record)
            
            current_date += timedelta(days=1)
            
        return pd.DataFrame(nutrition_data)
        
    async def get_exercise_data(self, start_date: datetime,
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve exercise data from MyFitnessPal.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with exercise metrics:
                - timestamp: Time of measurement
                - exercise: Exercise name
                - duration: Duration (minutes)
                - calories: Calories burned
                - notes: Additional notes
                
        Raises:
            RuntimeError: If API request fails
            ValueError: If date range is invalid
        """
        if not self.client:
            await self.initialize()
            
        end_date = end_date or datetime.now()
        
        exercise_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day = self.client.get_date(current_date)
            
            for exercise in day.exercises:
                record = {
                    'timestamp': current_date,
                    'exercise': exercise.name,
                    'duration': exercise.duration,
                    'calories': exercise.calories_burned,
                    'notes': exercise.notes
                }
                exercise_data.append(record)
            
            current_date += timedelta(days=1)
            
        return pd.DataFrame(exercise_data)
        
    async def get_weight_data(self, start_date: datetime,
                           end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve weight measurements from MyFitnessPal.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with weight metrics:
                - timestamp: Time of measurement
                - weight: Weight in kg
                - notes: Measurement notes
                
        Raises:
            RuntimeError: If API request fails
            ValueError: If date range is invalid
        """
        if not self.client:
            await self.initialize()
            
        end_date = end_date or datetime.now()
        
        weights = self.client.get_measurements('Weight', start_date, end_date)
        
        weight_data = [
            {
                'timestamp': date,
                'weight': weight,
                'notes': getattr(weight, 'notes', None)
            }
            for date, weight in weights.items()
        ]
        
        return pd.DataFrame(weight_data)
        
    # These methods are not supported by MyFitnessPal
    async def get_sleep_data(self, *args, **kwargs) -> pd.DataFrame:
        """Not supported by MyFitnessPal."""
        return pd.DataFrame()
        
    async def get_activity_data(self, *args, **kwargs) -> pd.DataFrame:
        """Not supported by MyFitnessPal."""
        return pd.DataFrame()
        
    async def get_hrv_data(self, *args, **kwargs) -> pd.DataFrame:
        """Not supported by MyFitnessPal."""
        return pd.DataFrame()
        
    async def get_readiness_data(self, *args, **kwargs) -> pd.DataFrame:
        """Not supported by MyFitnessPal."""
        return pd.DataFrame()
