"""EEG Data Collection and Processing Module.

This module handles EEG data collection from Muse devices via Lab Streaming Layer (LSL),
processes the raw data into frequency bands, and provides real-time analysis capabilities.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import asyncio
import logging
from enum import IntEnum
import numpy as np
from pylsl import StreamInlet, resolve_byprop, StreamInfo
import utils

class Band(IntEnum):
    """EEG frequency bands."""
    Delta = 0  # 0.5-4 Hz: Deep sleep, healing
    Theta = 1  # 4-8 Hz: Creativity, deep relaxation
    Alpha = 2  # 8-13 Hz: Relaxed focus, learning
    Beta = 3   # 13-30 Hz: Active thinking
    Gamma = 4  # 30-100 Hz: Peak performance

@dataclass
class EEGConfig:
    """Configuration for EEG data processing."""
    buffer_length: float = 3.0  # Length of the EEG data buffer (seconds)
    epoch_length: float = 1.0   # Length of FFT computation epochs (seconds)
    overlap_length: float = 0.5 # Overlap between consecutive epochs (seconds)
    channels: List[int] = None  # Channel indices to use (None = all channels)
    
    def __post_init__(self):
        if self.channels is None:
            # Default channels: left/right forehead
            self.channels = [1, 2]
        self.shift_length = self.epoch_length - self.overlap_length

@dataclass
class BandPowers:
    """Power values for each frequency band."""
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float

    @property
    def as_dict(self) -> Dict[str, float]:
        """Convert band powers to dictionary."""
        return {
            'delta': self.delta,
            'theta': self.theta,
            'alpha': self.alpha,
            'beta': self.beta,
            'gamma': self.gamma
        }

class EEGProcessor:
    """Handles EEG data collection and processing."""

    def __init__(self, config: Optional[EEGConfig] = None):
        """Initialize the EEG processor.
        
        Args:
            config: Optional configuration settings. If None, uses defaults.
        """
        self.config = config or EEGConfig()
        self.inlet: Optional[StreamInlet] = None
        self.fs: Optional[int] = None
        self.buffers: Optional[List] = None
        self.filter_state = None
        self._processing = False
        self._callback = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def connect(self, timeout: float = 2.0) -> bool:
        """Connect to an EEG stream.
        
        Args:
            timeout: Time to wait for stream in seconds
            
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            RuntimeError: If no EEG stream found
        """
        try:
            self.logger.info('Looking for an EEG stream...')
            streams = resolve_byprop('type', 'EEG', timeout=timeout)
            
            if not streams:
                raise RuntimeError('No EEG stream found')
                
            # Connect to the first available stream
            self.inlet = StreamInlet(streams[0], max_chunklen=12)
            self.fs = int(self.inlet.info().nominal_srate())
            
            # Initialize data buffers
            self.buffers = self._init_buffers()
            
            self.logger.info(f'Connected to EEG stream: {self.inlet.info().name()}')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to connect to EEG stream: {str(e)}')
            return False

    def _init_buffers(self) -> List:
        """Initialize EEG data buffers.
        
        Returns:
            List containing raw EEG and band power buffers
        """
        # Raw EEG buffer
        eeg_buffer = np.zeros((int(self.fs * self.config.buffer_length), 1))
        
        # Calculate number of epochs
        n_epochs = int(np.floor((self.config.buffer_length - self.config.epoch_length) /
                               self.config.shift_length + 1))
        
        # Band power buffer for each channel
        band_buffer = np.zeros((n_epochs, len(Band)))
        
        # Create buffer list for each channel
        return [[eeg_buffer.copy() for _ in self.config.channels],
                [band_buffer.copy() for _ in self.config.channels]]

    async def process_chunk(self) -> Optional[Dict[str, Any]]:
        """Process a single chunk of EEG data.
        
        Returns:
            Dictionary containing processed data and band powers
        """
        if not self.inlet:
            self.logger.error('No EEG stream connected')
            return None
            
        try:
            channel_data = {}
            
            for idx, channel in enumerate(self.config.channels):
                # Get EEG data chunk
                eeg_data, timestamp = self.inlet.pull_chunk(
                    timeout=1, 
                    max_samples=int(self.config.shift_length * self.fs)
                )
                
                if not eeg_data:
                    continue
                    
                # Process channel data
                ch_data = np.array(eeg_data)[:, channel]
                
                # Update EEG buffer
                self.buffers[0][idx], self.filter_state = utils.update_buffer(
                    self.buffers[0][idx], ch_data, 
                    notch=True, 
                    filter_state=self.filter_state
                )
                
                # Get latest epoch
                data_epoch = utils.get_last_data(
                    self.buffers[0][idx],
                    int(self.config.epoch_length * self.fs)
                )
                
                # Compute band powers
                band_powers = utils.compute_PSD(data_epoch, self.fs)
                self.buffers[1][idx], _ = utils.update_buffer(
                    self.buffers[1][idx], 
                    np.asarray([band_powers])
                )
                
                # Store processed data
                channel_data[f'channel_{channel}'] = {
                    'timestamp': timestamp,
                    'raw_data': ch_data.tolist(),
                    'band_powers': BandPowers(
                        delta=float(band_powers[Band.Delta]),
                        theta=float(band_powers[Band.Theta]),
                        alpha=float(band_powers[Band.Alpha]),
                        beta=float(band_powers[Band.Beta]),
                        gamma=float(band_powers[Band.Gamma])
                    ).as_dict
                }
            
            return channel_data
            
        except Exception as e:
            self.logger.error(f'Error processing EEG chunk: {str(e)}')
            return None

    async def start_monitoring(self, callback=None):
        """Start continuous EEG monitoring.
        
        Args:
            callback: Optional function to call with processed data
        """
        if self._processing:
            self.logger.warning('Monitoring already in progress')
            return
            
        self._processing = True
        self._callback = callback
        
        self.logger.info('Starting EEG monitoring...')
        
        while self._processing:
            data = await self.process_chunk()
            if data and self._callback:
                await self._callback(data)
            await asyncio.sleep(0.1)  # Prevent CPU overload

    async def stop_monitoring(self):
        """Stop EEG monitoring."""
        self._processing = False
        self.logger.info('Stopped EEG monitoring')

    def get_channel_quality(self) -> Dict[int, float]:
        """Get the signal quality for each channel.
        
        Returns:
            Dictionary mapping channel numbers to quality scores (0-1)
        """
        quality_scores = {}
        
        for idx, channel in enumerate(self.config.channels):
            if self.buffers and len(self.buffers[0]) > idx:
                # Calculate signal quality based on variance and artifact detection
                raw_data = self.buffers[0][idx]
                variance = np.var(raw_data)
                artifact_ratio = np.sum(np.abs(raw_data) > 100) / len(raw_data)
                
                # Quality score between 0 and 1
                quality = max(0, min(1, 1 - artifact_ratio) * (1 - np.clip(variance / 1000, 0, 1)))
                quality_scores[channel] = float(quality)
                
        return quality_scores

    def get_average_band_powers(self) -> BandPowers:
        """Get average band powers across all channels.
        
        Returns:
            BandPowers object containing averaged values
        """
        if not self.buffers or not self.buffers[1]:
            return BandPowers(0, 0, 0, 0, 0)
            
        # Average the latest band powers across all channels
        avg_powers = np.mean([buf[-1] for buf in self.buffers[1]], axis=0)
        
        return BandPowers(
            delta=float(avg_powers[Band.Delta]),
            theta=float(avg_powers[Band.Theta]),
            alpha=float(avg_powers[Band.Alpha]),
            beta=float(avg_powers[Band.Beta]),
            gamma=float(avg_powers[Band.Gamma])
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()