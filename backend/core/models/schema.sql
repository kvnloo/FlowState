-- Health Tracking Schema

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sleep metrics table
CREATE TABLE sleep_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    bedtime TIME NOT NULL,
    wake_time TIME NOT NULL,
    total_sleep_duration DECIMAL,  -- in hours
    sleep_latency DECIMAL,  -- time to fall asleep in minutes
    deep_sleep_duration DECIMAL,  -- in hours
    rem_sleep_duration DECIMAL,  -- in hours
    light_sleep_duration DECIMAL,  -- in hours
    wake_periods INTEGER,  -- number of times woken up
    sleep_efficiency DECIMAL,  -- percentage of time in bed actually sleeping
    room_temperature DECIMAL,  -- in celsius
    room_humidity DECIMAL,  -- percentage
    noise_level DECIMAL,  -- in decibels
    light_level DECIMAL,  -- in lux
    average_heart_rate DECIMAL,
    average_hrv DECIMAL,  -- Heart Rate Variability
    respiratory_rate DECIMAL,
    sleep_quality_rating INTEGER,  -- 1-10 scale
    morning_grogginess INTEGER,  -- 1-10 scale
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Nutrition metrics table
CREATE TABLE nutrition_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    calories DECIMAL,
    protein DECIMAL,  -- in grams
    carbohydrates DECIMAL,  -- in grams
    fiber DECIMAL,  -- in grams
    sugar DECIMAL,  -- in grams
    fat DECIMAL,  -- in grams
    saturated_fat DECIMAL,  -- in grams
    unsaturated_fat DECIMAL,  -- in grams
    vitamins JSONB,  -- detailed vitamin intake
    minerals JSONB,  -- detailed mineral intake
    meal_type VARCHAR(20),  -- breakfast, lunch, dinner, snack
    meal_time TIME,
    fasting_duration DECIMAL,  -- hours since last meal
    food_items JSONB,  -- list of foods consumed
    meal_photos JSONB,  -- URLs to meal photos
    water_intake DECIMAL,  -- in milliliters
    other_liquids DECIMAL,  -- in milliliters
    supplements JSONB,  -- list of supplements taken
    blood_glucose_response DECIMAL,  -- if using CGM
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Exercise metrics table
CREATE TABLE exercise_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activity_type VARCHAR(50),  -- e.g., running, weightlifting, yoga
    duration DECIMAL,  -- in minutes
    distance DECIMAL,  -- in kilometers
    average_heart_rate DECIMAL,
    max_heart_rate DECIMAL,
    calories_burned DECIMAL,
    exercises JSONB,  -- details of each exercise (sets, reps, weights)
    total_volume DECIMAL,  -- total weight × reps
    one_rep_maxes JSONB,  -- calculated 1RMs for key exercises
    perceived_exertion INTEGER,  -- 1-10 scale
    fatigue_level INTEGER,  -- 1-10 scale
    muscle_soreness JSONB,  -- body part specific soreness ratings
    heart_rate_zones JSONB,  -- time spent in each HR zone
    power_output JSONB,  -- for cycling/running power metrics
    vo2_max_estimate DECIMAL,
    temperature DECIMAL,
    humidity DECIMAL,
    altitude DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Biometric metrics table
CREATE TABLE biometric_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    weight DECIMAL,  -- in kg
    body_fat_percentage DECIMAL,
    muscle_mass DECIMAL,  -- in kg
    bone_mass DECIMAL,  -- in kg
    water_percentage DECIMAL,
    waist DECIMAL,  -- in cm
    chest DECIMAL,  -- in cm
    hips DECIMAL,  -- in cm
    biceps DECIMAL,  -- in cm
    thighs DECIMAL,  -- in cm
    resting_heart_rate DECIMAL,
    blood_pressure_systolic DECIMAL,
    blood_pressure_diastolic DECIMAL,
    respiratory_rate DECIMAL,
    body_temperature DECIMAL,
    glucose_level DECIMAL,
    ketone_level DECIMAL,
    cholesterol_hdl DECIMAL,
    cholesterol_ldl DECIMAL,
    triglycerides DECIMAL,
    vo2_max DECIMAL,
    hrv_score DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Mood metrics table
CREATE TABLE mood_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    mood_rating INTEGER,  -- 1-10 scale
    energy_level INTEGER,  -- 1-10 scale
    stress_level INTEGER,  -- 1-10 scale
    anxiety_level INTEGER,  -- 1-10 scale
    focus_rating INTEGER,  -- 1-10 scale
    mental_clarity INTEGER,  -- 1-10 scale
    motivation_level INTEGER,  -- 1-10 scale
    productivity_score INTEGER,  -- 1-10 scale
    flow_state_duration DECIMAL,  -- in hours
    weather_condition VARCHAR(50),
    daylight_exposure DECIMAL,  -- in hours
    mood_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX idx_sleep_metrics_user_date ON sleep_metrics(user_id, date);
CREATE INDEX idx_nutrition_metrics_user_timestamp ON nutrition_metrics(user_id, timestamp);
CREATE INDEX idx_exercise_metrics_user_timestamp ON exercise_metrics(user_id, timestamp);
CREATE INDEX idx_biometric_metrics_user_timestamp ON biometric_metrics(user_id, timestamp);
CREATE INDEX idx_mood_metrics_user_timestamp ON mood_metrics(user_id, timestamp);

-- Triggers for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sleep_metrics_updated_at
    BEFORE UPDATE ON sleep_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nutrition_metrics_updated_at
    BEFORE UPDATE ON nutrition_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercise_metrics_updated_at
    BEFORE UPDATE ON exercise_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_biometric_metrics_updated_at
    BEFORE UPDATE ON biometric_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mood_metrics_updated_at
    BEFORE UPDATE ON mood_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
