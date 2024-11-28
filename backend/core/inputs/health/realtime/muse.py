"""Muse EEG Data Collection and Processing Module.

This module implements real-time EEG data collection and analysis from Muse headbands
using the Lab Streaming Layer (LSL) protocol. It provides both raw EEG data access
and processed frequency band analysis.

Features:
    - Device discovery and auto-connection
    - Real-time EEG data streaming via LSL
    - Frequency band decomposition (Delta, Theta, Alpha, Beta, Gamma)
    - Automatic artifact rejection
    - Channel-specific analysis
    - Configurable processing parameters
    - Async/await support
    
Hardware Support:
    - Muse 2
    - Muse S
    - Muse 2016
    
Dependencies:
    - muselsl: Muse LSL interface (required)
    - pylsl: Lab Streaming Layer protocol
    - numpy: Numerical computations
    - scipy: Signal processing
    - bleak: Bluetooth communication
    
LSL Stream Format:
    - Type: 'EEG'
    - Channel Format: 4-5 channels (depending on device)
        * Channel 1: TP9 (Left ear)
        * Channel 2: AF7 (Left forehead)
        * Channel 3: AF8 (Right forehead)
        * Channel 4: TP10 (Right ear)
        * Channel 5: AUX (if available)
    - Sampling Rate: 256 Hz
    - Data Type: float32

Example:
    >>> from muse import EEGProcessor, EEGConfig
    >>> 
    >>> # Configure with custom settings
    >>> config = EEGConfig(
    ...     buffer_length=5.0,    # 5 second buffer
    ...     epoch_length=1.0,     # 1 second epochs
    ...     overlap_length=0.5,   # 50% overlap
    ...     channels=[1, 2]       # Left/right forehead
    ... )
    >>> 
    >>> # Initialize processor
    >>> processor = EEGProcessor(config)
    >>> 
    >>> # Connect and start processing
    >>> async def process_data(data):
    ...     print(f"Alpha power: {data['channel_1']['band_powers']['alpha']}")
    >>> 
    >>> await processor.connect()
    >>> await processor.start_monitoring(callback=process_data)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any, Callable
import asyncio
import logging
from enum import IntEnum
import numpy as np
from muselsl import stream, list_muses, view, record
from muselsl.muse import Muse
from pylsl import StreamInlet, resolve_byprop
import utils

MUSE_SAMPLING_RATE = 256  # Hz
MUSE_EEG_CHANNELS = 4     # 5 if AUX available

class Band(IntEnum):
    """EEG frequency bands in Hz.
    
    Standard frequency bands used in EEG analysis:
    - Delta (0.5-4 Hz): Deep sleep, healing
    - Theta (4-8 Hz): Creativity, meditation
    - Alpha (8-13 Hz): Relaxed focus, learning
    - Beta (13-30 Hz): Active thinking, focus
    - Gamma (30-100 Hz): Peak performance, insight
    """
    Delta = 0  # 0.5-4 Hz
    Theta = 1  # 4-8 Hz
    Alpha = 2  # 8-13 Hz
    Beta = 3   # 13-30 Hz
    Gamma = 4  # 30-100 Hz
    
    @property
    def frequency_range(self) -> Tuple[float, float]:
        """Get the frequency range for this band.
        
        Returns:
            Tuple of (min_freq, max_freq) in Hz
        """
        ranges = {
            Band.Delta: (0.5, 4.0),
            Band.Theta: (4.0, 8.0),
            Band.Alpha: (8.0, 13.0),
            Band.Beta: (13.0, 30.0),
            Band.Gamma: (30.0, 100.0)
        }
        return ranges[self]

@dataclass
class EEGConfig:
    """Configuration for EEG data processing.
    
    Attributes:
        buffer_length: Length of the EEG data buffer in seconds
        epoch_length: Length of FFT computation epochs in seconds
        overlap_length: Overlap between consecutive epochs in seconds
        channels: Channel indices to use (None = all channels)
        notch_freq: Frequency for notch filter (50/60 Hz)
        bandpass_range: Frequency range for bandpass filter
        artifact_threshold: Z-score threshold for artifact rejection
        device_name: Optional name of specific Muse device to connect to
        backend: Bluetooth backend ('bluemuse', 'bleak', or 'auto')
        interface: Optional Bluetooth interface to use
    """
    buffer_length: float = 3.0
    epoch_length: float = 1.0
    overlap_length: float = 0.5
    channels: List[int] = None
    notch_freq: float = 60.0  # Hz (US power line frequency)
    bandpass_range: Tuple[float, float] = (0.5, 100.0)
    artifact_threshold: float = 3.0
    device_name: Optional[str] = None
    backend: str = 'auto'  # 'bluemuse', 'bleak', or 'auto'
    interface: Optional[str] = None  # Bluetooth interface
    
    def __post_init__(self):
        if self.channels is None:
            # Default: left/right forehead (AF7/AF8)
            self.channels = [1, 2]
        self.shift_length = self.epoch_length - self.overlap_length

@dataclass
class BandPowers:
    """Power values for each frequency band.
    
    Attributes:
        delta: Power in delta band (0.5-4 Hz)
        theta: Power in theta band (4-8 Hz)
        alpha: Power in alpha band (8-13 Hz)
        beta: Power in beta band (13-30 Hz)
        gamma: Power in gamma band (30-100 Hz)
    """
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float

    @property
    def as_dict(self) -> Dict[str, float]:
        """Convert band powers to dictionary.
        
        Returns:
            Dictionary mapping band names to power values
        """
        return {
            'delta': self.delta,
            'theta': self.theta,
            'alpha': self.alpha,
            'beta': self.beta,
            'gamma': self.gamma
        }
        
    @property
    def total_power(self) -> float:
        """Calculate total power across all bands.
        
        Returns:
            Sum of power values across all frequency bands
        """
        return sum(self.as_dict.values())
        
    def get_relative_powers(self) -> Dict[str, float]:
        """Calculate relative power for each band.
        
        Returns:
            Dictionary mapping band names to relative power values
        """
        total = self.total_power
        return {
            band: power / total
            for band, power in self.as_dict.items()
        }

class EEGProcessor:
    """Handles real-time EEG data collection and processing.
    
    This class manages the connection to a Muse device via LSL,
    processes the raw EEG data into frequency bands, and provides
    both raw and processed data access.
    
    Attributes:
        config: Configuration settings
        muse: Muse device instance
        inlet: LSL stream inlet
        fs: Sampling frequency
        buffers: Data buffers for raw EEG and band powers
        filter_state: State of the signal filters
        logger: Logging instance
    """

    def __init__(self, config: Optional[EEGConfig] = None):
        """Initialize the EEG processor.
        
        Args:
            config: Optional configuration settings. If None, uses defaults.
        """
        self.config = config or EEGConfig()
        self.muse = None
        self.inlet = None
        self.fs = MUSE_SAMPLING_RATE
        self.buffers = None
        self.filter_state = None
        self._processing = False
        self._callback = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover nearby Muse devices.
        
        Returns:
            List of dictionaries containing device information:
                - name: Device name
                - address: Bluetooth address
                - model: Device model
                
        Note:
            This method uses the muselsl library to scan for nearby Muse
            devices over Bluetooth. Make sure Bluetooth is enabled and
            the device is in pairing mode.
        """
        try:
            muses = list_muses()
            self.logger.info(f"Found {len(muses)} Muse device(s)")
            return muses
        except Exception as e:
            self.logger.error(f"Failed to discover Muse devices: {str(e)}")
            return []

    async def connect(self, address: Optional[str] = None) -> bool:
        """Connect to a Muse device and start LSL streaming.
        
        Args:
            address: Optional Bluetooth address. If None, connects to first available device.
            
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            RuntimeError: If no Muse devices found or LSL stream fails
            
        Note:
            This method will:
            1. Discover nearby Muse devices if no address provided
            2. Connect to the device via Bluetooth
            3. Start LSL streaming
            4. Connect to the LSL stream
            5. Initialize data buffers
        """
        try:
            # Find Muse devices
            if not address and self.config.device_name:
                muses = await self.discover_devices()
                for muse in muses:
                    if muse['name'] == self.config.device_name:
                        address = muse['address']
                        break
            elif not address:
                muses = await self.discover_devices()
                if not muses:
                    raise RuntimeError("No Muse devices found")
                address = muses[0]['address']
            
            # Connect to device
            self.logger.info(f"Connecting to Muse at {address}...")
            self.muse = Muse(
                address,
                backend=self.config.backend,
                interface=self.config.interface
            )
            
            # Start streaming
            stream_params = {
                'ppg_enabled': True,
                'acc_enabled': True,
                'gyro_enabled': True,
                'eeg_disabled': False
            }
            success = stream(
                self.muse,
                **stream_params
            )
            
            if not success:
                raise RuntimeError("Failed to start LSL stream")
            
            # Connect to LSL stream
            streams = resolve_byprop('type', 'EEG', timeout=5.0)
            if not streams:
                raise RuntimeError("No LSL stream found")
            
            self.inlet = StreamInlet(streams[0])
            self.buffers = self._init_buffers()
            
            self.logger.info(
                f"Connected to Muse device\n"
                f"Sampling rate: {self.fs} Hz\n"
                f"Channel count: {len(self.config.channels)}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            return False
            
    async def disconnect(self):
        """Disconnect from the Muse device.
        
        This method will:
        1. Stop the LSL stream
        2. Disconnect from the Muse device
        3. Clean up resources
        """
        if self.muse:
            try:
                self.muse.disconnect()
                self.muse = None
                self.inlet = None
                self.logger.info("Disconnected from Muse device")
            except Exception as e:
                self.logger.error(f"Error disconnecting: {str(e)}")

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

    async def start_monitoring(self, callback: Optional[Callable] = None):
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