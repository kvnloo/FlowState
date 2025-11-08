"""Shimmer Health Data Provider Implementation.

This module implements a health data provider using the Open mHealth Shimmer
platform for unified data normalization across multiple wearable devices and
health data sources.

Shimmer provides a standardized data format (Open mHealth schemas) that normalizes
diverse health data from various providers into a consistent structure. This enables
seamless integration of data from Apple Health, Google Fit, Fitbit, Oura, Whoop,
and other platforms.

Architecture:
    - ShimmerClient: Low-level API communication
    - HealthDataFetcher: Data retrieval and normalization
    - ShimmerHealthProvider: High-level provider interface

Supported Data Types:
    - Sleep metrics (duration, stages, efficiency)
    - Activity data (workouts, steps, calories)
    - Heart rate variability (RMSSD, SDNN, LF/HF ratio)
    - Readiness scores (recovery, strain, preparedness)
    - Nutrition tracking (macros, calories, hydration)

Data Flow:
    1. Client authenticates with Shimmer API
    2. Request data for specific endpoint and date range
    3. Shimmer normalizes data to Open mHealth format
    4. Provider converts to FlowState internal format
    5. Return standardized pandas DataFrame

Dependencies:
    - pandas: Data manipulation and analysis
    - shimmer_client: Shimmer API integration

See Also:
    :class:`base.HealthDataProvider`: Base provider interface
    :mod:`shimmer_client`: Low-level Shimmer API client

Example:
    >>> from datetime import datetime, timedelta
    >>> from shimmer_client import ShimmerEndpoint
    >>>
    >>> # Configure Shimmer credentials
    >>> credentials = {
    ...     ShimmerEndpoint.OURA: "oura_api_token",
    ...     ShimmerEndpoint.WHOOP: "whoop_api_token"
    ... }
    >>>
    >>> # Initialize provider
    >>> provider = ShimmerHealthProvider(
    ...     shimmer_base_url="https://api.shimmer.health",
    ...     credentials=credentials
    ... )
    >>>
    >>> # Fetch last week's sleep data
    >>> end_date = datetime.now()
    >>> start_date = end_date - timedelta(days=7)
    >>> sleep_df = await provider.get_sleep_data(start_date, end_date)
    >>>
    >>> # Analyze sleep patterns
    >>> avg_duration = sleep_df['duration'].mean()
    >>> avg_efficiency = sleep_df['efficiency'].mean()
    >>> print(f"Average sleep: {avg_duration/60:.1f}h at {avg_efficiency:.0f}% efficiency")
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from .base import HealthDataProvider
from .shimmer_client import ShimmerClient, ShimmerEndpoint, ShimmerDataType, HealthDataFetcher

class ShimmerHealthProvider(HealthDataProvider):
    """Health data provider using Open mHealth Shimmer for data normalization.

    This provider integrates with the Shimmer platform to access health data from
    multiple wearable devices and health platforms. Shimmer handles authentication,
    data retrieval, and normalization to Open mHealth schemas.

    The provider supports multiple simultaneous endpoints, allowing aggregation of
    data from different sources. For example, sleep data from Oura can be combined
    with activity data from Whoop for comprehensive health tracking.

    Attributes
    ----------
    fetcher : HealthDataFetcher
        Shimmer data fetcher instance for API operations
    endpoints : List[ShimmerEndpoint]
        Active endpoints configured for this provider

    Notes
    -----
    Shimmer normalizes data using Open mHealth schemas:
        - Ensures consistent data structure across providers
        - Handles timezone conversions automatically
        - Validates data quality and completeness
        - Provides metadata about data sources

    The provider implements automatic retry logic and rate limiting to handle
    API constraints from various health platforms.

    Examples
    --------
    >>> # Single source (Oura only)
    >>> provider = ShimmerHealthProvider(
    ...     "https://api.shimmer.health",
    ...     {ShimmerEndpoint.OURA: "token"}
    ... )
    >>>
    >>> # Multiple sources for redundancy
    >>> provider = ShimmerHealthProvider(
    ...     "https://api.shimmer.health",
    ...     {
    ...         ShimmerEndpoint.OURA: "oura_token",
    ...         ShimmerEndpoint.WHOOP: "whoop_token",
    ...         ShimmerEndpoint.APPLE_HEALTH: "apple_token"
    ...     }
    ... )
    """
    
    def __init__(self, shimmer_base_url: str, credentials: Dict[ShimmerEndpoint, str]):
        self.fetcher = HealthDataFetcher(
            ShimmerClient(shimmer_base_url, credentials)
        )
        self.endpoints = list(credentials.keys())
    
    async def get_sleep_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve sleep metrics from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized sleep metrics:
                - timestamp: Time of measurement
                - duration: Total sleep duration (minutes)
                - deep_sleep: Deep sleep duration (minutes)
                - rem_sleep: REM sleep duration (minutes)
                - light_sleep: Light sleep duration (minutes)
                - awake: Time awake (minutes)
                - efficiency: Sleep efficiency (%)
                - source: Data source
        """
        return self.fetcher.get_sleep_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_activity_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve activity metrics from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized activity metrics:
                - timestamp: Time of measurement
                - type: Activity type
                - duration: Duration (minutes)
                - calories: Energy burned
                - distance: Distance (meters)
                - steps: Step count
                - heart_rate: Average heart rate
                - source: Data source
        """
        # Get both physical activity and step count data
        activity_df = self.fetcher.get_activity_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
        
        steps_df = self.fetcher.client.get_data(
            endpoint=self.endpoints[0],  # Use primary source for steps
            data_type=ShimmerDataType.STEP_COUNT,
            start_date=start_date,
            end_date=end_date
        )
        
        # Merge activity and steps data
        if not activity_df.empty and not steps_df.empty:
            activity_df = activity_df.merge(
                steps_df[['timestamp', 'steps']],
                on='timestamp',
                how='outer'
            )
        
        return activity_df
    
    async def get_hrv_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve heart rate variability data from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized HRV metrics:
                - timestamp: Time of measurement
                - rmssd: Root mean square of successive differences
                - sdnn: Standard deviation of NN intervals
                - lf_hf_ratio: Low-frequency to high-frequency ratio
                - heart_rate: Associated heart rate
                - source: Data source
        """
        return self.fetcher.get_hrv_data(
            endpoints=self.endpoints,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_readiness_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Calculate comprehensive readiness metrics from aggregated health data.

        This method computes daily readiness and recovery scores by aggregating
        multiple health metrics into a holistic assessment of physical preparedness
        and recovery status. The algorithm considers sleep quality, activity load,
        autonomic nervous system balance (HRV), and cardiovascular stress.

        The readiness score provides actionable insights for:
            - Training intensity recommendations
            - Recovery day identification
            - Performance optimization timing
            - Overtraining prevention

        Parameters
        ----------
        start_date : datetime
            Start of the date range for data retrieval
        end_date : Optional[datetime], default=None
            End of date range, defaults to current time if not specified

        Returns
        -------
        pd.DataFrame
            DataFrame with daily readiness metrics containing:

            Core Metrics:
                - date : datetime
                    Date of the readiness assessment
                - readiness_score : float
                    Overall readiness score (0-100), weighted composite of all factors
                - sleep_score : float
                    Sleep contribution (0-100)
                - activity_score : float
                    Activity contribution (0-100)
                - hrv_score : float
                    HRV contribution (0-100)
                - hr_score : float
                    Heart rate contribution (0-100)

            Supporting Data:
                - sleep_duration : float
                    Total sleep in minutes
                - steps : int
                    Daily step count
                - hrv : float
                    Average HRV (RMSSD in ms)
                - heart_rate : float
                    Average resting heart rate (bpm)

        Notes
        -----
        Readiness Calculation Formula:

        .. math::

            R = 0.4 \\cdot S_{sleep} + 0.3 \\cdot S_{activity} + 0.2 \\cdot S_{HRV} + 0.1 \\cdot S_{HR}

        where each component score :math:`S_x \\in [0, 100]`.

        Component Scoring:

        Sleep Score:
            .. math::

                S_{sleep} = \\min\\left(100, \\frac{duration_{minutes}}{480} \\times 100\\right)

            Target: 8 hours (480 minutes) = 100 points

        Activity Score:
            .. math::

                S_{activity} = \\min\\left(100, \\frac{steps}{10000} \\times 100\\right)

            Target: 10,000 steps = 100 points

        HRV Score:
            .. math::

                S_{HRV} = \\min\\left(100, \\frac{RMSSD}{100} \\times 100\\right)

            Target: 100ms RMSSD = 100 points (varies by individual)

        Heart Rate Score:
            .. math::

                S_{HR} = 100 - |HR - 70|

            Target: 70 bpm = 100 points, penalized for deviation

        Interpretation Guidelines:
            - 80-100: Optimal readiness, high-intensity training recommended
            - 60-79: Good readiness, moderate training appropriate
            - 40-59: Reduced readiness, light training or active recovery
            - 0-39: Poor readiness, rest day strongly recommended

        Weights are based on research showing sleep and activity as primary
        drivers of recovery, with HRV and resting heart rate as supporting
        autonomic indicators.

        Examples
        --------
        >>> from datetime import datetime, timedelta
        >>>
        >>> # Get last 30 days of readiness data
        >>> end = datetime.now()
        >>> start = end - timedelta(days=30)
        >>> readiness = await provider.get_readiness_data(start, end)
        >>>
        >>> # Analyze trends
        >>> print(f"Average readiness: {readiness['readiness_score'].mean():.1f}")
        >>> print(f"Sleep contribution: {readiness['sleep_score'].mean():.1f}")
        >>>
        >>> # Identify recovery days needed
        >>> low_readiness = readiness[readiness['readiness_score'] < 60]
        >>> print(f"Days needing recovery: {len(low_readiness)}")
        >>>
        >>> # Correlate with HRV
        >>> import matplotlib.pyplot as plt
        >>> readiness.plot(x='date', y=['readiness_score', 'hrv_score'])
        >>> plt.show()

        See Also
        --------
        get_sleep_data : Sleep metrics retrieval
        get_activity_data : Activity metrics retrieval
        get_hrv_data : Heart rate variability data
        """
        # Fetch all required metrics
        sleep_df = await self.get_sleep_data(start_date, end_date)
        activity_df = await self.get_activity_data(start_date, end_date)
        hrv_df = await self.get_hrv_data(start_date, end_date)
        
        # Get heart rate data
        hr_df = self.fetcher.client.get_data(
            endpoint=self.endpoints[0],  # Use primary source for heart rate
            data_type=ShimmerDataType.HEART_RATE,
            start_date=start_date,
            end_date=end_date
        )
        
        readiness_data = []
        for date in pd.date_range(start_date, end_date or datetime.now(), freq='D'):
            next_date = date + pd.Timedelta(days=1)
            
            # Calculate daily metrics
            day_sleep = sleep_df[
                (sleep_df['timestamp'] >= date) & 
                (sleep_df['timestamp'] < next_date)
            ]['duration'].sum() if 'duration' in sleep_df.columns else 0
            
            day_activity = activity_df[
                (activity_df['timestamp'] >= date) & 
                (activity_df['timestamp'] < next_date)
            ]
            
            day_hrv = hrv_df[
                (hrv_df['timestamp'] >= date) & 
                (hrv_df['timestamp'] < next_date)
            ]['hrv'].mean() if 'hrv' in hrv_df.columns else None
            
            day_hr = hr_df[
                (hr_df['timestamp'] >= date) & 
                (hr_df['timestamp'] < next_date)
            ]['heart_rate'].mean() if 'heart_rate' in hr_df.columns else None
            
            # Calculate component scores
            sleep_score = min(100, (day_sleep / 8) * 100)  # Optimal sleep = 8 hours
            
            activity_score = min(100, day_activity['steps'].sum() / 10000 * 100) \
                if not day_activity.empty and 'steps' in day_activity.columns else 0
            
            hrv_score = min(100, (day_hrv / 100) * 100) if day_hrv is not None else 50
            hr_score = 100 - abs(day_hr - 70) if day_hr is not None else 50
            
            # Calculate weighted readiness score
            readiness_score = (
                sleep_score * 0.4 +
                activity_score * 0.3 +
                hrv_score * 0.2 +
                hr_score * 0.1
            )
            
            readiness_data.append({
                'date': date,
                'readiness_score': readiness_score,
                'sleep_score': sleep_score,
                'activity_score': activity_score,
                'hrv_score': hrv_score,
                'hr_score': hr_score,
                'sleep_duration': day_sleep,
                'steps': day_activity['steps'].sum() if not day_activity.empty and 'steps' in day_activity.columns else 0,
                'hrv': day_hrv,
                'heart_rate': day_hr
            })
        
        return pd.DataFrame(readiness_data)
    
    async def get_nutrition_data(self, start_date: datetime, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve nutrition data from the data source.
        
        Args:
            start_date: Start of date range
            end_date: Optional end of date range
            
        Returns:
            DataFrame with normalized nutrition metrics:
                - timestamp: Time of measurement
                - calories: Total calories
                - protein: Protein (g)
                - carbs: Carbohydrates (g)
                - fat: Fat (g)
                - fiber: Fiber (g)
                - water: Water intake (ml)
                - source: Data source
        """
        # TO DO: Implement nutrition data retrieval
        pass
    
    def normalize_timestamp(self, timestamp: datetime) -> datetime:
        """Convert timestamp to UTC datetime.
        
        Args:
            timestamp: Input timestamp in any format
            
        Returns:
            Normalized UTC datetime
        """
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        return pd.Timestamp(timestamp).tz_localize(None)
    
    def normalize_duration(self, duration: float, unit: str = 'minutes') -> float:
        """Convert duration to minutes.
        
        Args:
            duration: Duration value
            unit: Input unit ('seconds', 'minutes', 'hours')
            
        Returns:
            Duration in minutes
        """
        conversions = {
            'seconds': 1/60,
            'minutes': 1,
            'hours': 60
        }
        return float(duration) * conversions.get(unit, 1)
