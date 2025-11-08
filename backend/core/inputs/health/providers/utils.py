"""Utility functions for EEG data processing."""

import numpy as np
from scipy import signal
from typing import Tuple, Optional, Any


def update_buffer(buffer: np.ndarray, new_data: np.ndarray,
                  notch: bool = False, filter_state: Optional[Any] = None) -> Tuple[np.ndarray, Any]:
    """Update a circular buffer with new data.

    Args:
        buffer: Existing buffer array
        new_data: New data to append
        notch: Whether to apply notch filter (not implemented yet)
        filter_state: Filter state (not used yet)

    Returns:
        Updated buffer and filter state
    """
    # Simple circular buffer update
    if len(new_data.shape) == 1:
        new_data = new_data.reshape(-1, 1)

    # Shift buffer and add new data
    buffer_size = buffer.shape[0]
    new_size = new_data.shape[0]

    if new_size >= buffer_size:
        # If new data is larger than buffer, take the last buffer_size samples
        buffer = new_data[-buffer_size:]
    else:
        # Shift existing data and append new
        buffer[:-new_size] = buffer[new_size:]
        buffer[-new_size:] = new_data

    return buffer, filter_state


def get_last_data(buffer: np.ndarray, n_samples: int) -> np.ndarray:
    """Get the last n samples from the buffer.

    Args:
        buffer: Data buffer
        n_samples: Number of samples to retrieve

    Returns:
        Last n samples from buffer
    """
    return buffer[-n_samples:].flatten()


def compute_PSD(data: np.ndarray, fs: float) -> np.ndarray:
    """Compute Power Spectral Density for EEG frequency bands.

    Args:
        data: EEG data
        fs: Sampling frequency

    Returns:
        Array of band powers [delta, theta, alpha, beta, gamma]
    """
    # Define frequency bands
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 100)
    }

    # Compute power spectral density using Welch's method
    freqs, psd = signal.welch(data, fs, nperseg=min(256, len(data)))

    # Calculate band powers
    band_powers = []
    for band_name in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
        low, high = bands[band_name]
        # Find frequency indices
        idx = np.logical_and(freqs >= low, freqs <= high)
        # Calculate average power in band
        band_power = np.mean(psd[idx]) if np.any(idx) else 0.0
        band_powers.append(band_power)

    return np.array(band_powers)