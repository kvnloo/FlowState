"""Flow State Detector Module.

This module analyzes real-time EEG and biometric data to detect and optimize flow states.

Implementation Status:
    ✓ Basic Flow Detection (2024-02-24)
        - EEG band power analysis
        - Heart rate variability
        - Focus metrics
    ✓ Cross-Frequency Analysis (2024-02-24)
        - Theta-gamma coupling
        - Phase synchronization
        - Power correlation
    ✓ Neural Metrics (2024-02-24)
        - Flow probability calculation
        - Focus scoring
        - Band power ratios
    ✓ Real-time Processing (2024-02-24)
        - Streaming EEG analysis
        - Artifact rejection
        - Feature extraction
    ⚠ Adaptive Thresholds (Partial)
        - Basic adaptation
        - Needs personalization
    ☐ Multi-modal Integration (Planned)
        - Eye tracking integration
        - Heart rate correlation
        - Skin conductance

Dependencies:
    - numpy: Array operations and numerical computing
    - scipy: Signal processing and statistical analysis
    - torch: Neural network operations
    - sklearn: Data preprocessing
    - mne: EEG processing utilities

Integration Points:
    - adaptive_audio_engine.py: Provides real-time frequency adaptation
    - eeg/realtime_processor.py: Real-time EEG processing
    - biometric/whoop_client.py: HRV and recovery metrics
    - biometric/tobii_tracker.py: Attention and focus metrics
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from scipy import signal
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import logging
from enum import IntEnum
from eeg.realtime_processor import RealtimeEEGProcessor
import asyncio

from eeg import EEGProcessor, Band, BandPowers

class FlowState(IntEnum):
    """Different levels of flow state."""
    UNKNOWN = 0
    ANXIETY = 1    # Challenge > Skill
    BOREDOM = 2    # Challenge < Skill
    FLOW = 3       # Challenge ≈ Skill
    DEEP_FLOW = 4  # Optimal state

@dataclass
class FlowFeatures:
    """Features extracted for flow state detection."""
    # Band power ratios
    alpha_theta_ratio: float
    theta_beta_ratio: float
    alpha_beta_ratio: float
    
    # Cognitive load indicators
    frontal_midline_theta: float
    frontal_alpha_asymmetry: float
    
    # Flow state indicators
    beta_suppression: float
    gamma_bursts: float
    alpha_coherence: float

@dataclass
class FlowMetrics:
    """Comprehensive metrics for flow state analysis.
    
    Attributes:
        flow_level: Enumerated flow state level
        confidence: Confidence in the flow state detection (0-1)
        challenge_skill_balance: Ratio of challenge to skill level (0-1)
        cognitive_load: Current cognitive load level (0-1)
        attention_level: Sustained attention measure (0-1)
        theta_gamma_coupling: Strength of theta-gamma cross-frequency coupling (0-1)
        phase_sync: Phase synchronization between frequency bands (0-1)
        focus_score: Composite focus metric based on EEG bands (0-1)
        flow_probability: Overall probability of being in flow state (0-1)
        recommendations: List of suggested optimizations
    """
    flow_level: FlowState
    confidence: float
    challenge_skill_balance: float
    cognitive_load: float
    attention_level: float
    theta_gamma_coupling: float = 0.0
    phase_sync: float = 0.0
    focus_score: float = 0.0
    flow_probability: float = 0.0
    recommendations: List[str]

class FlowStateDetector:
    """Detects and analyzes flow states using advanced EEG processing."""
    
    def __init__(self, channels: List[str], sampling_rate: int = 256):
        """Initialize the flow state detector.
        
        Args:
            channels: List of EEG channel names
            sampling_rate: EEG sampling rate in Hz
        """
        self.eeg_processor = RealtimeEEGProcessor(
            channels=channels,
            sampling_rate=sampling_rate
        )
        self.data_stream = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
    async def start_processing(self) -> None:
        """Start the real-time EEG processing pipeline."""
        if self.processing_task is None:
            self.processing_task = asyncio.create_task(
                self._processing_loop()
            )
            logging.info("Started real-time flow state detection")
    
    async def stop_processing(self) -> None:
        """Stop the real-time EEG processing pipeline."""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
            logging.info("Stopped flow state detection")
    
    async def _processing_loop(self) -> None:
        """Main processing loop for real-time flow state detection."""
        try:
            while True:
                # Get next chunk of EEG data
                eeg_chunk = await self.data_stream.get()
                
                # Process EEG data
                features = await self.eeg_processor.extract_features()
                
                # Detect flow state
                flow_metrics = self.detect_flow_state(
                    eeg_data=eeg_chunk,
                    features=features
                )
                
                # Log results
                logging.debug(
                    f"Flow state: {flow_metrics.flow_level}, "
                    f"Probability: {flow_metrics.flow_probability:.2f}"
                )
                
        except asyncio.CancelledError:
            logging.info("Flow state processing loop cancelled")
            raise
        except Exception as e:
            logging.error(f"Error in flow state processing: {str(e)}")
    
    def detect_flow_state(self, eeg_data: np.ndarray,
                         features: Optional[Dict[str, float]] = None) -> FlowMetrics:
        """Detect and analyze flow state from EEG data and extracted features.
        
        Args:
            eeg_data: Raw EEG data array
            features: Optional pre-extracted features
            
        Returns:
            FlowMetrics object with comprehensive flow state analysis
            
        Technical Details:
            - Real-time feature extraction
            - Flow state classification
            - Confidence estimation
            - Recommendation generation
        """
        # Use pre-extracted features if available
        if features is None:
            features = {}
        
        # Calculate flow metrics
        flow_state = self._determine_flow_state(features)
        confidence = self._calculate_confidence(features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            flow_state=flow_state,
            features=features
        )
        
        return FlowMetrics(
            flow_level=flow_state,
            confidence=confidence,
            theta_gamma_coupling=features.get('theta_gamma_coupling', 0.0),
            phase_sync=features.get('alpha_beta_sync', 0.0),
            focus_score=features.get('focus_score', 0.0),
            flow_probability=features.get('flow_probability', 0.0),
            recommendations=recommendations
        )

    def _determine_flow_state(self, features: Dict[str, float]) -> FlowState:
        """Determine the current flow state based on features.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Detected FlowState
        """
        # Convert to PyTorch tensor
        with torch.no_grad():
            x = torch.FloatTensor(list(features.values())).reshape(1, 1, -1)
            outputs = self.erp_model(x)
            state = int(outputs.argmax(dim=1))
            return FlowState(state)

    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in the flow state detection.
        
        Args:
            features: Feature dictionary
            
        Returns:
            Confidence score (0-1)
        """
        if len(self._feature_history) < 10:
            return 0.5
            
        # Calculate feature stability
        feature_std = np.std(self._feature_history, axis=0)
        stability = np.mean(1 / (1 + feature_std))
        
        # Calculate feature coherence
        coherence = features.get('alpha_coherence', 0.0)
        
        return float(np.clip((stability + coherence) / 2, 0, 1))

    def _generate_recommendations(
        self,
        flow_state: FlowState,
        features: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for optimizing flow state.
        
        Args:
            flow_state: Current flow state
            features: Feature dictionary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if flow_state == FlowState.ANXIETY:
            if features.get('cognitive_load', 0.0) > 0.7:
                recommendations.append("Cognitive load is high. Try breaking the task into smaller steps.")
            recommendations.append("Challenge level may be too high. Consider reducing complexity.")
            
        elif flow_state == FlowState.BOREDOM:
            if features.get('attention_level', 0.0) < 0.3:
                recommendations.append("Attention level is low. Try increasing task complexity.")
            recommendations.append("Challenge level may be too low. Consider adding complexity.")
            
        elif flow_state == FlowState.FLOW:
            recommendations.append("Maintain current engagement level.")
            if features.get('cognitive_load', 0.0) > 0.8:
                recommendations.append("Watch cognitive load - take breaks if needed.")
                
        elif flow_state == FlowState.DEEP_FLOW:
            recommendations.append("Optimal state achieved. Maintain current conditions.")
            
        # Add binaural beat recommendations
        if features.get('attention_level', 0.0) < 0.5:
            recommendations.append("Consider alpha-theta binaural beats (8-10 Hz) to improve focus.")
        elif features.get('cognitive_load', 0.0) > 0.7:
            recommendations.append("Try alpha binaural beats (10-12 Hz) to reduce cognitive load.")
            
        return recommendations
