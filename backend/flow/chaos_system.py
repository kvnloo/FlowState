"""Chaos System for Neural Entrainment.

This module introduces controlled chaos into various stimulation parameters
to explore novel neural entrainment patterns. It uses various chaos/randomness
algorithms that can be tuned via a global chaos level setting.

Features:
    - Global chaos level control
    - Parameter-specific chaos injection
    - Safe bounds enforcement
    - Pattern emergence detection
    - Effectiveness tracking
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random
from scipy import signal
from datetime import datetime

@dataclass
class ChaosConfig:
    """Configuration for chaos injection."""
    base_value: float
    min_value: float
    max_value: float
    volatility: float  # How much the value can change per step
    pattern_length: int  # Length of pattern before potential change
    mutation_rate: float  # Probability of pattern mutation

@dataclass
class EffectivePattern:
    """Record of patterns that produced interesting results."""
    pattern: np.ndarray
    eeg_effect: Dict[str, float]
    timestamp: datetime
    score: float

class ChaosSystem:
    """Manages chaos injection across the system."""
    
    def __init__(self, 
                 global_chaos: float = 0.0,
                 seed: Optional[int] = None):
        """Initialize the chaos system.
        
        Args:
            global_chaos: Global chaos level (0.0 - 1.0)
            seed: Random seed for reproducibility
        """
        self.global_chaos = global_chaos
        self.rng = np.random.default_rng(seed)
        
        # Store effective patterns for future use
        self.effective_patterns: List[EffectivePattern] = []
        
        # Initialize chaos generators
        self._init_chaos_generators()
        
    def _init_chaos_generators(self):
        """Initialize various chaos generation methods."""
        self.generators = {
            'logistic': lambda x, r: r * x * (1 - x),
            'henon': lambda x, y, a=1.4, b=0.3: (1 - a*x*x + y, b*x),
            'lorenz': lambda x, y, z, s=10, r=28, b=2.667:
                (s*(y - x), x*(r - z) - y, x*y - b*z)
        }
        
        # Current state for each generator
        self.generator_states = {
            'logistic': self.rng.random(),
            'henon': (self.rng.random(), self.rng.random()),
            'lorenz': (self.rng.random(), self.rng.random(), self.rng.random())
        }
        
    def set_global_chaos(self, level: float):
        """Set global chaos level (0.0 - 1.0)."""
        self.global_chaos = np.clip(level, 0.0, 1.0)
        
    def get_strobe_pattern(self, 
                          base_freq: float,
                          duration_ms: int,
                          config: ChaosConfig) -> np.ndarray:
        """Generate chaotic strobe pattern.
        
        Args:
            base_freq: Base frequency in Hz
            duration_ms: Duration in milliseconds
            config: Chaos configuration for this parameter
            
        Returns:
            Array of strobe timings with chaos injected
        """
        # Calculate number of strobes
        num_strobes = int(base_freq * duration_ms / 1000)
        
        if self.global_chaos < 0.01:
            # Almost no chaos - return regular pattern
            return np.linspace(0, duration_ms, num_strobes)
            
        # Generate chaotic sequence
        chaos_seq = self._generate_chaos_sequence(num_strobes)
        
        # Apply chaos to strobe timings
        strobe_times = np.zeros(num_strobes)
        current_time = 0
        
        for i in range(num_strobes):
            # Add chaotic jitter to timing
            jitter = chaos_seq[i] * config.volatility * self.global_chaos
            interval = (1000 / base_freq) * (1 + jitter)
            
            # Ensure timing stays within bounds
            interval = np.clip(interval, 
                             1000 / config.max_value,
                             1000 / config.min_value)
            
            current_time += interval
            strobe_times[i] = current_time
            
        return strobe_times
        
    def get_binaural_frequencies(self,
                               base_freq: float,
                               duration_ms: int,
                               config: ChaosConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Generate chaotic binaural beat frequencies.
        
        Args:
            base_freq: Base frequency in Hz
            duration_ms: Duration in milliseconds
            config: Chaos configuration for this parameter
            
        Returns:
            Tuple of (left_ear_freq, right_ear_freq) arrays
        """
        num_samples = int(duration_ms * 44.1)  # 44.1 kHz sampling
        
        if self.global_chaos < 0.01:
            # Regular binaural beats
            left_freq = np.ones(num_samples) * base_freq
            right_freq = np.ones(num_samples) * (base_freq + 40)  # 40 Hz difference
            return left_freq, right_freq
            
        # Generate chaotic frequency modulation
        chaos_seq = self._generate_chaos_sequence(num_samples)
        
        # Apply chaos to frequencies
        freq_mod = chaos_seq * config.volatility * self.global_chaos
        
        left_freq = base_freq * (1 + freq_mod)
        right_freq = (base_freq + 40) * (1 + freq_mod)  # Maintain 40 Hz difference
        
        # Ensure frequencies stay within bounds
        left_freq = np.clip(left_freq, config.min_value, config.max_value)
        right_freq = np.clip(right_freq, config.min_value, config.max_value)
        
        return left_freq, right_freq
        
    def get_duty_cycle(self,
                      base_duty: float,
                      config: ChaosConfig) -> float:
        """Generate chaotic duty cycle.
        
        Args:
            base_duty: Base duty cycle (0.0 - 1.0)
            config: Chaos configuration for this parameter
            
        Returns:
            Modified duty cycle
        """
        if self.global_chaos < 0.01:
            return base_duty
            
        # Generate single chaos value
        chaos_val = self._get_next_chaos_value()
        
        # Apply chaos to duty cycle
        duty = base_duty + (chaos_val - 0.5) * config.volatility * self.global_chaos
        
        # Ensure duty cycle stays within bounds
        return np.clip(duty, config.min_value, config.max_value)
        
    def record_effective_pattern(self,
                               pattern: np.ndarray,
                               eeg_data: Dict[str, float],
                               score: float):
        """Record patterns that produced interesting results.
        
        Args:
            pattern: The pattern that was used
            eeg_data: Resulting EEG measurements
            score: Effectiveness score (0.0 - 1.0)
        """
        if score > 0.7:  # Only store notably effective patterns
            self.effective_patterns.append(EffectivePattern(
                pattern=pattern,
                eeg_effect=eeg_data,
                timestamp=datetime.now(),
                score=score
            ))
            
            # Keep only top 100 patterns
            if len(self.effective_patterns) > 100:
                self.effective_patterns.sort(key=lambda x: x.score, reverse=True)
                self.effective_patterns = self.effective_patterns[:100]
                
    def _generate_chaos_sequence(self, length: int) -> np.ndarray:
        """Generate sequence of chaos values.
        
        Args:
            length: Length of sequence to generate
            
        Returns:
            Array of chaos values between 0 and 1
        """
        # Randomly select a chaos generator
        generator_type = random.choice(list(self.generators.keys()))
        
        sequence = np.zeros(length)
        
        if generator_type == 'logistic':
            x = self.generator_states['logistic']
            r = 3.9  # Chaos parameter
            
            for i in range(length):
                x = self.generators['logistic'](x, r)
                sequence[i] = x
                
            self.generator_states['logistic'] = x
            
        elif generator_type == 'henon':
            x, y = self.generator_states['henon']
            
            for i in range(length):
                x, y = self.generators['henon'](x, y)
                sequence[i] = x
                
            self.generator_states['henon'] = (x, y)
            
        else:  # Lorenz
            x, y, z = self.generator_states['lorenz']
            
            for i in range(length):
                dx, dy, dz = self.generators['lorenz'](x, y, z)
                x += dx * 0.01
                y += dy * 0.01
                z += dz * 0.01
                sequence[i] = (x + 30) / 60  # Normalize to 0-1
                
            self.generator_states['lorenz'] = (x, y, z)
            
        return sequence
        
    def _get_next_chaos_value(self) -> float:
        """Get next single chaos value between 0 and 1."""
        return self._generate_chaos_sequence(1)[0]
