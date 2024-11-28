"""Strobe Glasses Hardware Interface.

This module controls the strobe glasses hardware, synchronizing the strobing
patterns with EEG rhythms for optimal neural entrainment and cross-hemisphere synchronization.

Hardware Requirements:
    - Strobe glasses with independent left/right control
    - PWM control for each side
    - USB or Bluetooth connectivity
    - Minimum 1000Hz refresh rate
"""

from dataclasses import dataclass
import asyncio
import serial
import logging
from typing import Optional, Tuple
import numpy as np
from visual.visual_processor import VisualStimulator

@dataclass
class StrobeConfig:
    """Configuration for strobe glasses."""
    min_frequency: float = 1.0   # Hz
    max_frequency: float = 50.0  # Hz
    min_intensity: float = 0.0   # 0-1
    max_intensity: float = 1.0   # 0-1
    pwm_frequency: int = 10000   # Hz
    phase_precision: float = 0.001  # Phase precision in radians

class StrobeGlasses:
    """Interface for controlling strobe glasses hardware with bilateral stimulation."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baud_rate: int = 115200):
        """Initialize strobe glasses connection.
        
        Args:
            port: Serial port for glasses
            baud_rate: Serial baud rate
        """
        self.port = port
        self.baud_rate = baud_rate
        self.config = StrobeConfig()
        self.serial: Optional[serial.Serial] = None
        self.visual_stim = VisualStimulator(sampling_rate=self.config.pwm_frequency)
        self._running = False
        
    async def connect(self) -> bool:
        """Establish connection to strobe glasses.
        
        Returns:
            True if connection successful
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            logging.info(f"Connected to strobe glasses on {self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to strobe glasses: {str(e)}")
            return False
            
    async def disconnect(self):
        """Disconnect from strobe glasses."""
        if self.serial:
            self.serial.close()
            self.serial = None
        self._running = False
        
    async def set_bilateral_strobing(self, 
                                   left_freq: float,
                                   right_freq: float,
                                   phase_diff: float = 0.0,
                                   intensity: float = 1.0,
                                   duration: float = 0.0):
        """Set independent strobing patterns for left and right eyes.
        
        Args:
            left_freq: Left eye strobe frequency in Hz
            right_freq: Right eye strobe frequency in Hz
            phase_diff: Phase difference between eyes in radians
            intensity: Light intensity (0-1)
            duration: Pattern duration in seconds (0 for continuous)
        """
        if not self.serial:
            raise RuntimeError("Not connected to strobe glasses")
            
        # Clamp frequencies and intensity
        left_freq = np.clip(left_freq, 
                          self.config.min_frequency,
                          self.config.max_frequency)
        right_freq = np.clip(right_freq,
                           self.config.min_frequency,
                           self.config.max_frequency)
        intensity = np.clip(intensity,
                          self.config.min_intensity,
                          self.config.max_intensity)
                          
        # Convert to PWM values with phase difference
        left_period = int(self.config.pwm_frequency / left_freq)
        right_period = int(self.config.pwm_frequency / right_freq)
        
        # Calculate phase-shifted duty cycles
        left_duty = int(left_period * intensity)
        right_duty = int(right_period * intensity)
        phase_shift = int(right_period * phase_diff / (2 * np.pi))
        
        # Send bilateral command to glasses
        command = f"BILATERAL {left_period} {left_duty} {right_period} {right_duty} {phase_shift}\n"
        self.serial.write(command.encode())
        
    async def set_alternating_pattern(self, 
                                    base_freq: float,
                                    alt_freq: float,
                                    pattern_duration: float = 1.0):
        """Generate alternating bilateral stimulation pattern.
        
        Args:
            base_freq: Base frequency for alternation in Hz
            alt_freq: Alternation frequency between eyes in Hz
            pattern_duration: Duration of each alternation cycle in seconds
        """
        if not self.serial:
            raise RuntimeError("Not connected to strobe glasses")
            
        # Calculate number of samples for the pattern
        num_samples = int(pattern_duration * self.config.pwm_frequency)
        
        # Generate alternating pattern
        t = np.linspace(0, pattern_duration, num_samples)
        envelope = 0.5 * (1 + np.sin(2 * np.pi * alt_freq * t))
        
        # Create complementary patterns for each eye
        left_pattern = envelope * np.sin(2 * np.pi * base_freq * t)
        right_pattern = (1 - envelope) * np.sin(2 * np.pi * base_freq * t)
        
        # Convert to PWM values (0-255)
        left_pwm = ((left_pattern + 1) * 127.5).astype(np.uint8)
        right_pwm = ((right_pattern + 1) * 127.5).astype(np.uint8)
        
        # Send alternating pattern command
        command = f"ALT_PATTERN {num_samples}\n"
        self.serial.write(command.encode())
        self.serial.write(left_pwm.tobytes())
        self.serial.write(right_pwm.tobytes())
        
    async def set_synchronized_pattern(self, 
                                     frequencies: Tuple[float, float],
                                     eeg_phase: float,
                                     duration: float = 0.1):
        """Set EEG-synchronized strobing pattern with cross-frequency coupling.
        
        Args:
            frequencies: Tuple of (carrier_freq, modulation_freq) in Hz
            eeg_phase: Current EEG phase in radians for synchronization
            duration: Pattern duration in seconds
        """
        if not self.serial:
            raise RuntimeError("Not connected to strobe glasses")
            
        carrier_freq, mod_freq = frequencies
        
        # Generate synchronized pattern using visual stimulator
        pattern = self.visual_stim.generate_flicker(
            duration=duration,
            carrier_freq=carrier_freq,
            mod_freq=mod_freq,
            phase=eeg_phase
        )
        
        # Apply cross-frequency coupling
        t = np.linspace(0, duration, len(pattern))
        mod_pattern = 0.5 * (1 + np.cos(2 * np.pi * mod_freq * t + eeg_phase))
        pattern = pattern * mod_pattern
        
        # Convert to PWM values (0-255)
        pwm_values = (np.clip(pattern, 0, 1) * 255).astype(np.uint8)
        
        # Send synchronized pattern to glasses
        command = f"SYNC_PATTERN {len(pwm_values)}\n"
        self.serial.write(command.encode())
        self.serial.write(pwm_values.tobytes())
        
    async def start_entrainment(self, eeg_phase: float):
        """Start neural entrainment based on EEG phase.
        
        Args:
            eeg_phase: Current EEG phase in radians
        """
        if not self.serial:
            raise RuntimeError("Not connected to strobe glasses")
            
        self._running = True
        
        try:
            while self._running:
                # Generate 100ms of bilateral stimulation
                await self.set_synchronized_pattern(
                    frequencies=(40.0, 10.0),  # Gamma carrier with alpha modulation
                    eeg_phase=eeg_phase,
                    duration=0.1
                )
                
                # Wait for optimal timing
                delay = self.visual_stim.sync_with_eeg(eeg_phase)
                await asyncio.sleep(delay)
                
        except Exception as e:
            logging.error(f"Error in entrainment: {str(e)}")
            self._running = False
            
    async def stop_entrainment(self):
        """Stop neural entrainment."""
        self._running = False
        # Turn off strobing for both eyes
        await self.set_bilateral_strobing(0, 0, intensity=0)
