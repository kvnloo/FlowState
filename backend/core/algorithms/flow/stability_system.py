"""Flow State Stability System.

This module maintains optimal flow states through continuous neurological
feedback, adaptive environmental controls, and progressive challenge scaling.

Key Features:
    - Real-time flow state monitoring
    - Dynamic stability maintenance
    - Progressive challenge adaptation
    - Environmental optimization
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
from biometric.tobii_tracker import TobiiTracker
from biometric.whoop_client import WhoopClient
from hardware.strobe_glasses import StrobeGlasses
from attention.attention_maximizer import AttentionDensityMaximizer

@dataclass
class StabilityMetrics:
    """Container for flow stability metrics."""
    flow_depth: float  # Current depth of flow state (0-1)
    stability_score: float  # Overall stability measure (0-1)
    challenge_level: float  # Current challenge level (0-1)
    adaptation_rate: float  # Rate of parameter adaptation
    environmental_quality: float  # Environmental conditions score (0-1)
    recovery_capacity: float  # Remaining cognitive resources (0-1)

class FlowStateStabilitySystem:
    """Maintains and deepens flow states through adaptive optimization."""
    
    def __init__(self,
                 attention_maximizer: AttentionDensityMaximizer,
                 whoop_client: WhoopClient,
                 strobe_glasses: StrobeGlasses):
        """Initialize the stability system.
        
        Args:
            attention_maximizer: Attention optimization system
            whoop_client: Biometric data interface
            strobe_glasses: Visual stimulation control
        """
        self.attention_maximizer = attention_maximizer
        self.whoop_client = whoop_client
        self.strobe_glasses = strobe_glasses
        
        # Configuration
        self.stability_threshold = 0.8  # Minimum stability score
        self.adaptation_rate = 0.05  # Base rate of parameter changes
        self.challenge_increment = 0.1  # Step size for challenge increases
        
        # State tracking
        self.flow_history: List[float] = []
        self.challenge_history: List[float] = []
        self.current_challenge = 0.5  # Start at moderate challenge
        
    async def compute_stability_metrics(self) -> StabilityMetrics:
        """Compute current flow state stability metrics.
        
        Returns:
            StabilityMetrics object with current values
        """
        # Get biometric data
        hrv_data = await self.whoop_client.get_hrv()
        recovery = await self.whoop_client.get_recovery()
        
        # Get attention metrics
        attention_metrics = await self.attention_maximizer.compute_attention_metrics()
        
        # Compute flow depth from multiple indicators
        flow_depth = self._compute_flow_depth(
            attention_score=attention_metrics.attention_score,
            cognitive_load=attention_metrics.cognitive_load,
            hrv_coherence=self._compute_hrv_coherence(hrv_data)
        )
        
        # Compute stability score
        stability_score = self._compute_stability_score(
            flow_depth=flow_depth,
            attention_stability=self._compute_attention_stability(attention_metrics),
            physiological_stability=self._compute_physiological_stability(hrv_data)
        )
        
        # Assess environmental quality
        environmental_quality = self._assess_environment(
            attention_metrics=attention_metrics
        )
        
        # Calculate recovery capacity
        recovery_capacity = self._compute_recovery_capacity(
            recovery_score=recovery,
            cognitive_load=attention_metrics.cognitive_load
        )
        
        return StabilityMetrics(
            flow_depth=flow_depth,
            stability_score=stability_score,
            challenge_level=self.current_challenge,
            adaptation_rate=self.adaptation_rate,
            environmental_quality=environmental_quality,
            recovery_capacity=recovery_capacity
        )
        
    async def maintain_stability(self, eeg_phase: float):
        """Maintain flow state stability through adaptive optimization.
        
        Args:
            eeg_phase: Current EEG phase for synchronization
        """
        # Get current metrics
        metrics = await self.compute_stability_metrics()
        
        # Update history
        self.flow_history.append(metrics.flow_depth)
        self.challenge_history.append(metrics.challenge_level)
        
        # Adjust parameters based on stability
        if metrics.stability_score < self.stability_threshold:
            await self._stabilize_state(metrics, eeg_phase)
        elif metrics.recovery_capacity > 0.7:
            await self._deepen_flow(metrics, eeg_phase)
        else:
            await self._maintain_state(metrics, eeg_phase)
            
    def _compute_flow_depth(self,
                          attention_score: float,
                          cognitive_load: float,
                          hrv_coherence: float) -> float:
        """Compute current depth of flow state from multiple indicators."""
        # Optimal cognitive load is around 0.7-0.8
        load_optimality = 1.0 - abs(0.75 - cognitive_load) * 2
        
        # Weight and combine factors
        weights = {
            'attention': 0.4,
            'load': 0.3,
            'hrv': 0.3
        }
        
        flow_depth = (
            weights['attention'] * attention_score +
            weights['load'] * load_optimality +
            weights['hrv'] * hrv_coherence
        )
        
        return float(np.clip(flow_depth, 0, 1))
        
    def _compute_stability_score(self,
                               flow_depth: float,
                               attention_stability: float,
                               physiological_stability: float) -> float:
        """Compute overall stability score from multiple factors."""
        weights = {
            'flow': 0.4,
            'attention': 0.3,
            'physiological': 0.3
        }
        
        stability = (
            weights['flow'] * flow_depth +
            weights['attention'] * attention_stability +
            weights['physiological'] * physiological_stability
        )
        
        return float(np.clip(stability, 0, 1))
        
    def _compute_attention_stability(self, metrics) -> float:
        """Compute stability of attention metrics over time."""
        if len(self.flow_history) < 2:
            return 1.0
            
        # Calculate variance in recent attention scores
        recent_variance = np.var(self.flow_history[-10:]) if len(self.flow_history) >= 10 else 0
        stability = 1.0 - recent_variance
        
        return float(np.clip(stability, 0, 1))
        
    def _compute_physiological_stability(self, hrv_data: np.ndarray) -> float:
        """Compute stability of physiological metrics."""
        if len(hrv_data) < 2:
            return 1.0
            
        # Calculate HRV stability
        hrv_stability = 1.0 - np.std(hrv_data) / np.mean(hrv_data)
        
        return float(np.clip(hrv_stability, 0, 1))
        
    def _compute_hrv_coherence(self, hrv_data: np.ndarray) -> float:
        """Compute HRV coherence score."""
        if len(hrv_data) < 2:
            return 0.5
            
        # Simplified coherence calculation
        # In practice, this would use more sophisticated frequency analysis
        coherence = 1.0 - np.std(hrv_data) / np.mean(hrv_data)
        
        return float(np.clip(coherence, 0, 1))
        
    def _assess_environment(self, attention_metrics) -> float:
        """Assess quality of environmental conditions."""
        # Use attention metrics as proxy for environmental quality
        # In practice, would incorporate actual environmental sensors
        environmental_score = attention_metrics.attention_score
        
        return float(np.clip(environmental_score, 0, 1))
        
    def _compute_recovery_capacity(self,
                                recovery_score: float,
                                cognitive_load: float) -> float:
        """Compute remaining cognitive recovery capacity."""
        # Combine recovery score with inverse of cognitive load
        capacity = (recovery_score * 0.7) + ((1 - cognitive_load) * 0.3)
        
        return float(np.clip(capacity, 0, 1))
        
    async def _stabilize_state(self,
                             metrics: StabilityMetrics,
                             eeg_phase: float):
        """Stabilize flow state when stability is low."""
        # Reduce challenge level
        self.current_challenge = max(0.3, self.current_challenge - self.challenge_increment)
        
        # Adjust visual stimulation
        await self.strobe_glasses.set_synchronized_pattern(
            frequencies=(30.0, 8.0),  # Lower frequencies for stability
            eeg_phase=eeg_phase,
            duration=0.2
        )
        
    async def _deepen_flow(self,
                         metrics: StabilityMetrics,
                         eeg_phase: float):
        """Deepen flow state when stability is high and recovery capacity allows."""
        # Increase challenge level
        self.current_challenge = min(0.9, self.current_challenge + self.challenge_increment)
        
        # Enhance stimulation
        await self.strobe_glasses.set_bilateral_strobing(
            left_freq=40.0,  # High gamma for enhanced focus
            right_freq=40.0,
            phase_diff=np.pi/4,
            intensity=0.9
        )
        
    async def _maintain_state(self,
                           metrics: StabilityMetrics,
                           eeg_phase: float):
        """Maintain current flow state with minimal adjustments."""
        # Keep current challenge level
        # Use alternating pattern for sustained engagement
        await self.strobe_glasses.set_alternating_pattern(
            base_freq=35.0,  # Moderate gamma
            alt_freq=8.0,    # Alpha for stability
            pattern_duration=0.5
        )
