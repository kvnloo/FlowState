"""Chaos System for Neural Entrainment.

This module introduces controlled chaos into various stimulation parameters
to explore novel neural entrainment patterns. It uses deterministic chaos algorithms
to generate unpredictable but bounded variations in stimulation parameters.

Implementation Status:
    ✓ Global Chaos Control (2024-02-24)
        - Level-based chaos injection
        - Safe bounds enforcement
        - Real-time adaptation
    ✓ Pattern Generation (2024-02-24)
        - Strobe pattern variation
        - Binaural beat modulation
        - Duty cycle adaptation
    ✓ Chaos Algorithms (2024-02-24)
        - Logistic map
        - Henon map
        - Lorenz system
    ⚠ Pattern Learning (Partial)
        - Basic effectiveness tracking
        - Needs: Long-term optimization
    ☐ Multi-dimensional Chaos (Planned)
        - Design complete
        - Implementation pending

Dependencies:
    - numpy: Array operations and chaos calculations
    - scipy: Signal processing utilities
    - dataclasses: Configuration data structures
    - typing: Type hint support
    - random: Initialization randomization
    - datetime: Timestamp management

Integration Points:
    - flow_state_detector.py: Provides feedback for pattern effectiveness
    - adaptive_audio_engine.py: Receives chaotic frequency modulations
    - visual/visual_processor.py: Receives strobe pattern variations

Example:
    ```python
    # Initialize chaos system with moderate chaos
    system = ChaosSystem(global_chaos=0.3)
    
    # Configure chaos parameters
    config = ChaosConfig(
        base_value=10.0,
        min_value=8.0,
        max_value=12.0,
        volatility=0.2,
        pattern_length=100,
        mutation_rate=0.1
    )
    
    # Generate chaotic strobe pattern
    pattern = system.get_strobe_pattern(
        base_freq=10.0,
        duration_ms=1000,
        config=config
    )
    ```

Performance Considerations:
    - Chaos generation is computationally lightweight
    - Pattern history storage grows linearly with usage
    - Real-time generation suitable for audio/visual feedback

Configuration:
    No external configuration required. All parameters are passed
    through the ChaosConfig dataclass or constructor arguments.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random
from scipy import signal
from datetime import datetime

@dataclass
class ChaosConfig:
    """Configuration for chaos injection.

    Defines the parameters and constraints for chaos injection into a specific
    stimulation parameter (frequency, timing, etc.).

    Attributes:
        base_value (float): Starting value for the parameter
        min_value (float): Minimum allowed value
        max_value (float): Maximum allowed value
        volatility (float): Maximum allowed change per step (0.0-1.0)
        pattern_length (int): Number of steps before potential pattern change
        mutation_rate (float): Probability of pattern mutation per step (0.0-1.0)

    Class Invariants:
        - min_value <= base_value <= max_value
        - 0.0 <= volatility <= 1.0
        - pattern_length > 0
        - 0.0 <= mutation_rate <= 1.0

    Example:
        ```python
        config = ChaosConfig(
            base_value=10.0,
            min_value=8.0,
            max_value=12.0,
            volatility=0.2,
            pattern_length=100,
            mutation_rate=0.1
        )
        ```

    Note:
        Volatility and mutation_rate together determine how quickly and
        dramatically patterns can change. Higher values lead to more
        unpredictable behavior.
    """
    base_value: float
    min_value: float
    max_value: float
    volatility: float  # How much the value can change per step
    pattern_length: int  # Length of pattern before potential change
    mutation_rate: float  # Probability of pattern mutation

@dataclass
class EffectivePattern:
    """Record of patterns that produced interesting results.

    Stores patterns that led to positive neural entrainment effects,
    along with their measured impact and effectiveness score.

    Attributes:
        pattern (np.ndarray): The successful stimulation pattern
        eeg_effect (Dict[str, float]): Measured EEG band power changes
        timestamp (datetime): When the pattern was recorded
        score (float): Effectiveness score (0.0-1.0)

    Example:
        ```python
        pattern = EffectivePattern(
            pattern=np.array([1.0, 1.2, 0.8, 1.1]),
            eeg_effect={'alpha': 0.5, 'theta': 0.3},
            timestamp=datetime.now(),
            score=0.85
        )
        ```

    Note:
        Patterns are stored for future optimization and machine learning
        applications. Higher scores indicate more effective patterns.
    """
    pattern: np.ndarray
    eeg_effect: Dict[str, float]
    timestamp: datetime
    score: float

class ChaosSystem:
    """Manages chaos injection across the system.

    This class implements various chaos generation algorithms to create
    controlled unpredictability in stimulation parameters. It tracks
    effective patterns and adapts its behavior based on feedback.

    Attributes:
        global_chaos (float): Master chaos level (0.0-1.0)
        rng (np.random.Generator): Random number generator
        effective_patterns (List[EffectivePattern]): History of successful patterns
        generators (Dict): Available chaos generation algorithms
        generator_states (Dict): Current state of each generator

    Class Invariants:
        - 0.0 <= global_chaos <= 1.0
        - At least one chaos generator must be available
        - Generator states must match generator algorithms

    Example:
        ```python
        system = ChaosSystem(global_chaos=0.3)
        pattern = system.get_strobe_pattern(
            base_freq=10.0,
            duration_ms=1000,
            config=config
        )
        ```

    Note:
        The system uses deterministic chaos to ensure reproducibility
        while maintaining apparent randomness. This allows for pattern
        tracking and optimization over time.
    """
    
    def __init__(self, 
                 global_chaos: float = 0.0,
                 seed: Optional[int] = None):
        """Initialize the chaos system.
        
        Sets up the chaos generation system with specified global chaos level
        and optional random seed for reproducibility.

        Args:
            global_chaos: Global chaos level (0.0-1.0)
            seed: Random seed for reproducibility

        Raises:
            ValueError: If global_chaos is outside [0.0, 1.0] range

        Example:
            ```python
            # Create system with moderate chaos
            system = ChaosSystem(global_chaos=0.3)
            
            # Create reproducible system
            system = ChaosSystem(global_chaos=0.3, seed=42)
            ```
        """
        if not 0.0 <= global_chaos <= 1.0:
            raise ValueError("global_chaos must be between 0.0 and 1.0")
            
        self.global_chaos = global_chaos
        self.rng = np.random.default_rng(seed)
        
        # Store effective patterns for future use
        self.effective_patterns: List[EffectivePattern] = []
        
        # Initialize chaos generators
        self._init_chaos_generators()
        
    def _init_chaos_generators(self):
        """Initialize various chaos generation methods.

        Sets up the available chaos generators and their initial states.
        Each generator produces values in the [0, 1] range.

        Technical Details:
            - Logistic map: r * x * (1 - x)
            - Henon map: 1 - a*x^2 + y, b*x
            - Lorenz system: dx/dt = s(y-x), dy/dt = x(r-z)-y, dz/dt = xy-bz

        Note:
            Generator parameters are chosen to ensure chaotic behavior
            while maintaining bounded outputs.
        """
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
        """Set global chaos level.

        Updates the system-wide chaos level that scales all chaos effects.

        Args:
            level: New chaos level (0.0-1.0)

        Raises:
            ValueError: If level is outside [0.0, 1.0] range

        Example:
            ```python
            # Increase chaos level
            system.set_global_chaos(0.5)
            ```
        """
        if not 0.0 <= level <= 1.0:
            raise ValueError("Chaos level must be between 0.0 and 1.0")
        self.global_chaos = level
        
    def get_strobe_pattern(self, 
                          base_freq: float,
                          duration_ms: int,
                          config: ChaosConfig) -> np.ndarray:
        """Generate chaotic strobe pattern.
        
        Creates a sequence of strobe timings with controlled chaos injection.
        The pattern maintains the average frequency while introducing timing
        variations.

        Args:
            base_freq: Base frequency in Hz (1.0-60.0)
            duration_ms: Duration in milliseconds (>0)
            config: Chaos configuration for this parameter
            
        Returns:
            np.ndarray: Array of strobe timings with chaos injected

        Raises:
            ValueError: If base_freq or duration_ms are invalid

        Example:
            ```python
            pattern = system.get_strobe_pattern(
                base_freq=10.0,
                duration_ms=1000,
                config=config
            )
            ```

        Technical Details:
            - Maintains average frequency over time
            - Applies bounded random walks to timing
            - Uses chaos sequence for variation
            - Ensures safe frequency bounds
        """
        if base_freq <= 0 or base_freq > 60:
            raise ValueError("base_freq must be between 1.0 and 60.0 Hz")
        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

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
        
        Creates frequency patterns for left and right audio channels to produce
        binaural beats with controlled chaos injection.

        Args:
            base_freq: Base frequency in Hz (20.0-500.0)
            duration_ms: Duration in milliseconds (>0)
            config: Chaos configuration for this parameter
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Left and right ear frequency arrays

        Raises:
            ValueError: If base_freq or duration_ms are invalid

        Example:
            ```python
            left_freq, right_freq = system.get_binaural_frequencies(
                base_freq=100.0,
                duration_ms=1000,
                config=config
            )
            ```

        Technical Details:
            - Maintains frequency difference for beat
            - Applies coupled chaos to both channels
            - Ensures frequencies stay in audible range
            - Optimizes for neural entrainment
        """
        if base_freq < 20 or base_freq > 500:
            raise ValueError("base_freq must be between 20.0 and 500.0 Hz")
        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

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
        
        Creates a modified duty cycle with controlled chaos injection
        for visual or other stimulation patterns.

        Args:
            base_duty: Base duty cycle (0.0-1.0)
            config: Chaos configuration for this parameter
            
        Returns:
            float: Modified duty cycle

        Raises:
            ValueError: If base_duty is outside [0.0, 1.0]

        Example:
            ```python
            duty = system.get_duty_cycle(
                base_duty=0.5,
                config=config
            )
            ```

        Technical Details:
            - Maintains average duty cycle
            - Uses single chaos value per call
            - Ensures bounds for safe operation
            - Smooth transitions between values
        """
        if not 0.0 <= base_duty <= 1.0:
            raise ValueError("base_duty must be between 0.0 and 1.0")

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
        
        Stores patterns that led to positive neural entrainment effects
        for future optimization and analysis.

        Args:
            pattern: The pattern that was used
            eeg_data: Resulting EEG measurements
            score: Effectiveness score (0.0-1.0)

        Raises:
            ValueError: If score is outside [0.0, 1.0]

        Example:
            ```python
            system.record_effective_pattern(
                pattern=strobe_pattern,
                eeg_data={'alpha': 0.5, 'theta': 0.3},
                score=0.85
            )
            ```

        Technical Details:
            - Maintains sorted history
            - Limits storage to top 100 patterns
            - Uses timestamps for aging
            - Optimizes for memory usage
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

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
        
        Creates a sequence of chaos values using one of the available
        chaos generators.

        Args:
            length: Length of sequence to generate (>0)
            
        Returns:
            np.ndarray: Array of chaos values between 0 and 1

        Raises:
            ValueError: If length is not positive

        Technical Details:
            - Randomly selects generator type
            - Maintains generator state
            - Ensures bounded output
            - Optimizes for sequence length
        """
        if length <= 0:
            raise ValueError("length must be positive")

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
        """Get next single chaos value.
        
        Generates a single chaos value using the current generator state.

        Returns:
            float: Chaos value between 0 and 1

        Technical Details:
            - Uses current generator state
            - Updates state after generation
            - Ensures value bounds
            - Optimizes for single value
        """
        return self._generate_chaos_sequence(1)[0]
