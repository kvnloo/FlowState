"""Attention Density Maximizer.

This module optimizes attention and focus by analyzing eye tracking data,
detecting distractions, and dynamically adjusting stimulation parameters
to maximize attention density.

Key Features:
    - Real-time attention scoring
    - Distraction detection and elimination
    - Dynamic frequency modulation based on attention metrics
    - Integration with eye tracking and EEG data
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
from biometric.tobii_tracker import TobiiTracker
from visual.visual_processor import VisualStimulator
from hardware.strobe_glasses import StrobeGlasses

@dataclass
class AttentionMetrics:
    """Container for attention-related metrics."""
    fixation_duration: float  # Average fixation duration in seconds
    saccade_velocity: float  # Average saccade velocity in degrees/second
    pupil_diameter: float  # Normalized pupil diameter (0-1)
    blink_rate: float  # Blinks per minute
    attention_score: float  # Computed attention score (0-1)
    cognitive_load: float  # Estimated cognitive load (0-1)

class AttentionDensityMaximizer:
    """Optimizes attention density through multimodal feedback."""
    
    def __init__(self, 
                 eye_tracker: TobiiTracker,
                 visual_stim: VisualStimulator,
                 strobe_glasses: StrobeGlasses):
        """Initialize the attention maximizer.
        
        Args:
            eye_tracker: Tobii eye tracker instance
            visual_stim: Visual stimulator for pattern generation
            strobe_glasses: Strobe glasses hardware interface
        """
        self.eye_tracker = eye_tracker
        self.visual_stim = visual_stim
        self.strobe_glasses = strobe_glasses
        
        # Configuration parameters
        self.attention_threshold = 0.7  # Minimum attention score
        self.distraction_threshold = 0.3  # Maximum distraction tolerance
        self.adaptation_rate = 0.1  # Rate of parameter adjustment
        
        # State tracking
        self.baseline_attention: Optional[float] = None
        self.attention_history: List[float] = []
        self.distraction_zones: List[Tuple[float, float]] = []  # (x, y) coordinates
        
    async def compute_attention_metrics(self, window_size: float = 1.0) -> AttentionMetrics:
        """Compute attention metrics from eye tracking data.
        
        Args:
            window_size: Time window for metric computation in seconds
            
        Returns:
            AttentionMetrics object with computed values
        """
        # Get raw eye tracking data
        gaze_data = await self.eye_tracker.get_gaze_data(duration=window_size)
        
        # Extract basic metrics
        fixations = self._extract_fixations(gaze_data)
        saccades = self._extract_saccades(gaze_data)
        pupil_data = self._extract_pupil_data(gaze_data)
        blinks = self._extract_blinks(gaze_data)
        
        # Compute derived metrics
        fixation_duration = np.mean([f.duration for f in fixations])
        saccade_velocity = np.mean([s.velocity for s in saccades])
        pupil_diameter = np.mean(pupil_data) / self.eye_tracker.max_pupil_size
        blink_rate = len(blinks) * (60.0 / window_size)  # Convert to blinks/minute
        
        # Compute attention score using multiple factors
        attention_score = self._compute_attention_score(
            fixation_duration=fixation_duration,
            saccade_velocity=saccade_velocity,
            pupil_diameter=pupil_diameter,
            blink_rate=blink_rate
        )
        
        # Estimate cognitive load
        cognitive_load = self._estimate_cognitive_load(
            pupil_diameter=pupil_diameter,
            blink_rate=blink_rate,
            saccade_velocity=saccade_velocity
        )
        
        return AttentionMetrics(
            fixation_duration=fixation_duration,
            saccade_velocity=saccade_velocity,
            pupil_diameter=pupil_diameter,
            blink_rate=blink_rate,
            attention_score=attention_score,
            cognitive_load=cognitive_load
        )
        
    def _compute_attention_score(self,
                               fixation_duration: float,
                               saccade_velocity: float,
                               pupil_diameter: float,
                               blink_rate: float) -> float:
        """Compute overall attention score from individual metrics.
        
        Uses a weighted combination of metrics, normalized to 0-1 range.
        Longer fixations, moderate saccade velocity, larger pupils, and
        lower blink rates generally indicate higher attention.
        """
        # Normalize metrics to 0-1 range
        norm_fixation = np.clip(fixation_duration / 0.3, 0, 1)  # 300ms is typical
        norm_saccade = 1 - np.clip(saccade_velocity / 500, 0, 1)  # Lower is better
        norm_pupil = pupil_diameter  # Already normalized
        norm_blink = 1 - np.clip(blink_rate / 30, 0, 1)  # Lower is better
        
        # Weighted combination
        weights = {
            'fixation': 0.4,
            'saccade': 0.2,
            'pupil': 0.3,
            'blink': 0.1
        }
        
        attention_score = (
            weights['fixation'] * norm_fixation +
            weights['saccade'] * norm_saccade +
            weights['pupil'] * norm_pupil +
            weights['blink'] * norm_blink
        )
        
        return float(np.clip(attention_score, 0, 1))
        
    def _estimate_cognitive_load(self,
                               pupil_diameter: float,
                               blink_rate: float,
                               saccade_velocity: float) -> float:
        """Estimate cognitive load from eye metrics.
        
        Higher cognitive load typically correlates with:
        - Larger pupil diameter
        - Reduced blink rate
        - Increased saccade velocity
        """
        # Normalize and weight factors
        pupil_load = pupil_diameter  # Already normalized
        blink_load = 1 - np.clip(blink_rate / 30, 0, 1)  # Lower blink rate = higher load
        saccade_load = np.clip(saccade_velocity / 500, 0, 1)  # Higher velocity = higher load
        
        weights = {
            'pupil': 0.5,
            'blink': 0.2,
            'saccade': 0.3
        }
        
        cognitive_load = (
            weights['pupil'] * pupil_load +
            weights['blink'] * blink_load +
            weights['saccade'] * saccade_load
        )
        
        return float(np.clip(cognitive_load, 0, 1))
        
    async def optimize_stimulation(self, current_eeg_phase: float):
        """Optimize visual stimulation based on attention metrics.
        
        Args:
            current_eeg_phase: Current EEG phase for synchronization
        """
        # Get current attention metrics
        metrics = await self.compute_attention_metrics()
        
        # Update baseline if not set
        if self.baseline_attention is None:
            self.baseline_attention = metrics.attention_score
            
        # Adjust stimulation based on attention level
        if metrics.attention_score < self.attention_threshold:
            # Attention is low - increase stimulation
            await self._enhance_attention(metrics, current_eeg_phase)
        elif metrics.cognitive_load > 0.8:
            # Cognitive load too high - reduce stimulation
            await self._reduce_cognitive_load(metrics, current_eeg_phase)
        else:
            # Maintain current state with slight optimization
            await self._maintain_optimal_state(metrics, current_eeg_phase)
            
        # Update history
        self.attention_history.append(metrics.attention_score)
        
    async def _enhance_attention(self, 
                               metrics: AttentionMetrics, 
                               eeg_phase: float):
        """Enhance attention through targeted stimulation.
        
        Increases gamma-band stimulation and adjusts bilateral phase
        difference to enhance interhemispheric synchronization.
        """
        # Calculate optimal frequencies based on attention level
        attention_deficit = self.attention_threshold - metrics.attention_score
        gamma_freq = 40 + (attention_deficit * 10)  # Increase gamma for focus
        alpha_freq = 10 - (attention_deficit * 2)   # Decrease alpha for alertness
        
        # Set bilateral stimulation with phase difference
        phase_diff = np.pi / 4  # 45-degree phase shift for enhanced synchronization
        await self.strobe_glasses.set_bilateral_strobing(
            left_freq=gamma_freq,
            right_freq=gamma_freq,
            phase_diff=phase_diff,
            intensity=0.8
        )
        
    async def _reduce_cognitive_load(self, 
                                   metrics: AttentionMetrics, 
                                   eeg_phase: float):
        """Reduce cognitive load while maintaining attention.
        
        Shifts stimulation towards alpha-band to promote relaxed focus.
        """
        # Calculate load reduction
        load_excess = metrics.cognitive_load - 0.8
        alpha_freq = 10 + (load_excess * 2)  # Increase alpha for relaxation
        
        # Use alternating pattern with slower frequency
        await self.strobe_glasses.set_alternating_pattern(
            base_freq=alpha_freq,
            alt_freq=2.0,  # Slow alternation
            pattern_duration=1.0
        )
        
    async def _maintain_optimal_state(self, 
                                    metrics: AttentionMetrics, 
                                    eeg_phase: float):
        """Maintain optimal attention state with minimal adjustment.
        
        Uses current EEG phase for synchronized stimulation.
        """
        # Use current successful frequencies with slight optimization
        await self.strobe_glasses.set_synchronized_pattern(
            frequencies=(40.0, 10.0),  # Standard gamma-alpha coupling
            eeg_phase=eeg_phase,
            duration=0.1
        )
        
    def _extract_fixations(self, gaze_data: Dict) -> List[Dict]:
        """Extract fixation events from raw gaze data."""
        # Implementation depends on eye tracker data format
        return []  # TODO: Implement fixation detection
        
    def _extract_saccades(self, gaze_data: Dict) -> List[Dict]:
        """Extract saccade events from raw gaze data."""
        # Implementation depends on eye tracker data format
        return []  # TODO: Implement saccade detection
        
    def _extract_pupil_data(self, gaze_data: Dict) -> np.ndarray:
        """Extract pupil diameter data."""
        # Implementation depends on eye tracker data format
        return np.array([])  # TODO: Implement pupil data extraction
        
    def _extract_blinks(self, gaze_data: Dict) -> List[Dict]:
        """Extract blink events from raw gaze data."""
        # Implementation depends on eye tracker data format
        return []  # TODO: Implement blink detection
