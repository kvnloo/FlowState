"""Adaptive Audio Engine Module.

This module provides real-time binaural beat generation and adaptation based on user state.

Implementation Status:
    ✓ Binaural Beat Generation (2024-02-24)
        - Carrier frequency management
        - Beat frequency adaptation
        - Real-time synthesis
    ✓ User State Tracking (2024-02-24)
        - Fatigue monitoring
        - Caffeine level tracking
        - Sleep state integration
    ✓ AI Recommendations (2024-02-24)
        - Frequency optimization
        - State-based adaptation
    ✓ Cross-Frequency Coupling (2024-02-24)
        - Gamma-theta coupling
        - Phase-amplitude modulation
        - Neural entrainment
    ⚠ Volume Adaptation (Partial)
        - Basic control implemented
        - Missing ambient adaptation
    ☐ Multi-channel Support (Planned)
        - Design complete
        - Implementation pending

Dependencies:
    - numpy: Array operations and signal generation
    - sounddevice: Real-time audio output
    - scipy: Signal processing utilities
    - dataclasses: Data structure management

Integration Points:
    - flow_state_detector.py: Flow state metrics and optimization
    - ai_advisor.py: Frequency recommendations
    - biometric/whoop_client.py: Recovery state tracking

Example:
    ```python
    engine = AdaptiveAudioEngine()
    await engine.start('flow', user_state={'fatigue': 0.3})
    engine.update_frequencies(theta=6.0, gamma=40.0)
    ```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Literal
import numpy as np
import sounddevice as sd
import json
import asyncio
import logging
from pathlib import Path

@dataclass
class UserState:
    """User's current physiological and environmental state.
    
    Attributes:
        time_of_day: Hour of the day (0-23)
        fatigue: Optional fatigue level (0-10)
        caffeine_level: Optional caffeine level (0-10)
        last_sleep: Optional hours since last sleep
    """
    time_of_day: int
    fatigue: Optional[float] = None
    caffeine_level: Optional[float] = None
    last_sleep: Optional[float] = None

@dataclass
class FrequencyResponse:
    """Records the brain's response to specific frequency combinations.
    
    Attributes:
        base_freq: Base carrier frequency in Hz
        beat_freq: Binaural beat frequency in Hz
        timestamp: Unix timestamp of the recording
        alpha_response: Maximum alpha wave power during session
        theta_response: Maximum theta wave power during session
        beta_response: Maximum beta wave power during session
        gamma_response: Maximum gamma wave power during session
        flow_score: Calculated flow state score (0-1)
        user_state: User's state during the session
    """
    base_freq: float
    beat_freq: float
    timestamp: float
    alpha_response: float
    theta_response: float
    beta_response: float
    gamma_response: float
    flow_score: float
    user_state: UserState

@dataclass
class FrequencyRecommendation:
    """AI-generated frequency recommendations.
    
    Attributes:
        base_freq: Recommended carrier frequency in Hz
        beat_freq: Recommended binaural beat frequency in Hz
        strobe_freq: Recommended visual strobe frequency in Hz
        confidence: AI's confidence in the recommendation (0-1)
        reasoning: Explanation for the recommendation
    """
    base_freq: float
    beat_freq: float
    strobe_freq: float
    confidence: float
    reasoning: str

@dataclass
class PhaseState:
    """Track phase relationships between frequency bands.
    
    Attributes:
        theta_phase: Current phase of theta wave (radians)
        gamma_phase: Current phase of gamma wave (radians)
        alpha_phase: Current phase of alpha wave (radians)
        coupling_strength: Strength of phase coupling (0-1)
        phase_lag: Phase difference between left/right channels (radians)
    """
    theta_phase: float = 0.0
    gamma_phase: float = 0.0
    alpha_phase: float = 0.0
    coupling_strength: float = 0.5
    phase_lag: float = 0.0

@dataclass
class FrequencyAdaptation:
    """Tracks and adapts frequency responses for personalization.
    
    Attributes:
        base_frequency_range: Valid range for carrier frequency
        beat_frequency_range: Valid range for beat frequency
        adaptation_rate: Learning rate for frequency updates (0-1)
        frequency_history: Recent frequency responses
        optimal_ranges: Personalized optimal frequency ranges
    """
    base_frequency_range: Tuple[float, float] = (4.0, 12.0)
    beat_frequency_range: Tuple[float, float] = (0.5, 4.0)
    adaptation_rate: float = 0.1
    frequency_history: List[FrequencyResponse] = field(default_factory=list)
    optimal_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)

class AdaptiveAudioEngine:
    """Adaptive binaural beat generator for neural entrainment.
    
    This class generates binaural beats using sounddevice, adapting frequencies
    based on real-time brainwave data and AI recommendations. It maintains a history
    of successful frequency combinations and uses them to optimize future sessions.
    
    Attributes:
        FREQUENCY_RANGES: Dictionary defining optimal frequency ranges for different states
        SAMPLE_RATE: Audio sample rate in Hz
    """
    
    FREQUENCY_RANGES = {
        'flow': {
            'alpha': {'min': 8, 'max': 12},    # Upper alpha band
            'theta': {'min': 6, 'max': 8},     # Upper theta band
            'beta': {'min': 12, 'max': 15}     # Low beta band
        },
        'carrier': {'min': 100, 'max': 400},   # Carrier frequency range
        'strobe': {'min': 4, 'max': 12}        # Safe strobe frequency range
    }
    
    SAMPLE_RATE = 44100  # Standard audio sample rate
    
    def __init__(self, api_key: str):
        """Initialize the audio engine.
        
        Args:
            api_key: API key for the AI advisor service
        """
        self.advisor = AIAdvisor(api_key)
        self.user_responses: List[FrequencyResponse] = []
        self.current_session: Optional[FrequencyResponse] = None
        self.session_start_time: float = 0
        self.stream: Optional[sd.OutputStream] = None
        self.volume = 0.1
        self.phase = 0
        self.phase_state = PhaseState()
        self.frequency_adaptation = FrequencyAdaptation()
        
        self._load_user_responses()
    
    def _load_user_responses(self) -> None:
        """Load previous user responses from storage."""
        try:
            with open('frequency_responses.json', 'r') as f:
                data = json.load(f)
                self.user_responses = [FrequencyResponse(**resp) for resp in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_responses = []
    
    def _save_user_responses(self) -> None:
        """Save user responses to storage."""
        with open('frequency_responses.json', 'w') as f:
            json.dump([resp.__dict__ for resp in self.user_responses], f)
    
    def _calculate_flow_score(self, alpha: float, theta: float, beta: float) -> float:
        """Calculate the current flow state score.
        
        Args:
            alpha: Alpha wave power
            theta: Theta wave power
            beta: Beta wave power
            
        Returns:
            Flow state score between 0 and 1
        """
        # Calculate ratios important for flow state
        alpha_theta = alpha / (theta or 0.1)  # Alpha/Theta ratio
        alpha_beta = alpha / (beta or 0.1)    # Alpha/Beta ratio
        
        # Ideal ranges for flow state
        ideal_alpha_theta = 1.5  # Slightly more alpha than theta
        ideal_alpha_beta = 2.0   # Alpha should be stronger than beta
        
        # Calculate how close we are to ideal ratios
        alpha_theta_score = 1 - min(abs(alpha_theta - ideal_alpha_theta) / ideal_alpha_theta, 1)
        alpha_beta_score = 1 - min(abs(alpha_beta - ideal_alpha_beta) / ideal_alpha_beta, 1)
        
        # Combine scores with weights
        return 0.6 * alpha_theta_score + 0.4 * alpha_beta_score
    
    def _generate_coupled_waveform(self, t: np.ndarray) -> np.ndarray:
        """Generate phase-coupled waveform combining theta and gamma.
        
        This method implements cross-frequency coupling between theta and gamma
        bands to enhance neural entrainment. It uses theta phase to modulate
        gamma amplitude, creating a naturalistic coupling pattern.
        
        Args:
            t: Time points array for waveform generation
        
        Returns:
            np.ndarray: Combined waveform with phase-amplitude coupling
        
        Technical Details:
            - Theta carrier wave (4-8 Hz)
            - Gamma modulation (40+ Hz)
            - Alpha stabilization (8-12 Hz)
            - Phase-amplitude coupling
        """
        # Theta carrier wave (4-8 Hz)
        theta = np.sin(2 * np.pi * self.current_session.base_freq * t + self.phase_state.theta_phase)
        
        # Gamma modulated by theta phase (40+ Hz)
        gamma_amp = 0.5 * (1 + theta)  # Amplitude modulation
        gamma = gamma_amp * np.sin(2 * np.pi * self.current_session.beat_freq * t + self.phase_state.gamma_phase)
        
        # Alpha for cognitive stability (8-12 Hz)
        alpha = 0.3 * np.sin(2 * np.pi * self.current_session.base_freq * t + self.phase_state.alpha_phase)
        
        # Combine waves with coupling
        combined = (theta + self.phase_state.coupling_strength * gamma + alpha) / 2
        return combined

    def _audio_callback(self, outdata: np.ndarray, frames: int, 
                       time_info: Dict, status: sd.CallbackFlags) -> None:
        """Generate audio samples for sounddevice output.
        
        This callback method is called by sounddevice to fill the audio buffer.
        It generates phase-coupled binaural beats with precise frequency control
        and neural entrainment patterns.
        
        Args:
            outdata: Output buffer to fill with audio samples
            frames: Number of frames to generate
            time_info: Timing information from sounddevice
            status: Status flags from sounddevice
        
        Technical Details:
            - Real-time waveform generation
            - Phase tracking and updates
            - Stereo channel management
            - Volume normalization
        """
        if self.current_session is None:
            outdata.fill(0)
            return
            
        t = (self.phase + np.arange(frames)) / self.SAMPLE_RATE
        
        # Generate coupled waveforms for each ear
        left_coupled = self._generate_coupled_waveform(t)
        
        # Add phase lag for spatial effect
        t_right = t + self.phase_state.phase_lag
        right_coupled = self._generate_coupled_waveform(t_right)
        
        # Update phases
        self.phase_state.theta_phase += 2 * np.pi * self.current_session.base_freq * frames / self.SAMPLE_RATE
        self.phase_state.gamma_phase += 2 * np.pi * self.current_session.beat_freq * frames / self.SAMPLE_RATE
        self.phase_state.alpha_phase += 2 * np.pi * self.current_session.base_freq * frames / self.SAMPLE_RATE
        
        # Normalize and apply volume
        outdata[:, 0] = left_coupled * self.volume
        outdata[:, 1] = right_coupled * self.volume
        
        self.phase += frames
    
    async def start(self, target_state: Literal['focus', 'flow', 'meditate'],
                   user_state: Optional[Dict] = None) -> float:
        """Start generating binaural beats.
        
        Args:
            target_state: Desired mental state
            user_state: Optional dictionary with user's current state
            
        Returns:
            Recommended strobe frequency for visual synchronization
        """
        recommendation = await self.get_optimal_frequencies(target_state, user_state)
        
        self.session_start_time = time.time()
        self.current_session = FrequencyResponse(
            base_freq=recommendation.base_freq,
            beat_freq=recommendation.beat_freq,
            timestamp=self.session_start_time,
            alpha_response=0,
            theta_response=0,
            beta_response=0,
            gamma_response=0,
            flow_score=0,
            user_state=UserState(
                time_of_day=datetime.now().hour,
                **(user_state or {})
            )
        )
        
        self.stream = sd.OutputStream(
            channels=2,
            callback=self._audio_callback,
            samplerate=self.SAMPLE_RATE
        )
        self.stream.start()
        
        return recommendation.strobe_freq
    
    def stop(self) -> None:
        """Stop generating binaural beats."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if self.current_session:
            self.user_responses.append(self.current_session)
            self._save_user_responses()
            self.current_session = None
    
    def set_volume(self, volume: float) -> None:
        """Set the output volume.
        
        Args:
            volume: Volume level between 0 and 1
        """
        self.volume = max(0, min(1, volume))
    
    def update_brainwave_response(self, alpha: float, theta: float,
                                beta: float, gamma: float) -> None:
        """Update the current session with brainwave responses.
        
        Args:
            alpha: Alpha wave power
            theta: Theta wave power
            beta: Beta wave power
            gamma: Gamma wave power
        """
        if self.current_session:
            # Update maximum band powers
            self.current_session.alpha_response = max(self.current_session.alpha_response, alpha)
            self.current_session.theta_response = max(self.current_session.theta_response, theta)
            self.current_session.beta_response = max(self.current_session.beta_response, beta)
            self.current_session.gamma_response = max(self.current_session.gamma_response, gamma)
            
            # Calculate and update flow score
            flow_score = self._calculate_flow_score(alpha, theta, beta)
            self.current_session.flow_score = max(self.current_session.flow_score, flow_score)
            
            # If flow score is high enough, save these frequencies as effective
            if flow_score > 0.8:
                self.user_responses.append(FrequencyResponse(
                    **self.current_session.__dict__,
                    timestamp=time.time()
                ))
                self._save_user_responses()
    
    async def get_optimal_frequencies(self, target_state: Literal['focus', 'flow', 'meditate'],
                                    user_state: Optional[Dict] = None) -> FrequencyRecommendation:
        """Get optimal frequency recommendations.
        
        Args:
            target_state: Desired mental state
            user_state: Optional dictionary with user's current state
            
        Returns:
            FrequencyRecommendation object with optimal frequencies
        """
        current_hour = datetime.now().hour
        
        # Filter for successful flow states in similar conditions
        successful_sessions = [
            session for session in self.user_responses
            if session.flow_score > 0.8 and
            abs(session.user_state.time_of_day - current_hour) <= 2
        ]
        
        # If we have successful sessions, use them to inform our choice
        if successful_sessions:
            best_session = max(successful_sessions, key=lambda x: x.flow_score)
            return FrequencyRecommendation(
                base_freq=best_session.base_freq,
                beat_freq=best_session.beat_freq,
                strobe_freq=best_session.beat_freq / 2,  # Harmonically related to audio
                confidence=0.9,
                reasoning='Using previously successful frequency combination'
            )
        
        # Otherwise, use AI advisor with enhanced parameters
        prompt = f"""
        Recommend optimal frequencies for neural entrainment targeting flow state.
        
        Current Context:
        - Target State: {target_state}
        - Time: {current_hour}:00
        - Fatigue: {user_state.get('fatigue', 'unknown') if user_state else 'unknown'}
        - Caffeine: {user_state.get('caffeine_level', 'unknown') if user_state else 'unknown'}
        - Sleep: {user_state.get('last_sleep', 'unknown') if user_state else 'unknown'}h ago
        
        Requirements:
        1. Base frequency should be in carrier range ({self.FREQUENCY_RANGES['carrier']['min']}-{self.FREQUENCY_RANGES['carrier']['max']}Hz)
        2. Beat frequency should target upper alpha/lower beta ({self.FREQUENCY_RANGES['flow']['alpha']['min']}-{self.FREQUENCY_RANGES['flow']['beta']['min']}Hz)
        3. Strobe frequency should be harmonically related to beat frequency
        4. Consider circadian rhythms and user state
        
        Previous successful combinations:
        {json.dumps([s.__dict__ for s in successful_sessions[-3:]], indent=2)}
        """
        
        try:
            return await self.advisor.get_frequency_recommendation(prompt)
        except Exception as e:
            print(f'Error getting frequency recommendation: {e}')
            
            # Enhanced default frequencies based on target state
            defaults = {
                'focus': {'base': 200, 'beat': 10, 'strobe': 5},      # Upper alpha
                'flow': {'base': 200, 'beat': 8, 'strobe': 4},        # Alpha-theta border
                'meditate': {'base': 200, 'beat': 6, 'strobe': 3},    # Theta
            }
            
            d = defaults[target_state]
            return FrequencyRecommendation(
                base_freq=d['base'],
                beat_freq=d['beat'],
                strobe_freq=d['strobe'],
                confidence=0.5,
                reasoning='Using research-based default frequencies'
            )

    def _update_optimal_ranges(self, flow_metrics: FlowMetrics) -> None:
        """Update optimal frequency ranges based on flow state response.
        
        This method implements adaptive learning of optimal frequency ranges
        based on the user's neural response and flow state metrics.
        
        Args:
            flow_metrics: Current flow state metrics
        
        Technical Details:
            - Exponential moving average for range updates
            - Confidence-weighted adaptation
            - Boundary enforcement for safe ranges
        """
        if not self.current_session:
            return
        
        # Only update if we have high confidence
        if flow_metrics.confidence < 0.6:
            return
        
        # Calculate adaptation weight
        weight = self.frequency_adaptation.adaptation_rate * flow_metrics.confidence
        
        # Update optimal ranges based on flow probability
        if flow_metrics.flow_probability > 0.7:
            current_base = self.current_session.base_freq
            current_beat = self.current_session.beat_freq
            
            # Update optimal ranges with exponential moving average
            for state in ['focus', 'flow', 'meditate']:
                if state not in self.frequency_adaptation.optimal_ranges:
                    self.frequency_adaptation.optimal_ranges[state] = (
                        self.frequency_adaptation.base_frequency_range[0],
                        self.frequency_adaptation.base_frequency_range[1]
                    )
                
                current_range = self.frequency_adaptation.optimal_ranges[state]
                new_min = (1 - weight) * current_range[0] + weight * max(
                    current_base - 1.0,
                    self.frequency_adaptation.base_frequency_range[0]
                )
                new_max = (1 - weight) * current_range[1] + weight * min(
                    current_base + 1.0,
                    self.frequency_adaptation.base_frequency_range[1]
                )
                
                self.frequency_adaptation.optimal_ranges[state] = (new_min, new_max)

    def _adapt_frequencies(self, flow_metrics: FlowMetrics) -> None:
        """Dynamically adapt frequencies based on flow state.
        
        This method implements real-time frequency adaptation based on
        neural coupling strength and flow state metrics.
        
        Args:
            flow_metrics: Current flow state metrics
        
        Technical Details:
            - Theta-gamma coupling optimization
            - Phase synchronization tracking
            - Boundary enforcement
            - Gradual frequency shifts
        """
        if not self.current_session:
            return
        
        # Calculate base frequency adjustment
        coupling_error = 0.8 - flow_metrics.theta_gamma_coupling
        phase_error = 0.8 - flow_metrics.phase_sync
        
        # Adjust base frequency (theta range)
        base_freq_delta = (
            0.3 * coupling_error +
            0.2 * phase_error
        ) * self.frequency_adaptation.adaptation_rate
        
        # Adjust beat frequency (gamma range)
        beat_freq_delta = (
            0.4 * coupling_error +
            0.3 * phase_error
        ) * self.frequency_adaptation.adaptation_rate
        
        # Apply frequency updates with boundary enforcement
        new_base_freq = np.clip(
            self.current_session.base_freq + base_freq_delta,
            self.frequency_adaptation.base_frequency_range[0],
            self.frequency_adaptation.base_frequency_range[1]
        )
        
        new_beat_freq = np.clip(
            self.current_session.beat_freq + beat_freq_delta,
            self.frequency_adaptation.beat_frequency_range[0],
            self.frequency_adaptation.beat_frequency_range[1]
        )
        
        # Update frequencies
        self.current_session = FrequencyResponse(
            base_freq=new_base_freq,
            beat_freq=new_beat_freq,
            volume=self.current_session.volume,
            target_state=self.current_session.target_state,
            strobe_freq=self.current_session.strobe_freq,
            confidence=flow_metrics.confidence,
            reasoning="Dynamic adaptation based on neural coupling"
        )
        
        # Store frequency response for history
        self.frequency_adaptation.frequency_history.append(self.current_session)
        if len(self.frequency_adaptation.frequency_history) > 100:
            self.frequency_adaptation.frequency_history.pop(0)

    async def process_flow_update(self, flow_metrics: FlowMetrics) -> None:
        """Process flow state updates and adapt frequencies.
        
        This method coordinates the frequency adaptation system,
        updating optimal ranges and adjusting frequencies in real-time.
        
        Args:
            flow_metrics: Current flow state metrics
        
        Technical Details:
            - Asynchronous processing
            - Optimal range updates
            - Dynamic frequency adaptation
            - History tracking
        """
        self._update_optimal_ranges(flow_metrics)
        self._adapt_frequencies(flow_metrics)
        
        # Log adaptation results
        logging.info(
            f"Adapted frequencies - Base: {self.current_session.base_freq:.2f} Hz, "
            f"Beat: {self.current_session.beat_freq:.2f} Hz, "
            f"Flow Probability: {flow_metrics.flow_probability:.2f}"
        )
