from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, JSON, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    
    # Relationships
    sleep_records = relationship("SleepMetrics", back_populates="user")
    nutrition_records = relationship("NutritionMetrics", back_populates="user")
    exercise_records = relationship("ExerciseMetrics", back_populates="user")
    biometric_records = relationship("BiometricMetrics", back_populates="user")
    mood_records = relationship("MoodMetrics", back_populates="user")

class SleepMetrics(Base, TimestampMixin):
    __tablename__ = 'sleep_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Sleep timing
    bedtime = Column(Time, nullable=False)
    wake_time = Column(Time, nullable=False)
    total_sleep_duration = Column(Float)  # in hours
    sleep_latency = Column(Float)  # time to fall asleep in minutes
    
    # Sleep quality metrics
    deep_sleep_duration = Column(Float)  # in hours
    rem_sleep_duration = Column(Float)  # in hours
    light_sleep_duration = Column(Float)  # in hours
    wake_periods = Column(Integer)  # number of times woken up
    sleep_efficiency = Column(Float)  # percentage of time in bed actually sleeping
    
    # Environmental factors
    room_temperature = Column(Float)  # in celsius
    room_humidity = Column(Float)  # percentage
    noise_level = Column(Float)  # in decibels
    light_level = Column(Float)  # in lux
    
    # Wearable data
    average_heart_rate = Column(Float)
    average_hrv = Column(Float)  # Heart Rate Variability
    respiratory_rate = Column(Float)
    
    # Subjective metrics
    sleep_quality_rating = Column(Integer)  # 1-10 scale
    morning_grogginess = Column(Integer)  # 1-10 scale
    
    # Relationships
    user = relationship("User", back_populates="sleep_records")

class NutritionMetrics(Base, TimestampMixin):
    __tablename__ = 'nutrition_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Macronutrients (in grams)
    calories = Column(Float)
    protein = Column(Float)
    carbohydrates = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    fat = Column(Float)
    saturated_fat = Column(Float)
    unsaturated_fat = Column(Float)
    
    # Micronutrients (in various units)
    vitamins = Column(JSON)  # Store detailed vitamin intake
    minerals = Column(JSON)  # Store detailed mineral intake
    
    # Meal timing
    meal_type = Column(String(20))  # breakfast, lunch, dinner, snack
    meal_time = Column(Time)
    fasting_duration = Column(Float)  # hours since last meal
    
    # Food details
    food_items = Column(JSON)  # List of foods consumed
    meal_photos = Column(JSON)  # URLs to meal photos
    
    # Hydration
    water_intake = Column(Float)  # in milliliters
    other_liquids = Column(Float)  # in milliliters
    
    # Supplements
    supplements = Column(JSON)  # List of supplements taken
    
    # Automated metrics
    blood_glucose_response = Column(Float)  # if using CGM
    
    # Relationships
    user = relationship("User", back_populates="nutrition_records")

class ExerciseMetrics(Base, TimestampMixin):
    __tablename__ = 'exercise_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Exercise details
    activity_type = Column(String(50))  # e.g., running, weightlifting, yoga
    duration = Column(Float)  # in minutes
    distance = Column(Float)  # in kilometers (if applicable)
    
    # Intensity metrics
    average_heart_rate = Column(Float)
    max_heart_rate = Column(Float)
    calories_burned = Column(Float)
    
    # Strength training specifics
    exercises = Column(JSON)  # Details of each exercise (sets, reps, weights)
    total_volume = Column(Float)  # total weight × reps
    one_rep_maxes = Column(JSON)  # Calculated 1RMs for key exercises
    
    # Recovery metrics
    perceived_exertion = Column(Integer)  # 1-10 scale
    fatigue_level = Column(Integer)  # 1-10 scale
    muscle_soreness = Column(JSON)  # Body part specific soreness ratings
    
    # Performance metrics
    heart_rate_zones = Column(JSON)  # Time spent in each HR zone
    power_output = Column(JSON)  # For cycling/running power metrics
    vo2_max_estimate = Column(Float)
    
    # Environmental factors
    temperature = Column(Float)
    humidity = Column(Float)
    altitude = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="exercise_records")

class BiometricMetrics(Base, TimestampMixin):
    __tablename__ = 'biometric_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Basic measurements
    weight = Column(Float)  # in kg
    body_fat_percentage = Column(Float)
    muscle_mass = Column(Float)  # in kg
    bone_mass = Column(Float)  # in kg
    water_percentage = Column(Float)
    
    # Body measurements (cm)
    waist = Column(Float)
    chest = Column(Float)
    hips = Column(Float)
    biceps = Column(Float)
    thighs = Column(Float)
    
    # Vital signs
    resting_heart_rate = Column(Float)
    blood_pressure_systolic = Column(Float)
    blood_pressure_diastolic = Column(Float)
    respiratory_rate = Column(Float)
    body_temperature = Column(Float)
    
    # Blood metrics
    glucose_level = Column(Float)
    ketone_level = Column(Float)
    cholesterol_hdl = Column(Float)
    cholesterol_ldl = Column(Float)
    triglycerides = Column(Float)
    
    # Other health markers
    vo2_max = Column(Float)
    hrv_score = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="biometric_records")

class MoodMetrics(Base, TimestampMixin):
    __tablename__ = 'mood_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Emotional state
    mood_rating = Column(Integer)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    anxiety_level = Column(Integer)  # 1-10 scale
    
    # Mental state
    focus_rating = Column(Integer)  # 1-10 scale
    mental_clarity = Column(Integer)  # 1-10 scale
    motivation_level = Column(Integer)  # 1-10 scale
    
    # Productivity
    productivity_score = Column(Integer)  # 1-10 scale
    flow_state_duration = Column(Float)  # in hours
    
    # Environmental factors
    weather_condition = Column(String(50))
    daylight_exposure = Column(Float)  # in hours
    
    # Notes
    mood_notes = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="mood_records")
