from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class HealthMetric:
    timestamp: datetime
    metric_type: str
    value: float
    source: str
    metadata: Dict = None

class HealthDataProvider(ABC):
    """Base class for all health data providers."""
    
    @abstractmethod
    def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep-related metrics."""
        pass
    
    @abstractmethod
    def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch activity-related metrics."""
        pass
    
    @abstractmethod
    def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch Heart Rate Variability data."""
        pass
    
    @abstractmethod
    def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch readiness/recovery metrics."""
        pass

class DataNormalizer:
    """Normalize data from different sources into a consistent format."""
    
    @staticmethod
    def normalize_sleep_data(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Convert source-specific sleep data to standard format."""
        # Implementation will vary based on source
        return df
    
    @staticmethod
    def normalize_activity_data(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Convert source-specific activity data to standard format."""
        # Implementation will vary based on source
        return df
    
    @staticmethod
    def normalize_hrv_data(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Convert source-specific HRV data to standard format."""
        # Implementation will vary based on source
        return df

class HealthDataAggregator:
    """Aggregate and analyze data from multiple sources."""
    
    def __init__(self):
        self.data_providers: List[HealthDataProvider] = []
        
    def add_provider(self, provider: HealthDataProvider):
        self.data_providers.append(provider)
        
    def get_aggregated_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Aggregate sleep data from all providers."""
        dfs = []
        for provider in self.data_providers:
            try:
                df = provider.get_sleep_data(start_date, end_date)
                df = DataNormalizer.normalize_sleep_data(df, provider.__class__.__name__)
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching data from {provider.__class__.__name__}: {str(e)}")
        
        return pd.concat(dfs) if dfs else pd.DataFrame()
    
    def analyze_correlations(self, metrics: List[str], start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Analyze correlations between different health metrics."""
        # Gather all relevant data
        all_data = pd.DataFrame()
        # Implementation for correlation analysis
        return all_data.corr()
