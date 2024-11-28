"""Shimmer Health Data Normalization Client.

This module provides a client for the Shimmer Health Data Aggregation API,
which normalizes health data from various providers into a standardized format.

Shimmer acts as a middleware layer that handles:
    1. Data retrieval from various health providers
    2. Data normalization and standardization
    3. Consistent API interface across providers
    4. OAuth token management
    5. Rate limiting and caching

Supported Providers:
    - Oura Ring
    - Fitbit
    - Garmin
    - Apple Health
    - Google Fit
    - Withings
    - Samsung Health

Data Types:
    - Sleep Episodes
    - Physical Activity
    - Heart Rate
    - Heart Rate Variability
    - Blood Pressure
    - Blood Glucose
    - Body Weight
    - Body Temperature
    - Oxygen Saturation
    - Respiratory Rate

Example:
    >>> client = ShimmerClient(
    ...     base_url="https://api.shimmerapi.com",
    ...     credentials={
    ...         ShimmerEndpoint.OURA: ShimmerCredentials(
    ...             client_id="your-id",
    ...             client_secret="your-secret"
    ...         )
    ...     }
    ... )
    >>> sleep_data = client.get_data(
    ...     endpoint=ShimmerEndpoint.OURA,
    ...     data_type=ShimmerDataType.SLEEP_EPISODE,
    ...     start_date=start_date,
    ...     end_date=end_date
    ... )
"""

from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
import pandas as pd
import requests

class ShimmerEndpoint(str, Enum):
    """Supported Shimmer API endpoints."""
    OURA = "oura"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    WITHINGS = "withings"
    SAMSUNG_HEALTH = "samsung_health"

class ShimmerDataType(str, Enum):
    """Available health data types in Shimmer API."""
    SLEEP_EPISODE = "sleep_episode"
    SLEEP_DURATION = "sleep_duration"
    PHYSICAL_ACTIVITY = "physical_activity"
    HEART_RATE = "heart_rate"
    HRV = "heart_rate_variability"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_GLUCOSE = "blood_glucose"
    BODY_WEIGHT = "body_weight"
    BODY_TEMPERATURE = "body_temperature"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    CALORIES_BURNED = "calories_burned"

@dataclass
class ShimmerCredentials:
    """OAuth credentials for Shimmer API authentication.
    
    Attributes:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        access_token: Optional OAuth access token
        refresh_token: Optional OAuth refresh token
    """
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class ShimmerClient:
    """Client for interacting with Shimmer Health Data API.
    
    This client handles authentication, data retrieval, and normalization
    of health data from various providers through the Shimmer API.
    
    Attributes:
        base_url: Shimmer API base URL
        credentials: Dictionary mapping endpoints to credentials
        session: Requests session for API communication
    """
    
    def __init__(self, base_url: str, credentials: Dict[ShimmerEndpoint, ShimmerCredentials]):
        """Initialize Shimmer client.
        
        Args:
            base_url: Shimmer API base URL
            credentials: Dictionary mapping endpoints to OAuth credentials
        """
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.session = requests.Session()
    
    def get_data(self, endpoint: ShimmerEndpoint, data_type: ShimmerDataType,
                 start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve normalized health data from Shimmer API.
        
        Args:
            endpoint: Provider endpoint to query
            data_type: Type of health data to retrieve
            start_date: Start of date range
            end_date: Optional end of date range
        
        Returns:
            DataFrame containing normalized health data with columns:
                - timestamp: UTC timestamp of measurement
                - value: Primary metric value
                - unit: Unit of measurement
                - type: Measurement type
                - source: Data source/provider
                - metadata: Additional provider-specific data
        
        Raises:
            ValueError: If endpoint or data type is invalid
            requests.RequestException: If API request fails
        """
        if endpoint not in self.credentials:
            raise ValueError(f"No credentials provided for endpoint: {endpoint}")
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "data_type": data_type
        }
        
        response = self.session.get(
            f"{self.base_url}/v1/{endpoint}/data",
            params=params,
            headers=self._get_auth_headers(endpoint)
        )
        response.raise_for_status()
        
        return pd.DataFrame(response.json()["data"])
    
    def _get_auth_headers(self, endpoint: ShimmerEndpoint) -> Dict[str, str]:
        """Get authentication headers for API requests.
        
        Args:
            endpoint: Provider endpoint
            
        Returns:
            Dictionary of HTTP headers including authorization
        """
        creds = self.credentials[endpoint]
        if not creds.access_token:
            self._refresh_token(endpoint)
        
        return {
            "Authorization": f"Bearer {creds.access_token}",
            "Content-Type": "application/json"
        }
    
    def _refresh_token(self, endpoint: ShimmerEndpoint):
        """Refresh OAuth access token for endpoint.
        
        Args:
            endpoint: Provider endpoint
            
        Raises:
            requests.RequestException: If token refresh fails
        """
        creds = self.credentials[endpoint]
        
        response = self.session.post(
            f"{self.base_url}/v1/auth/token",
            json={
                "grant_type": "refresh_token",
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "refresh_token": creds.refresh_token
            }
        )
        response.raise_for_status()
        
        token_data = response.json()
        creds.access_token = token_data["access_token"]
        creds.refresh_token = token_data.get("refresh_token", creds.refresh_token)

class HealthDataFetcher:
    """Fetch and aggregate health data from multiple sources using Shimmer."""
    
    def __init__(self, shimmer_client: ShimmerClient):
        self.client = shimmer_client
    
    def get_sleep_data(self, 
                      endpoints: list[ShimmerEndpoint],
                      start_date: datetime,
                      end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch sleep data from multiple sources."""
        dfs = []
        for endpoint in endpoints:
            try:
                df = self.client.get_data(
                    endpoint=endpoint,
                    data_type=ShimmerDataType.SLEEP_EPISODE,
                    start_date=start_date,
                    end_date=end_date
                )
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching sleep data from {endpoint.value}: {str(e)}")
        
        return pd.concat(dfs) if dfs else pd.DataFrame()
    
    def get_activity_data(self,
                         endpoints: list[ShimmerEndpoint],
                         start_date: datetime,
                         end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch physical activity data from multiple sources."""
        dfs = []
        for endpoint in endpoints:
            try:
                df = self.client.get_data(
                    endpoint=endpoint,
                    data_type=ShimmerDataType.PHYSICAL_ACTIVITY,
                    start_date=start_date,
                    end_date=end_date
                )
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching activity data from {endpoint.value}: {str(e)}")
        
        return pd.concat(dfs) if dfs else pd.DataFrame()
    
    def get_hrv_data(self,
                     endpoints: list[ShimmerEndpoint],
                     start_date: datetime,
                     end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch HRV data from multiple sources."""
        dfs = []
        for endpoint in endpoints:
            try:
                df = self.client.get_data(
                    endpoint=endpoint,
                    data_type=ShimmerDataType.HRV,
                    start_date=start_date,
                    end_date=end_date
                )
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching HRV data from {endpoint.value}: {str(e)}")
        
        return pd.concat(dfs) if dfs else pd.DataFrame()
