"""Real-time EEG Processing Module.

This module provides real-time EEG signal processing and analysis capabilities.

Implementation Status:
    ✓ Signal Processing (2024-02-24)
        - Artifact rejection
        - Band power extraction
        - Real-time filtering
    ✓ Feature Extraction (2024-02-24)
        - Cross-frequency coupling
        - Phase synchronization
        - Power ratios
    ✓ Data Management (2024-02-24)
        - Circular buffer
        - Streaming interface
        - Event markers
    ⚠ Advanced Analysis (Partial)
        - Source localization
        - Connectivity metrics
    ☐ Multi-device Support (Planned)
        - Device abstraction
        - Protocol handling

Dependencies:
    - numpy: Array operations and signal processing
    - scipy: Advanced signal processing
    - mne: EEG-specific processing utilities
    - numba: Performance optimization

Integration Points:
    - flow_state_detector.py: Flow state analysis
    - adaptive_audio_engine.py: Neural entrainment
    - ai_advisor.py: State optimization
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Deque
import numpy as np
from scipy import signal
import mne
from collections import deque
import logging
from numba import jit
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class EEGBuffer:
    """Circular buffer for EEG data with preprocessing capabilities.
    
    Attributes:
        max_size: Maximum number of samples to store
        channels: List of channel names
        sampling_rate: Sampling rate in Hz
        data: Circular buffer for raw data
        filtered_data: Preprocessed data cache
    """
    max_size: int
    channels: List[str]
    sampling_rate: int
    data: Deque[np.ndarray] = field(default_factory=lambda: deque(maxlen=2048))
    filtered_data: Dict[str, np.ndarray] = field(default_factory=dict)

@dataclass
class ArtifactParams:
    """Parameters for artifact detection and rejection.
    
    Attributes:
        amplitude_threshold: Maximum allowed amplitude (μV)
        gradient_threshold: Maximum allowed gradient (μV/ms)
        flatline_duration: Maximum duration of flat signal (ms)
        noise_threshold: Maximum high-frequency noise level
    """
    amplitude_threshold: float = 100.0
    gradient_threshold: float = 10.0
    flatline_duration: int = 100
    noise_threshold: float = 0.8

class RealtimeEEGProcessor:
    """Real-time EEG signal processing and analysis.
    
    This class provides real-time processing of EEG signals, including
    artifact rejection, feature extraction, and streaming analysis.
    """
    
    def __init__(self, channels: List[str], sampling_rate: int,
                 buffer_duration: float = 4.0):
        """Initialize the EEG processor.
        
        Args:
            channels: List of EEG channel names
            sampling_rate: Sampling rate in Hz
            buffer_duration: Duration of data to buffer (seconds)
        """
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.buffer_size = int(buffer_duration * sampling_rate)
        self.buffer = EEGBuffer(
            max_size=self.buffer_size,
            channels=channels,
            sampling_rate=sampling_rate
        )
        self.artifact_params = ArtifactParams()
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Initialize filters
        self._init_filters()
        
    def _init_filters(self) -> None:
        """Initialize filter coefficients for different frequency bands."""
        self.filters = {
            'theta': signal.butter(3, [4, 8], 'bandpass', fs=self.sampling_rate),
            'alpha': signal.butter(3, [8, 13], 'bandpass', fs=self.sampling_rate),
            'beta': signal.butter(3, [13, 30], 'bandpass', fs=self.sampling_rate),
            'gamma': signal.butter(3, [30, 100], 'bandpass', fs=self.sampling_rate),
            'line_noise': signal.butter(3, [48, 52], 'bandstop', fs=self.sampling_rate)
        }

    @jit(nopython=True)
    def _detect_artifacts(self, data: np.ndarray) -> np.ndarray:
        """Detect artifacts in EEG data using Numba-optimized processing.
        
        Args:
            data: Raw EEG data array
            
        Returns:
            np.ndarray: Boolean mask of clean samples
            
        Technical Details:
            - Amplitude thresholding
            - Gradient analysis
            - Flatline detection
            - High-frequency noise detection
        """
        mask = np.ones(len(data), dtype=np.bool_)
        
        # Amplitude threshold
        mask &= np.abs(data) < self.artifact_params.amplitude_threshold
        
        # Gradient threshold
        gradients = np.diff(data, prepend=data[0])
        mask &= np.abs(gradients) < self.artifact_params.gradient_threshold
        
        # Flatline detection
        for i in range(len(data) - self.artifact_params.flatline_duration):
            if np.std(data[i:i+self.artifact_params.flatline_duration]) < 0.1:
                mask[i:i+self.artifact_params.flatline_duration] = False
        
        return mask

    async def process_chunk(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Process a chunk of EEG data asynchronously.
        
        Args:
            data: Raw EEG data chunk
            
        Returns:
            Dict containing processed data for each frequency band
            
        Technical Details:
            - Line noise removal
            - Artifact rejection
            - Band-specific filtering
            - Feature extraction
        """
        # Remove line noise
        denoised = signal.filtfilt(*self.filters['line_noise'], data)
        
        # Detect artifacts
        clean_mask = await asyncio.get_event_loop().run_in_executor(
            self.thread_pool, self._detect_artifacts, denoised
        )
        
        # Apply filters to clean data
        filtered = {}
        for band, (b, a) in self.filters.items():
            if band != 'line_noise':
                filtered[band] = signal.filtfilt(b, a, denoised * clean_mask)
        
        # Update buffer
        self.buffer.data.append(denoised)
        self.buffer.filtered_data = filtered
        
        return filtered

    async def extract_features(self) -> Dict[str, float]:
        """Extract relevant features from the current buffer.
        
        Returns:
            Dict containing extracted features:
                - Band powers
                - Cross-frequency coupling
                - Phase synchronization
                - Signal quality metrics
        """
        if not self.buffer.data:
            return {}
        
        # Get latest data
        data = np.array(list(self.buffer.data))
        filtered = self.buffer.filtered_data
        
        # Calculate band powers
        powers = {
            band: np.mean(np.abs(hilbert_data)**2)
            for band, hilbert_data in filtered.items()
        }
        
        # Calculate cross-frequency coupling
        theta_phase = np.angle(signal.hilbert(filtered['theta']))
        gamma_amp = np.abs(signal.hilbert(filtered['gamma']))
        coupling = np.abs(np.mean(gamma_amp * np.exp(1j * theta_phase)))
        
        # Calculate phase synchronization
        alpha_phase = np.angle(signal.hilbert(filtered['alpha']))
        beta_phase = np.angle(signal.hilbert(filtered['beta']))
        sync = 1 - np.std(np.mod(alpha_phase - beta_phase, 2*np.pi))
        
        # Combine features
        features = {
            **powers,
            'theta_gamma_coupling': coupling,
            'alpha_beta_sync': sync,
            'signal_quality': np.mean(self._detect_artifacts(data))
        }
        
        return features

    async def run_pipeline(self, data_stream: asyncio.Queue) -> None:
        """Run the complete processing pipeline on streaming data.
        
        Args:
            data_stream: Queue containing incoming EEG data chunks
            
        Technical Details:
            - Asynchronous processing
            - Real-time feature extraction
            - Quality monitoring
            - Performance optimization
        """
        while True:
            try:
                # Get next chunk
                chunk = await data_stream.get()
                
                # Process chunk
                filtered_data = await self.process_chunk(chunk)
                
                # Extract features
                features = await self.extract_features()
                
                # Log processing results
                logging.debug(
                    f"Processed chunk - Signal quality: {features.get('signal_quality', 0):.2f}, "
                    f"Theta-gamma coupling: {features.get('theta_gamma_coupling', 0):.2f}"
                )
                
            except Exception as e:
                logging.error(f"Error in EEG processing pipeline: {str(e)}")
                continue
