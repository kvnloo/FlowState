"""Health Metrics Models.

This module defines the SQLAlchemy models for storing various health metrics including
sleep, nutrition, exercise, biometrics, and mood data. These models form the core data
structure for the health tracking system.

The models are designed to be flexible enough to accommodate data from multiple providers
while maintaining consistency in how the data is stored and accessed.

Example:
    >>> from backend.core.models.health_metrics import User, SleepMetrics
    >>> user = User(email="user@example.com", name="John Doe")
    >>> sleep_data = SleepMetrics(
    ...     user=user,
    ...     date=datetime.now(),
    ...     duration_mins=480,
    ...     sleep_score=85
    ... )
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base, TimestampMixin):
    """User model for storing user information and preferences.
    
    This model stores core user information and maintains relationships with various
    health metric tables. It also stores provider-specific tokens and user preferences.
    
    Attributes:
        id (int): Primary key
        email (str): User's email address
        name (str): User's full name
        preferences (dict): JSON field for storing user preferences
        provider_tokens (dict): JSON field for storing provider OAuth tokens
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    
    Relationships:
        sleep_metrics: One-to-many relationship with SleepMetrics
        nutrition_metrics: One-to-many relationship with NutritionMetrics
        exercise_metrics: One-to-many relationship with ExerciseMetrics
        biometric_metrics: One-to-many relationship with BiometricMetrics
        mood_metrics: One-to-many relationship with MoodMetrics
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    preferences = Column(JSON, default=dict)
    provider_tokens = Column(JSON, default=dict)
    
    sleep_metrics = relationship("SleepMetrics", back_populates="user", cascade="all, delete-orphan")
    nutrition_metrics = relationship("NutritionMetrics", back_populates="user", cascade="all, delete-orphan")
    exercise_metrics = relationship("ExerciseMetrics", back_populates="user", cascade="all, delete-orphan")
    biometric_metrics = relationship("BiometricMetrics", back_populates="user", cascade="all, delete-orphan")
    mood_metrics = relationship("MoodMetrics", back_populates="user", cascade="all, delete-orphan")

class SleepMetrics(Base, TimestampMixin):
    """Model for storing sleep-related metrics.
    
    This model captures comprehensive sleep data from various providers, normalizing
    it into a consistent format while preserving raw provider data.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to user
        date (datetime): Date of the sleep record
        duration_mins (float): Total sleep duration in minutes
        deep_sleep_mins (float): Deep sleep duration in minutes
        rem_sleep_mins (float): REM sleep duration in minutes
        light_sleep_mins (float): Light sleep duration in minutes
        awake_mins (float): Time awake during sleep period
        sleep_score (float): Overall sleep quality score (0-100)
        provider (str): Name of the data provider (e.g., 'oura', 'whoop')
        raw_data (dict): Original provider data in JSON format
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'sleep_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    duration_mins = Column(Float)
    deep_sleep_mins = Column(Float)
    rem_sleep_mins = Column(Float)
    light_sleep_mins = Column(Float)
    awake_mins = Column(Float)
    sleep_score = Column(Float)
    provider = Column(String)
    raw_data = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="sleep_metrics")

class NutritionMetrics(Base, TimestampMixin):
    """Model for storing nutrition-related metrics.
    
    This model tracks detailed nutrition data including macronutrients and hydration.
    It supports multiple data sources while maintaining a standardized format.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to user
        date (datetime): Date of the nutrition record
        calories (float): Total calories consumed
        protein_g (float): Protein intake in grams
        carbs_g (float): Carbohydrate intake in grams
        fat_g (float): Fat intake in grams
        fiber_g (float): Fiber intake in grams
        water_ml (float): Water intake in milliliters
        provider (str): Name of the data provider
        raw_data (dict): Original provider data in JSON format
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'nutrition_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    calories = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    fiber_g = Column(Float)
    water_ml = Column(Float)
    provider = Column(String)
    raw_data = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="nutrition_metrics")

class ExerciseMetrics(Base, TimestampMixin):
    """Model for storing exercise-related metrics.
    
    This model captures detailed exercise and physical activity data from various
    tracking devices and apps, standardizing it for analysis while preserving
    provider-specific details.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to user
        date (datetime): Date of the exercise record
        activity_type (str): Type of exercise (e.g., 'running', 'cycling')
        duration_mins (float): Activity duration in minutes
        calories_burned (float): Estimated calories burned
        distance_meters (float): Distance covered in meters
        avg_heart_rate (float): Average heart rate during activity
        max_heart_rate (float): Maximum heart rate during activity
        provider (str): Name of the data provider
        raw_data (dict): Original provider data in JSON format
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'exercise_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    activity_type = Column(String)
    duration_mins = Column(Float)
    calories_burned = Column(Float)
    distance_meters = Column(Float)
    avg_heart_rate = Column(Float)
    max_heart_rate = Column(Float)
    provider = Column(String)
    raw_data = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="exercise_metrics")

class BiometricMetrics(Base, TimestampMixin):
    """Model for storing biometric measurements.
    
    This model tracks various physiological measurements and vital signs,
    providing a comprehensive view of physical health markers.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to user
        date (datetime): Date of the biometric record
        weight_kg (float): Weight in kilograms
        body_fat_pct (float): Body fat percentage
        hrv_ms (float): Heart rate variability in milliseconds
        resting_hr (float): Resting heart rate
        blood_glucose (float): Blood glucose level in mg/dL
        systolic_bp (float): Systolic blood pressure in mmHg
        diastolic_bp (float): Diastolic blood pressure in mmHg
        provider (str): Name of the data provider
        raw_data (dict): Original provider data in JSON format
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'biometric_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    weight_kg = Column(Float)
    body_fat_pct = Column(Float)
    hrv_ms = Column(Float)
    resting_hr = Column(Float)
    blood_glucose = Column(Float)
    systolic_bp = Column(Float)
    diastolic_bp = Column(Float)
    provider = Column(String)
    raw_data = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="biometric_metrics")

class MoodMetrics(Base, TimestampMixin):
    """Model for storing mood and mental state metrics.
    
    This model captures subjective and objective measures of psychological
    well-being and readiness, integrating data from various tracking methods.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to user
        date (datetime): Date of the mood record
        mood_score (float): Overall mood score (0-100)
        stress_level (float): Stress level measurement (0-100)
        energy_level (float): Energy level measurement (0-100)
        readiness_score (float): Overall readiness score (0-100)
        notes (str): Additional notes or context
        provider (str): Name of the data provider
        raw_data (dict): Original provider data in JSON format
        created_at (datetime): Timestamp of record creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'mood_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    mood_score = Column(Float)
    stress_level = Column(Float)
    energy_level = Column(Float)
    readiness_score = Column(Float)
    notes = Column(String)
    provider = Column(String)
    raw_data = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="mood_metrics")
