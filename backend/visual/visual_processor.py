"""Visual Stimulation Generator.

This module generates precisely-timed visual stimuli (like flashes or patterns)
that synchronize with the user's brain rhythms for enhanced neural entrainment.

Key Features:
    - Generates visual flicker patterns
    - Synchronizes with EEG rhythms
    - Creates specific frequency stimulation
    - Optimizes stimulus timing
"""

from dataclasses import dataclass
from typing import Dict
import numpy as np
from scipy import signal
import logging
import asyncio

@dataclass
class StimParams:
    """Parameters for visual stimulation."""
    gamma_freq: float = 40.0  # Fast flicker (40Hz)
    alpha_freq: float = 10.0  # Slower flicker (10Hz)
    min_brightness: float = 0.0
    max_brightness: float = 1.0

class VisualStimulator:
    """Generates visual stimulation patterns synchronized with brain rhythms."""
    
    def __init__(self, sampling_rate: int = 1000):
        """Initialize visual stimulator.
        
        Args:
            sampling_rate: Sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
        self.params = StimParams()
    
    def generate_flicker(self, duration: float) -> np.ndarray:
        """Generate visual flicker pattern.
        
        Args:
            duration: Pattern duration in seconds
            
        Returns:
            Brightness values over time (0-1)
        """
        # Generate time vector
        t = np.arange(0, duration, 1/self.sampling_rate)
        
        # Create gamma (40Hz) flicker
        gamma = np.sin(2 * np.pi * self.params.gamma_freq * t)
        
        # Create alpha (10Hz) modulation
        alpha = np.sin(2 * np.pi * self.params.alpha_freq * t)
        
        # Combine frequencies and scale to brightness
        pattern = (gamma * (1 + 0.5 * alpha) + 1) / 2  # Scale to 0-1
        pattern = pattern * (self.params.max_brightness - self.params.min_brightness) + self.params.min_brightness
        
        return pattern
        
    def sync_with_eeg(self, eeg_phase: float) -> float:
        """Calculate optimal flash timing based on EEG phase.
        
        Args:
            eeg_phase: Current EEG phase in radians
            
        Returns:
            When to show next flash (in seconds)
        """
        # Calculate phase difference
        phase_diff = np.mod(eeg_phase, 2*np.pi)
        
        # Convert to delay
        delay = phase_diff / (2*np.pi * self.params.gamma_freq)
        
        return delay
