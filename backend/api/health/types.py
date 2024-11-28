from datetime import datetime
from typing import List, Optional
import strawberry
from decimal import Decimal

@strawberry.type
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

@strawberry.type
class SleepMetrics:
    id: int
    user_id: int
    date: datetime
    bedtime: str
    wake_time: str
    total_sleep_duration: Optional[Decimal]
    sleep_latency: Optional[Decimal]
    deep_sleep_duration: Optional[Decimal]
    rem_sleep_duration: Optional[Decimal]
    light_sleep_duration: Optional[Decimal]
    wake_periods: Optional[int]
    sleep_efficiency: Optional[Decimal]
    room_temperature: Optional[Decimal]
    room_humidity: Optional[Decimal]
    noise_level: Optional[Decimal]
    light_level: Optional[Decimal]
    average_heart_rate: Optional[Decimal]
    average_hrv: Optional[Decimal]
    respiratory_rate: Optional[Decimal]
    sleep_quality_rating: Optional[int]
    morning_grogginess: Optional[int]

@strawberry.type
class NutritionMetrics:
    id: int
    user_id: int
    timestamp: datetime
    calories: Optional[Decimal]
    protein: Optional[Decimal]
    carbohydrates: Optional[Decimal]
    fiber: Optional[Decimal]
    sugar: Optional[Decimal]
    fat: Optional[Decimal]
    saturated_fat: Optional[Decimal]
    unsaturated_fat: Optional[Decimal]
    vitamins: Optional[dict]
    minerals: Optional[dict]
    meal_type: Optional[str]
    meal_time: Optional[str]
    fasting_duration: Optional[Decimal]
    food_items: Optional[List[str]]
    meal_photos: Optional[List[str]]
    water_intake: Optional[Decimal]
    other_liquids: Optional[Decimal]
    supplements: Optional[List[str]]
    blood_glucose_response: Optional[Decimal]

@strawberry.type
class ExerciseMetrics:
    id: int
    user_id: int
    timestamp: datetime
    activity_type: Optional[str]
    duration: Optional[Decimal]
    distance: Optional[Decimal]
    average_heart_rate: Optional[Decimal]
    max_heart_rate: Optional[Decimal]
    calories_burned: Optional[Decimal]
    exercises: Optional[dict]
    total_volume: Optional[Decimal]
    one_rep_maxes: Optional[dict]
    perceived_exertion: Optional[int]
    fatigue_level: Optional[int]
    muscle_soreness: Optional[dict]
    heart_rate_zones: Optional[dict]
    power_output: Optional[dict]
    vo2_max_estimate: Optional[Decimal]
    temperature: Optional[Decimal]
    humidity: Optional[Decimal]
    altitude: Optional[Decimal]

@strawberry.type
class BiometricMetrics:
    id: int
    user_id: int
    timestamp: datetime
    weight: Optional[Decimal]
    body_fat_percentage: Optional[Decimal]
    muscle_mass: Optional[Decimal]
    bone_mass: Optional[Decimal]
    water_percentage: Optional[Decimal]
    waist: Optional[Decimal]
    chest: Optional[Decimal]
    hips: Optional[Decimal]
    biceps: Optional[Decimal]
    thighs: Optional[Decimal]
    resting_heart_rate: Optional[Decimal]
    blood_pressure_systolic: Optional[Decimal]
    blood_pressure_diastolic: Optional[Decimal]
    respiratory_rate: Optional[Decimal]
    body_temperature: Optional[Decimal]
    glucose_level: Optional[Decimal]
    ketone_level: Optional[Decimal]
    cholesterol_hdl: Optional[Decimal]
    cholesterol_ldl: Optional[Decimal]
    triglycerides: Optional[Decimal]
    vo2_max: Optional[Decimal]
    hrv_score: Optional[Decimal]

@strawberry.type
class MoodMetrics:
    id: int
    user_id: int
    timestamp: datetime
    mood_rating: Optional[int]
    energy_level: Optional[int]
    stress_level: Optional[int]
    anxiety_level: Optional[int]
    focus_rating: Optional[int]
    mental_clarity: Optional[int]
    motivation_level: Optional[int]
    productivity_score: Optional[int]
    flow_state_duration: Optional[Decimal]
    weather_condition: Optional[str]
    daylight_exposure: Optional[Decimal]
    mood_notes: Optional[str]
