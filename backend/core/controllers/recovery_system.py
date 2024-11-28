"""Recovery and Integration System.

This module optimizes post-flow recovery and enhances subsequent flow states
through adaptive cool-down protocols, neural plasticity optimization,
and comprehensive recovery tracking.

Key Features:
    - Post-flow cool-down protocols
    - Neural plasticity enhancement
    - Recovery metric tracking
    - Adaptive rest scheduling
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from biometric.whoop_client import WhoopClient
from hardware.strobe_glasses import StrobeGlasses
from flow.stability_system import FlowStateStabilitySystem

@dataclass
class RecoveryMetrics:
    """Container for recovery-related metrics."""
    cognitive_recovery: float  # Mental recovery score (0-1)
    neural_plasticity: float  # Estimated plasticity potential (0-1)
    rest_quality: float  # Quality of rest periods (0-1)
    recovery_rate: float  # Rate of recovery progress
    integration_score: float  # Learning integration measure (0-1)
    readiness_score: float  # Readiness for next flow session (0-1)

class RecoveryAndIntegrationSystem:
    """Optimizes recovery and integration of flow state benefits."""
    
    def __init__(self,
                 stability_system: FlowStateStabilitySystem,
                 whoop_client: WhoopClient,
                 strobe_glasses: StrobeGlasses):
        """Initialize the recovery system.
        
        Args:
            stability_system: Flow state stability tracker
            whoop_client: Biometric data interface
            strobe_glasses: Visual stimulation control
        """
        self.stability_system = stability_system
        self.whoop_client = whoop_client
        self.strobe_glasses = strobe_glasses
        
        # Configuration
        self.min_recovery_threshold = 0.7  # Minimum recovery before next session
        self.optimal_rest_duration = timedelta(minutes=20)  # Ideal rest period
        self.plasticity_window = timedelta(hours=2)  # Post-flow plasticity window
        
        # State tracking
        self.last_flow_end: Optional[datetime] = None
        self.recovery_history: List[float] = []
        self.session_durations: List[timedelta] = []
        self.integration_scores: List[float] = []
        
    async def compute_recovery_metrics(self) -> RecoveryMetrics:
        """Compute current recovery and integration metrics.
        
        Returns:
            RecoveryMetrics object with current values
        """
        # Get biometric data
        hrv_data = await self.whoop_client.get_hrv()
        recovery = await self.whoop_client.get_recovery()
        
        # Get stability metrics for context
        stability_metrics = await self.stability_system.compute_stability_metrics()
        
        # Compute cognitive recovery
        cognitive_recovery = self._compute_cognitive_recovery(
            recovery_score=recovery,
            stability_metrics=stability_metrics
        )
        
        # Estimate neural plasticity potential
        neural_plasticity = self._estimate_plasticity(
            time_since_flow=self._time_since_last_flow(),
            recovery_score=recovery
        )
        
        # Assess rest quality
        rest_quality = self._assess_rest_quality(
            hrv_data=hrv_data,
            recovery=recovery
        )
        
        # Calculate recovery rate
        recovery_rate = self._compute_recovery_rate()
        
        # Compute integration score
        integration_score = self._compute_integration_score(
            plasticity=neural_plasticity,
            rest_quality=rest_quality
        )
        
        # Calculate readiness for next session
        readiness_score = self._compute_readiness(
            cognitive_recovery=cognitive_recovery,
            rest_quality=rest_quality,
            recovery_rate=recovery_rate
        )
        
        return RecoveryMetrics(
            cognitive_recovery=cognitive_recovery,
            neural_plasticity=neural_plasticity,
            rest_quality=rest_quality,
            recovery_rate=recovery_rate,
            integration_score=integration_score,
            readiness_score=readiness_score
        )
        
    async def start_recovery_protocol(self):
        """Initiate post-flow recovery protocol."""
        self.last_flow_end = datetime.now()
        
        # Get current metrics
        metrics = await self.compute_recovery_metrics()
        
        # Start cool-down protocol
        await self._run_cooldown_protocol(metrics)
        
        # Begin recovery tracking
        self.recovery_history.append(metrics.cognitive_recovery)
        
    async def optimize_integration(self, eeg_phase: float):
        """Optimize neural plasticity and learning integration.
        
        Args:
            eeg_phase: Current EEG phase for synchronization
        """
        metrics = await self.compute_recovery_metrics()
        
        if metrics.neural_plasticity > 0.8:
            await self._enhance_plasticity(metrics, eeg_phase)
        else:
            await self._maintain_recovery(metrics, eeg_phase)
            
    def is_ready_for_flow(self) -> Tuple[bool, str]:
        """Check if user is ready for another flow session.
        
        Returns:
            Tuple of (ready: bool, reason: str)
        """
        if not self.recovery_history:
            return True, "No previous session data"
            
        latest_recovery = self.recovery_history[-1]
        time_since_flow = self._time_since_last_flow()
        
        if latest_recovery < self.min_recovery_threshold:
            return False, "Insufficient recovery"
            
        if time_since_flow < self.optimal_rest_duration:
            return False, "Rest period not complete"
            
        return True, "Ready for flow"
        
    def _compute_cognitive_recovery(self,
                                 recovery_score: float,
                                 stability_metrics) -> float:
        """Compute cognitive recovery score."""
        # Weight recovery score with stability context
        cognitive_recovery = (
            0.7 * recovery_score +
            0.3 * stability_metrics.recovery_capacity
        )
        
        return float(np.clip(cognitive_recovery, 0, 1))
        
    def _estimate_plasticity(self,
                          time_since_flow: Optional[timedelta],
                          recovery_score: float) -> float:
        """Estimate current neural plasticity potential."""
        if not time_since_flow:
            return 0.5
            
        # Plasticity peaks immediately after flow and gradually declines
        hours_since_flow = time_since_flow.total_seconds() / 3600
        time_factor = np.exp(-hours_since_flow / 2)  # 2-hour decay constant
        
        # Combine with recovery score
        plasticity = (0.7 * time_factor) + (0.3 * recovery_score)
        
        return float(np.clip(plasticity, 0, 1))
        
    def _assess_rest_quality(self,
                          hrv_data: np.ndarray,
                          recovery: float) -> float:
        """Assess quality of rest periods."""
        if len(hrv_data) < 2:
            return recovery  # Fall back to recovery score
            
        # Compute HRV stability as rest quality indicator
        hrv_stability = 1.0 - np.std(hrv_data) / np.mean(hrv_data)
        
        # Combine with recovery score
        rest_quality = (0.6 * hrv_stability) + (0.4 * recovery)
        
        return float(np.clip(rest_quality, 0, 1))
        
    def _compute_recovery_rate(self) -> float:
        """Compute rate of recovery progress."""
        if len(self.recovery_history) < 2:
            return 0.5
            
        # Calculate rate of change in recovery scores
        recent_rates = np.diff(self.recovery_history[-5:]) if len(self.recovery_history) >= 5 else np.diff(self.recovery_history)
        avg_rate = np.mean(recent_rates)
        
        # Normalize to 0-1 range
        norm_rate = 0.5 + (avg_rate * 5)  # Scale factor of 5 for sensitivity
        
        return float(np.clip(norm_rate, 0, 1))
        
    def _compute_integration_score(self,
                                plasticity: float,
                                rest_quality: float) -> float:
        """Compute learning integration score."""
        # Weight plasticity and rest quality
        integration = (0.7 * plasticity) + (0.3 * rest_quality)
        
        return float(np.clip(integration, 0, 1))
        
    def _compute_readiness(self,
                         cognitive_recovery: float,
                         rest_quality: float,
                         recovery_rate: float) -> float:
        """Compute readiness score for next flow session."""
        weights = {
            'recovery': 0.4,
            'rest': 0.3,
            'rate': 0.3
        }
        
        readiness = (
            weights['recovery'] * cognitive_recovery +
            weights['rest'] * rest_quality +
            weights['rate'] * recovery_rate
        )
        
        return float(np.clip(readiness, 0, 1))
        
    def _time_since_last_flow(self) -> Optional[timedelta]:
        """Calculate time since last flow session ended."""
        if not self.last_flow_end:
            return None
        return datetime.now() - self.last_flow_end
        
    async def _run_cooldown_protocol(self, metrics: RecoveryMetrics):
        """Run post-flow cool-down protocol."""
        # Use gentle alpha stimulation for relaxation
        await self.strobe_glasses.set_synchronized_pattern(
            frequencies=(10.0, 4.0),  # Alpha-theta for relaxation
            eeg_phase=0.0,  # Phase not critical during cooldown
            duration=0.5
        )
        
    async def _enhance_plasticity(self,
                               metrics: RecoveryMetrics,
                               eeg_phase: float):
        """Enhance neural plasticity during optimal window."""
        # Use theta-gamma coupling for plasticity enhancement
        await self.strobe_glasses.set_bilateral_strobing(
            left_freq=40.0,  # Gamma
            right_freq=6.0,  # Theta
            phase_diff=np.pi/3,
            intensity=0.7
        )
        
    async def _maintain_recovery(self,
                              metrics: RecoveryMetrics,
                              eeg_phase: float):
        """Maintain recovery state with minimal stimulation."""
        # Use gentle alpha stimulation
        await self.strobe_glasses.set_alternating_pattern(
            base_freq=10.0,  # Alpha
            alt_freq=4.0,   # Theta
            pattern_duration=1.0
        )
