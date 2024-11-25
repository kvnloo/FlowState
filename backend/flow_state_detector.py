"""Flow State Detection and Optimization Module.

This module integrates advanced algorithms for detecting and optimizing flow states using
EEG data, binaural beats, and cognitive state detection. It builds upon the Deep-BCI
algorithms for enhanced accuracy and real-time processing.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from scipy import signal
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import logging
from enum import IntEnum

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
    """Metrics describing the current flow state."""
    flow_level: FlowState
    confidence: float
    challenge_skill_balance: float
    cognitive_load: float
    attention_level: float
    recommendations: List[str]

class FlowStateDetector:
    """Detects and analyzes flow states using advanced EEG processing."""

    def __init__(self, eeg_processor: EEGProcessor):
        """Initialize the flow state detector.
        
        Args:
            eeg_processor: Instance of EEGProcessor for raw data
        """
        self.eeg = eeg_processor
        self.scaler = StandardScaler()
        self._setup_logging()
        self._init_models()

    def _setup_logging(self):
        """Configure logging for the detector."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _init_models(self):
        """Initialize neural networks and processing models."""
        # Simple CNN for ERP detection
        self.erp_model = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Flatten(),
            nn.Linear(32 * 61, 64),
            nn.ReLU(),
            nn.Linear(64, len(FlowState))
        )

    def extract_features(self, band_powers: BandPowers) -> FlowFeatures:
        """Extract relevant features for flow state detection.
        
        Args:
            band_powers: Current band power measurements
            
        Returns:
            FlowFeatures object containing extracted features
        """
        # Calculate band power ratios
        alpha_theta = band_powers.alpha / band_powers.theta if band_powers.theta > 0 else 0
        theta_beta = band_powers.theta / band_powers.beta if band_powers.beta > 0 else 0
        alpha_beta = band_powers.alpha / band_powers.beta if band_powers.beta > 0 else 0
        
        # Get channel data for asymmetry calculation
        channels = self.eeg.get_channel_quality()
        left_alpha = channels.get(1, 0)  # Left frontal
        right_alpha = channels.get(2, 0)  # Right frontal
        
        # Calculate frontal alpha asymmetry
        asymmetry = (right_alpha - left_alpha) / (right_alpha + left_alpha) if (right_alpha + left_alpha) > 0 else 0
        
        # Detect gamma bursts
        gamma_bursts = self._detect_gamma_bursts(band_powers.gamma)
        
        # Calculate alpha coherence
        alpha_coherence = self._calculate_alpha_coherence()
        
        return FlowFeatures(
            alpha_theta_ratio=alpha_theta,
            theta_beta_ratio=theta_beta,
            alpha_beta_ratio=alpha_beta,
            frontal_midline_theta=band_powers.theta,
            frontal_alpha_asymmetry=asymmetry,
            beta_suppression=1 - (band_powers.beta / (band_powers.alpha + band_powers.theta)) 
                if (band_powers.alpha + band_powers.theta) > 0 else 0,
            gamma_bursts=gamma_bursts,
            alpha_coherence=alpha_coherence
        )

    def _detect_gamma_bursts(self, gamma_power: float) -> float:
        """Detect and quantify gamma burst activity.
        
        Args:
            gamma_power: Current gamma band power
            
        Returns:
            Normalized gamma burst score (0-1)
        """
        # Implementation based on Deep-BCI's cognitive state detection
        threshold = 2.5  # Standard deviations above mean
        if not hasattr(self, '_gamma_baseline'):
            self._gamma_baseline = []
            self._gamma_std = 1.0
            
        self._gamma_baseline.append(gamma_power)
        if len(self._gamma_baseline) > 100:  # Rolling window
            self._gamma_baseline.pop(0)
            self._gamma_std = np.std(self._gamma_baseline)
            
        if len(self._gamma_baseline) > 10:  # Need minimum samples
            z_score = (gamma_power - np.mean(self._gamma_baseline)) / self._gamma_std
            return float(max(0, min(1, (z_score - threshold) / threshold if z_score > threshold else 0)))
        return 0.0

    def _calculate_alpha_coherence(self) -> float:
        """Calculate alpha coherence between relevant channels.
        
        Returns:
            Coherence score (0-1)
        """
        if not self.eeg.buffers or not self.eeg.buffers[0]:
            return 0.0
            
        try:
            # Get latest data from frontal channels
            ch1_data = self.eeg.buffers[0][0][-256:]  # 1 second at 256 Hz
            ch2_data = self.eeg.buffers[0][1][-256:]
            
            # Calculate coherence in alpha band (8-13 Hz)
            f, coh = signal.coherence(ch1_data, ch2_data, fs=256, nperseg=256)
            alpha_mask = (f >= 8) & (f <= 13)
            return float(np.mean(coh[alpha_mask]))
            
        except Exception as e:
            self.logger.warning(f"Error calculating alpha coherence: {str(e)}")
            return 0.0

    def analyze_flow_state(self, features: FlowFeatures) -> FlowMetrics:
        """Analyze the current flow state based on extracted features.
        
        Args:
            features: Extracted EEG features
            
        Returns:
            FlowMetrics object containing analysis results
        """
        # Prepare feature vector
        feature_vector = np.array([
            features.alpha_theta_ratio,
            features.theta_beta_ratio,
            features.alpha_beta_ratio,
            features.frontal_midline_theta,
            features.frontal_alpha_asymmetry,
            features.beta_suppression,
            features.gamma_bursts,
            features.alpha_coherence
        ]).reshape(1, -1)
        
        # Normalize features
        if not hasattr(self, '_feature_history'):
            self._feature_history = []
        self._feature_history.append(feature_vector)
        if len(self._feature_history) > 100:
            self._feature_history.pop(0)
        
        # Determine flow state
        flow_state = self._determine_flow_state(feature_vector)
        confidence = self._calculate_confidence(feature_vector)
        
        # Calculate metrics
        challenge_skill = self._estimate_challenge_skill_balance(features)
        cognitive_load = self._estimate_cognitive_load(features)
        attention = self._estimate_attention_level(features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            flow_state, 
            challenge_skill,
            cognitive_load,
            attention
        )
        
        return FlowMetrics(
            flow_level=flow_state,
            confidence=confidence,
            challenge_skill_balance=challenge_skill,
            cognitive_load=cognitive_load,
            attention_level=attention,
            recommendations=recommendations
        )

    def _determine_flow_state(self, features: np.ndarray) -> FlowState:
        """Determine the current flow state based on features.
        
        Args:
            features: Normalized feature vector
            
        Returns:
            Detected FlowState
        """
        # Convert to PyTorch tensor
        with torch.no_grad():
            x = torch.FloatTensor(features).reshape(1, 1, -1)
            outputs = self.erp_model(x)
            state = int(outputs.argmax(dim=1))
            return FlowState(state)

    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence in the flow state detection.
        
        Args:
            features: Feature vector
            
        Returns:
            Confidence score (0-1)
        """
        if len(self._feature_history) < 10:
            return 0.5
            
        # Calculate feature stability
        feature_std = np.std(self._feature_history, axis=0)
        stability = np.mean(1 / (1 + feature_std))
        
        # Calculate feature coherence
        coherence = features[0, -1]  # Alpha coherence
        
        return float(np.clip((stability + coherence) / 2, 0, 1))

    def _estimate_challenge_skill_balance(self, features: FlowFeatures) -> float:
        """Estimate the balance between challenge and skill level.
        
        Args:
            features: Extracted features
            
        Returns:
            Balance score (-1 to 1, where 0 is perfect balance)
        """
        # High beta/theta ratio indicates high challenge
        challenge = features.beta_suppression
        
        # High alpha/theta ratio indicates high skill
        skill = features.alpha_theta_ratio
        
        # Normalize to -1 to 1 range
        return float(np.clip((challenge - skill) / max(challenge + skill, 1e-6), -1, 1))

    def _estimate_cognitive_load(self, features: FlowFeatures) -> float:
        """Estimate current cognitive load.
        
        Args:
            features: Extracted features
            
        Returns:
            Cognitive load score (0-1)
        """
        # Combine multiple indicators
        load_indicators = [
            features.frontal_midline_theta,  # Higher theta = higher load
            1 - features.alpha_beta_ratio,   # Lower alpha/beta = higher load
            1 - features.beta_suppression    # Lower beta suppression = higher load
        ]
        return float(np.mean(load_indicators))

    def _estimate_attention_level(self, features: FlowFeatures) -> float:
        """Estimate current attention level.
        
        Args:
            features: Extracted features
            
        Returns:
            Attention level score (0-1)
        """
        # Combine attention indicators
        attention_indicators = [
            features.beta_suppression,       # Higher suppression = better focus
            features.alpha_coherence,        # Higher coherence = better attention
            features.gamma_bursts,           # Gamma bursts indicate high attention
            abs(features.frontal_alpha_asymmetry)  # Asymmetry indicates engagement
        ]
        return float(np.mean(attention_indicators))

    def _generate_recommendations(
        self,
        flow_state: FlowState,
        challenge_skill: float,
        cognitive_load: float,
        attention: float
    ) -> List[str]:
        """Generate recommendations for optimizing flow state.
        
        Args:
            flow_state: Current flow state
            challenge_skill: Challenge-skill balance (-1 to 1)
            cognitive_load: Cognitive load level (0-1)
            attention: Attention level (0-1)
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if flow_state == FlowState.ANXIETY:
            if cognitive_load > 0.7:
                recommendations.append("Cognitive load is high. Try breaking the task into smaller steps.")
            recommendations.append("Challenge level may be too high. Consider reducing complexity.")
            
        elif flow_state == FlowState.BOREDOM:
            if attention < 0.3:
                recommendations.append("Attention level is low. Try increasing task complexity.")
            recommendations.append("Challenge level may be too low. Consider adding complexity.")
            
        elif flow_state == FlowState.FLOW:
            recommendations.append("Maintain current engagement level.")
            if cognitive_load > 0.8:
                recommendations.append("Watch cognitive load - take breaks if needed.")
                
        elif flow_state == FlowState.DEEP_FLOW:
            recommendations.append("Optimal state achieved. Maintain current conditions.")
            
        # Add binaural beat recommendations
        if attention < 0.5:
            recommendations.append("Consider alpha-theta binaural beats (8-10 Hz) to improve focus.")
        elif cognitive_load > 0.7:
            recommendations.append("Try alpha binaural beats (10-12 Hz) to reduce cognitive load.")
            
        return recommendations
