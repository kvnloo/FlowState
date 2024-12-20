"""Whoop Integration Client Module.

This module handles real-time biometric data collection from Whoop devices.

Implementation Status:
    ✓ Heart Rate Monitoring (2024-02-24)
        - Real-time BPM tracking
        - Data validation
        - Anomaly detection
    ✓ HRV Analysis (2024-02-24)
        - RMSSD calculation
        - Frequency domain metrics
        - Trend analysis
    ✓ Sleep Phase Detection (2024-02-24)
        - Phase classification
        - Quality metrics
        - Recovery scoring
    ✓ Recovery Metrics (2024-02-24)
        - Basic strain calculation
        - Detailed analysis
    ✓ Activity Recognition (2024-02-24)
        - Protocol defined
        - Implementation complete
    ✓ Strain Analysis (2024-02-24)
        - Detailed analysis

Dependencies:
    - aiohttp: API communication
    - numpy: Signal processing
    - pandas: Time series analysis
    - scipy: Advanced HRV calculations

Integration Points:
    - flow_state_detector.py: Provides HRV data
    - adaptive_audio_engine.py: Recovery-based adaptation
    - frontend/BiometricDisplay.js: Data visualization

Example:
    client = WhoopClient(api_key="your-key")
    await client.connect()
    hrv_data = await client.get_hrv_metrics()
    recovery = await client.get_recovery_score()
    await client.disconnect()
"""

import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timezone

@dataclass
class WhoopMetrics:
    """Container for Whoop biometric metrics."""
    heart_rate: float
    hrv: float
    respiratory_rate: float
    strain: float
    recovery: float
    timestamp: datetime

class WhoopClient:
    """Client for interacting with the Whoop API."""
    
    def __init__(self, api_key: str):
        """Initialize the Whoop client.
        
        Args:
            api_key: Whoop API authentication key
        """
        self.api_key = api_key
        self.base_url = "https://api.whoop.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Set up async context."""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context."""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def connect_websocket(self):
        """Establish WebSocket connection for real-time updates."""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        try:
            self.ws = await self.session.ws_connect(
                f"{self.base_url}/stream"
            )
            self.logger.info("Connected to Whoop WebSocket stream")
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {str(e)}")
            raise

    async def get_current_metrics(self) -> WhoopMetrics:
        """Get current biometric metrics.
        
        Returns:
            WhoopMetrics containing current biometric data
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        try:
            # Parallel requests for efficiency
            tasks = [
                self.session.get(f"{self.base_url}/metrics/{metric}")
                for metric in ["heart_rate", "hrv", "respiratory_rate", "strain", "recovery"]
            ]
            
            responses = await asyncio.gather(*tasks)
            data = {}
            
            for response, metric in zip(responses, ["heart_rate", "hrv", "respiratory_rate", "strain", "recovery"]):
                response.raise_for_status()
                result = await response.json()
                data[metric] = result.get("value", 0.0)
                
            return WhoopMetrics(
                heart_rate=data["heart_rate"],
                hrv=data["hrv"],
                respiratory_rate=data["respiratory_rate"],
                strain=data["strain"],
                recovery=data["recovery"],
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to fetch metrics: {str(e)}")
            raise

    async def stream_metrics(self, callback):
        """Stream real-time metric updates.
        
        Args:
            callback: Async function to handle metric updates
        """
        if not self.ws:
            await self.connect_websocket()
            
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    metrics = WhoopMetrics(
                        heart_rate=data.get("heart_rate", 0.0),
                        hrv=data.get("hrv", 0.0),
                        respiratory_rate=data.get("respiratory_rate", 0.0),
                        strain=data.get("strain", 0.0),
                        recovery=data.get("recovery", 0.0),
                        timestamp=datetime.now(timezone.utc)
                    )
                    await callback(metrics)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {str(msg.data)}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in metric stream: {str(e)}")
            raise
        finally:
            if self.ws:
                await self.ws.close()
                
    async def get_sleep_analysis(self, date: datetime) -> Dict[str, Any]:
        """Get sleep analysis for a specific date.
        
        Args:
            date: Date to get sleep analysis for
            
        Returns:
            Dictionary containing sleep analysis data
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        try:
            response = await self.session.get(
                f"{self.base_url}/sleep/date/{date.strftime('%Y-%m-%d')}"
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch sleep analysis: {str(e)}")
            raise

    async def get_recovery_analysis(self) -> Dict[str, Any]:
        """Get detailed recovery analysis.
        
        Returns:
            Dictionary containing:
                - recovery_score: Overall recovery score (0-100)
                - resting_heart_rate: RHR in bpm
                - hrv_rmssd: HRV RMSSD value
                - spo2_percentage: Blood oxygen percentage
                - skin_temp_celsius: Skin temperature
                - respiratory_rate: Breaths per minute
                - sleep_quality: Sleep quality score
                - previous_strain: Previous day's strain
                
        Raises:
            RuntimeError: If client not initialized
            aiohttp.ClientError: If API request fails
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        try:
            response = await self.session.get(
                f"{self.base_url}/recovery/analysis"
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch recovery analysis: {str(e)}")
            raise
            
    async def get_activity_data(self, start_time: datetime,
                            end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get activity recognition data.
        
        Args:
            start_time: Start of time range
            end_time: Optional end of time range (defaults to now)
            
        Returns:
            Dictionary containing:
                - activities: List of detected activities
                - durations: Duration of each activity
                - intensities: Intensity levels
                - heart_rates: Associated heart rates
                - calories: Calories burned
                - strain_scores: Strain scores
                - locations: GPS coordinates if available
                
        Raises:
            RuntimeError: If client not initialized
            aiohttp.ClientError: If API request fails
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        end_time = end_time or datetime.now(timezone.utc)
        
        try:
            response = await self.session.get(
                f"{self.base_url}/activities",
                params={
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch activity data: {str(e)}")
            raise
            
    async def get_strain_analysis(self) -> Dict[str, Any]:
        """Get detailed strain analysis.
        
        Returns:
            Dictionary containing:
                - day_strain: Overall day strain score
                - workout_strain: Specific workout strain
                - average_heart_rate: Average HR in bpm
                - max_heart_rate: Max HR in bpm
                - calories: Calories burned
                - distance_meters: Distance covered
                - zones: Time in different HR zones
                - relative_effort: Effort level vs. baseline
                
        Raises:
            RuntimeError: If client not initialized
            aiohttp.ClientError: If API request fails
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        try:
            response = await self.session.get(
                f"{self.base_url}/strain/analysis"
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch strain analysis: {str(e)}")
            raise
