from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import requests
from dataclasses import dataclass

@dataclass
class KovaakMetric:
    timestamp: datetime
    scenario: str
    score: float
    accuracy: float
    time_to_target: float
    targets_hit: int
    shots_fired: int
    metadata: Dict = None

class KovaakClient:
    """Client for interacting with Kovaak's FPS Aim Trainer API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def get_recent_scores(self, scenario: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Fetch recent scores, optionally filtered by scenario."""
        # Implementation will depend on actual Kovaak's API
        # This is a placeholder structure
        return pd.DataFrame()
    
    def get_progress_over_time(self, scenario: str, start_date: datetime, 
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Analyze progress in a specific scenario over time."""
        scores = self.get_recent_scores(scenario)
        return scores.sort_values('timestamp')
    
    def analyze_peak_performance_conditions(self, metrics_df: pd.DataFrame) -> Dict:
        """Analyze conditions during peak performance sessions."""
        # Identify top 10% of performances
        top_scores = metrics_df.nlargest(int(len(metrics_df) * 0.1), 'score')
        
        # Analyze common factors
        analysis = {
            'avg_time_of_day': top_scores['timestamp'].dt.hour.mean(),
            'avg_accuracy': top_scores['accuracy'].mean(),
            'avg_time_to_target': top_scores['time_to_target'].mean(),
        }
        
        return analysis

class VisualPerformanceAnalyzer:
    """Analyze visual performance metrics from Kovaak's and eye tracking data."""
    
    def __init__(self, kovaak_client: KovaakClient):
        self.kovaak_client = kovaak_client
    
    def analyze_reaction_time_correlation(self, eye_tracking_data: pd.DataFrame, 
                                       kovaak_data: pd.DataFrame) -> Dict:
        """Analyze correlation between eye tracking metrics and aim performance."""
        # Merge eye tracking and Kovaak's data based on timestamp
        merged_data = pd.merge_asof(eye_tracking_data, kovaak_data, 
                                  on='timestamp', direction='nearest')
        
        correlations = {
            'saccade_speed_vs_accuracy': merged_data['saccade_speed'].corr(merged_data['accuracy']),
            'fixation_duration_vs_time_to_target': merged_data['fixation_duration'].corr(merged_data['time_to_target']),
            'blink_rate_vs_score': merged_data['blink_rate'].corr(merged_data['score'])
        }
        
        return correlations
    
    def get_visual_fatigue_indicators(self, eye_tracking_data: pd.DataFrame) -> Dict:
        """Analyze eye tracking data for signs of visual fatigue."""
        # Calculate various fatigue indicators
        indicators = {
            'blink_rate_change': None,  # Implement blink rate trend analysis
            'saccade_velocity_change': None,  # Implement saccade velocity trend
            'fixation_stability': None  # Implement fixation stability analysis
        }
        
        return indicators
