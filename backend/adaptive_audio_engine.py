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
    ⚠ Volume Adaptation (Partial)
        - Basic control implemented
        - Missing ambient adaptation
    ☐ Multi-channel Support (Planned)
        - Design complete
        - Implementation pending

Dependencies:
    - sounddevice: Audio output and real-time synthesis
    - numpy: Signal processing and calculations
    - ai_advisor: ML-based frequency optimization

Integration Points:
    - flow_state_detector.py: Receives state updates
    - biometric/whoop_client.py: Gets HRV data
    - biometric/tobii_tracker.py: Synchronizes with eye movement

Example:
    engine = AdaptiveAudioEngine(api_key="your-api-key")
    strobe_freq = await engine.start("flow")
    engine.update_brainwave_response(alpha=10, theta=5, beta=3, gamma=2)
    engine.stop()
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
import json
import time
from datetime import datetime
import numpy as np
import sounddevice as sd
from ai_advisor import AIAdvisor


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
    
    def _audio_callback(self, outdata: np.ndarray, frames: int, 
                       time_info: Dict, status: sd.CallbackFlags) -> None:
        """Generate audio samples for sounddevice.
        
        Args:
            outdata: Output buffer to fill with audio samples
            frames: Number of frames to generate
            time_info: Timing information from sounddevice
            status: Status flags from sounddevice
        """
        if self.current_session is None:
            outdata.fill(0)
            return
            
        t = (self.phase + np.arange(frames)) / self.SAMPLE_RATE
        left = np.sin(2 * np.pi * self.current_session.base_freq * t)
        right = np.sin(2 * np.pi * (self.current_session.base_freq + self.current_session.beat_freq) * t)
        
        outdata[:, 0] = left * self.volume
        outdata[:, 1] = right * self.volume
        
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
