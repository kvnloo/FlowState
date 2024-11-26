from typing import Dict, List, Optional
import requests
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
from enum import Enum

class ShimmerDataType(Enum):
    PHYSICAL_ACTIVITY = "physical_activity"
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BODY_WEIGHT = "body_weight"
    BODY_TEMPERATURE = "body_temperature"
    SLEEP_DURATION = "sleep_duration"
    SLEEP_EPISODE = "sleep_episode"
    STEP_COUNT = "step_count"
    CALORIES_BURNED = "calories_burned"
    HRV = "heart_rate_variability"

class ShimmerEndpoint(Enum):
    GOOGLEFIT = "googlefit"
    FITBIT = "fitbit"
    OURA = "oura"
    APPLE_HEALTH = "apple_health"
    MYFITNESSPAL = "myfitnesspal"

@dataclass
class ShimmerCredentials:
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class ShimmerClient:
    """Client for interacting with Open mHealth Shimmer API."""
    
    def __init__(self, base_url: str, credentials: Dict[ShimmerEndpoint, ShimmerCredentials]):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.session = requests.Session()
    
    def authorize_shim(self, endpoint: ShimmerEndpoint) -> str:
        """Get authorization URL for a specific shim."""
        creds = self.credentials[endpoint]
        response = requests.get(
            f"{self.base_url}/authorize/{endpoint.value}",
            params={
                "client_id": creds.client_id,
                "client_secret": creds.client_secret
            }
        )
        response.raise_for_status()
        return response.json()["authorization_url"]
    
    def get_data(self, 
                 endpoint: ShimmerEndpoint,
                 data_type: ShimmerDataType,
                 start_date: datetime,
                 end_date: Optional[datetime] = None,
                 normalize: bool = True) -> pd.DataFrame:
        """Fetch data from a specific shim for a given data type."""
        if end_date is None:
            end_date = datetime.now()
            
        creds = self.credentials[endpoint]
        
        response = requests.get(
            f"{self.base_url}/data/{endpoint.value}/{data_type.value}",
            params={
                "access_token": creds.access_token,
                "normalized": normalize,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        )
        response.raise_for_status()
        
        # Convert Open mHealth format to DataFrame
        data = response.json()
        return self._omh_to_dataframe(data)
    
    def _omh_to_dataframe(self, omh_data: List[Dict]) -> pd.DataFrame:
        """Convert Open mHealth format data to pandas DataFrame."""
        normalized_data = []
        
        for point in omh_data:
            body = point.get("body", {})
            
            # Extract common fields
            row = {
                "timestamp": point.get("header", {}).get("creation_date_time"),
                "schema_id": point.get("header", {}).get("schema_id"),
                "source": point.get("header", {}).get("acquisition_provenance", {}).get("source_name")
            }
            
            # Add all body measurements
            if isinstance(body, dict):
                for key, value in body.items():
                    if isinstance(value, dict) and "value" in value:
                        row[key] = value["value"]
                        row[f"{key}_unit"] = value.get("unit", None)
                    else:
                        row[key] = value
            
            normalized_data.append(row)
        
        df = pd.DataFrame(normalized_data)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
        return df

class HealthDataFetcher:
    """Fetch and aggregate health data from multiple sources using Shimmer."""
    
    def __init__(self, shimmer_client: ShimmerClient):
        self.client = shimmer_client
    
    def get_sleep_data(self, 
                      endpoints: List[ShimmerEndpoint],
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
                         endpoints: List[ShimmerEndpoint],
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
                     endpoints: List[ShimmerEndpoint],
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
