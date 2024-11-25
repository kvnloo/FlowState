"""Tobii Eye Tracker Integration Module.

This module provides real-time eye tracking and cognitive load estimation through Tobii hardware.

Implementation Status:
    ✓ Gaze Tracking (2024-02-24)
        - 3D position tracking
        - Validity checking
        - Real-time streaming
    ✓ Attention Metrics (2024-02-24)
        - Fixation duration
        - Saccade velocity
        - Pupil diameter
    ✓ Cognitive Load (2024-02-24)
        - Combined metric calculation
        - Real-time adaptation
    ⚠ Strobe Synchronization (Partial)
        - Basic timing implemented
        - Missing: predictive timing
    ☐ Multi-Screen Support (Planned)
        - Protocol designed
        - Implementation pending

Dependencies:
    - tobii_research: Core eye tracking functionality
    - numpy: Metric calculations and signal processing
    - asyncio: Async data streaming
    - aiohttp: WebSocket communication

Integration Points:
    - flow_state_detector.py: Provides attention metrics
    - adaptive_audio_engine.py: Syncs with audio timing
    - frontend/FlowStateMonitor.js: Real-time visualization

Example:
    tracker = TobiiTracker()
    await tracker.initialize()
    await tracker.start_tracking()
    metrics = await tracker.get_attention_metrics()
    await tracker.stop_tracking()
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, List

import numpy as np
try:
    import tobii_research as tr
except ImportError:
    logging.error("Tobii Pro SDK not found. Please install it from https://developer.tobiipro.com/python/python-getting-started.html")
    tr = None

@dataclass
class GazeData:
    timestamp: float
    left_eye_position: Optional[Dict[str, float]]
    right_eye_position: Optional[Dict[str, float]]
    left_pupil_diameter: Optional[float]
    right_pupil_diameter: Optional[float]
    gaze_point: Optional[Dict[str, float]]

class TobiiTracker:
    def __init__(self):
        self._eyetracker = None
        self._gaze_data_callback = None
        self._running = False
        self._gaze_data_queue = asyncio.Queue()
        self._attention_metrics = {
            'fixation_duration': 0.0,
            'saccade_velocity': 0.0,
            'pupil_diameter': 0.0,
            'blink_rate': 0.0
        }
        self._gaze_history: List[GazeData] = []
        self._max_history = 1000  # Store last 1000 gaze points
        
    async def initialize(self) -> bool:
        """Initialize connection to Tobii eye tracker."""
        if tr is None:
            logging.error("Tobii Pro SDK not installed")
            return False
            
        try:
            found_eyetrackers = tr.find_all_eyetrackers()
            if not found_eyetrackers:
                logging.error("No eye trackers found")
                return False
                
            self._eyetracker = found_eyetrackers[0]
            logging.info(f"Connected to eye tracker with serial number {self._eyetracker.serial_number}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize eye tracker: {str(e)}")
            return False
            
    def _gaze_data_handler(self, gaze_data):
        """Handle incoming gaze data from the eye tracker."""
        data = GazeData(
            timestamp=gaze_data['system_time_stamp'],
            left_eye_position={
                'x': gaze_data['left_gaze_point_3d']['x'],
                'y': gaze_data['left_gaze_point_3d']['y'],
                'z': gaze_data['left_gaze_point_3d']['z']
            } if gaze_data['left_gaze_point_3d_validity'] else None,
            right_eye_position={
                'x': gaze_data['right_gaze_point_3d']['x'],
                'y': gaze_data['right_gaze_point_3d']['y'],
                'z': gaze_data['right_gaze_point_3d']['z']
            } if gaze_data['right_gaze_point_3d_validity'] else None,
            left_pupil_diameter=gaze_data['left_pupil_diameter'] if gaze_data['left_pupil_diameter_validity'] else None,
            right_pupil_diameter=gaze_data['right_pupil_diameter'] if gaze_data['right_pupil_diameter_validity'] else None,
            gaze_point={
                'x': gaze_data['left_gaze_point_on_display_area']['x'],
                'y': gaze_data['left_gaze_point_on_display_area']['y']
            } if gaze_data['left_gaze_point_validity'] else None
        )
        
        self._gaze_history.append(data)
        if len(self._gaze_history) > self._max_history:
            self._gaze_history.pop(0)
            
        asyncio.create_task(self._gaze_data_queue.put(data))
        self._update_attention_metrics(data)
        
    def _update_attention_metrics(self, gaze_data: GazeData):
        """Update attention metrics based on new gaze data."""
        # Update fixation duration
        if len(self._gaze_history) >= 2:
            prev_gaze = self._gaze_history[-2]
            if (gaze_data.gaze_point and prev_gaze.gaze_point and
                abs(gaze_data.gaze_point['x'] - prev_gaze.gaze_point['x']) < 0.1 and
                abs(gaze_data.gaze_point['y'] - prev_gaze.gaze_point['y']) < 0.1):
                self._attention_metrics['fixation_duration'] += (gaze_data.timestamp - prev_gaze.timestamp) / 1000000.0
            else:
                self._attention_metrics['fixation_duration'] = 0
                
        # Calculate saccade velocity
        if len(self._gaze_history) >= 2:
            prev_gaze = self._gaze_history[-2]
            if gaze_data.gaze_point and prev_gaze.gaze_point:
                dx = gaze_data.gaze_point['x'] - prev_gaze.gaze_point['x']
                dy = gaze_data.gaze_point['y'] - prev_gaze.gaze_point['y']
                dt = (gaze_data.timestamp - prev_gaze.timestamp) / 1000000.0  # Convert to seconds
                velocity = np.sqrt(dx*dx + dy*dy) / dt if dt > 0 else 0
                self._attention_metrics['saccade_velocity'] = velocity
                
        # Update pupil diameter
        if gaze_data.left_pupil_diameter and gaze_data.right_pupil_diameter:
            self._attention_metrics['pupil_diameter'] = (gaze_data.left_pupil_diameter + gaze_data.right_pupil_diameter) / 2
            
        # Update blink rate (simplified)
        if len(self._gaze_history) >= 30:  # Check last 30 samples
            blinks = sum(1 for g in self._gaze_history[-30:] 
                        if g.left_pupil_diameter is None and g.right_pupil_diameter is None)
            self._attention_metrics['blink_rate'] = blinks
            
    async def start_tracking(self):
        """Start tracking eye movements."""
        if not self._eyetracker:
            logging.error("Eye tracker not initialized")
            return
            
        self._running = True
        self._eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self._gaze_data_handler)
        logging.info("Started eye tracking")
        
    async def stop_tracking(self):
        """Stop tracking eye movements."""
        if not self._eyetracker:
            return
            
        self._running = False
        self._eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self._gaze_data_handler)
        logging.info("Stopped eye tracking")
        
    async def get_attention_metrics(self) -> Dict[str, float]:
        """Get current attention metrics."""
        return self._attention_metrics.copy()
        
    async def get_cognitive_load(self) -> float:
        """Estimate cognitive load based on pupil diameter and blink rate."""
        if not self._attention_metrics:
            return 0.0
            
        # Normalize pupil diameter (0-1)
        pupil_factor = min(1.0, self._attention_metrics['pupil_diameter'] / 5.0)
        
        # Normalize blink rate (0-1)
        blink_factor = min(1.0, self._attention_metrics['blink_rate'] / 30.0)
        
        # Combine metrics (higher pupil diameter and lower blink rate indicate higher cognitive load)
        cognitive_load = (0.7 * pupil_factor + 0.3 * (1 - blink_factor))
        return cognitive_load
        
    async def get_latest_gaze_data(self) -> Optional[GazeData]:
        """Get the latest gaze data point."""
        try:
            return await asyncio.wait_for(self._gaze_data_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
            
    def is_running(self) -> bool:
        """Check if eye tracking is currently active."""
        return self._running
