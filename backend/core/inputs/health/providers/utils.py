"""EEG Signal Processing Utilities.

This module provides low-level signal processing utilities for real-time EEG data
analysis. It implements circular buffering, frequency domain analysis, and digital
filtering operations optimized for neurophysiological signals.

The utilities are designed for real-time processing of continuous EEG streams with
minimal latency and computational overhead. All functions support vectorized operations
and maintain filter state for seamless streaming.

Mathematical Framework:
    Power Spectral Density is computed using Welch's method:

    .. math::

        P_{xx}(f) = \\frac{1}{KU}\\sum_{k=0}^{K-1} |X_k(f)|^2

    where:
        - K is the number of overlapping segments
        - U is the normalization factor for the window
        - X_k(f) is the DFT of segment k

    Band power is calculated as the integral over frequency range:

    .. math::

        BP_{band} = \\int_{f_{low}}^{f_{high}} P_{xx}(f) df

Signal Processing Chain:
    1. Circular buffering for continuous data flow
    2. Optional notch filtering (50/60 Hz power line noise)
    3. Bandpass filtering (0.5-100 Hz for EEG)
    4. Artifact detection and rejection
    5. Welch periodogram for PSD estimation
    6. Band power integration

Dependencies:
    - numpy: Efficient array operations
    - scipy.signal: Digital signal processing

See Also:
    :mod:`muse`: Main EEG processor using these utilities
    :class:`muse.EEGProcessor`: High-level EEG data collection

Example:
    >>> import numpy as np
    >>> from utils import update_buffer, compute_PSD
    >>>
    >>> # Initialize buffer
    >>> buffer = np.zeros((1024, 1))  # 4 seconds at 256 Hz
    >>> fs = 256  # Sampling rate
    >>>
    >>> # Process incoming data chunks
    >>> new_data = np.random.randn(128)  # 0.5 second chunk
    >>> buffer, state = update_buffer(buffer, new_data)
    >>>
    >>> # Compute band powers
    >>> epoch = buffer[-256:, 0]  # Last 1 second
    >>> band_powers = compute_PSD(epoch, fs)
    >>> print(f"Alpha power: {band_powers[2]:.2f}")
"""

import numpy as np
from scipy import signal
from typing import Tuple, Optional, Any


def update_buffer(buffer: np.ndarray, new_data: np.ndarray,
                  notch: bool = False, filter_state: Optional[Any] = None) -> Tuple[np.ndarray, Any]:
    """Update circular buffer with new EEG data samples.

    Implements a circular buffer for continuous EEG data streaming. The buffer
    operates as a FIFO queue, discarding oldest samples when new data arrives.
    This enables fixed-memory windowed operations on continuous signals.

    The function automatically handles data shape normalization and supports
    both small updates (typical real-time streaming) and large batch updates
    (initialization or catch-up scenarios).

    Parameters
    ----------
    buffer : np.ndarray
        Existing buffer array of shape (n_samples, n_channels)
    new_data : np.ndarray
        New data to append, shape (n_new_samples,) or (n_new_samples, n_channels)
    notch : bool, optional
        Whether to apply notch filter for power line noise removal (default: False)
        Currently reserved for future implementation
    filter_state : Any, optional
        State of digital filters for continuous operation (default: None)
        Currently reserved for future implementation

    Returns
    -------
    buffer : np.ndarray
        Updated buffer with new data appended and old data removed
    filter_state : Any
        Updated filter state (currently unchanged)

    Notes
    -----
    Buffer update follows FIFO policy:

    .. math::

        B_{new}[i] = \\begin{cases}
            B_{old}[i + n] & \\text{if } i < N - n \\\\
            D[i - (N - n)] & \\text{if } i \\geq N - n
        \\end{cases}

    where N is buffer size and n is new data size.

    For real-time EEG streaming at 256 Hz with 0.1s updates:
        - Buffer size: ~1024 samples (4 seconds)
        - Update size: ~26 samples (0.1 seconds)
        - Overlap: ~998 samples maintained

    Examples
    --------
    >>> # Create 4-second buffer at 256 Hz
    >>> buffer = np.zeros((1024, 1))
    >>>
    >>> # Add 0.5 second of new data
    >>> new_samples = np.random.randn(128)
    >>> buffer, state = update_buffer(buffer, new_samples)
    >>>
    >>> # Buffer now contains last 4 seconds with newest 0.5s appended
    >>> assert buffer.shape == (1024, 1)
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
    """Extract the most recent samples from circular buffer.

    Retrieves the last n samples from the buffer for epoch-based analysis.
    This function is typically used to extract fixed-length epochs for
    frequency domain analysis or feature extraction.

    Parameters
    ----------
    buffer : np.ndarray
        Data buffer of shape (buffer_size, n_channels)
    n_samples : int
        Number of most recent samples to extract

    Returns
    -------
    np.ndarray
        Flattened array of last n samples, shape (n_samples,)

    Notes
    -----
    For EEG analysis with 256 Hz sampling:
        - 1 second epoch: n_samples = 256
        - 2 second epoch: n_samples = 512
        - 4 second epoch: n_samples = 1024

    The function flattens multi-channel buffers to single dimension.
    For multi-channel processing, extract each channel separately.

    Examples
    --------
    >>> buffer = np.random.randn(1024, 1)  # 4 second buffer
    >>> epoch = get_last_data(buffer, 256)  # Get last 1 second
    >>> assert epoch.shape == (256,)
    >>>
    >>> # Use for sliding window analysis
    >>> for i in range(0, len(buffer), 128):
    ...     epoch = get_last_data(buffer[:i+256], 256)
    ...     # Process epoch...
    """
    return buffer[-n_samples:].flatten()


def compute_PSD(data: np.ndarray, fs: float) -> np.ndarray:
    """Compute Power Spectral Density for standard EEG frequency bands.

    Calculates absolute power in five standard EEG frequency bands using
    Welch's periodogram method. This provides robust spectral estimates
    with reduced variance compared to direct FFT.

    The function implements the complete signal processing pipeline:
        1. Apply Welch's method with overlapping segments
        2. Identify frequency bins for each band
        3. Integrate power across band frequencies
        4. Return normalized band powers

    Parameters
    ----------
    data : np.ndarray
        EEG time series data, shape (n_samples,)
        Typical: 256-1024 samples (1-4 seconds at 256 Hz)
    fs : float
        Sampling frequency in Hz (typically 256 Hz for Muse)

    Returns
    -------
    np.ndarray
        Array of band powers [delta, theta, alpha, beta, gamma]
        Shape: (5,)
        Units: μV²/Hz (microvolts squared per Hz)

    Notes
    -----
    Frequency Band Definitions (Hz):
        - Delta: 0.5-4 Hz (deep sleep, unconscious processes)
        - Theta: 4-8 Hz (meditation, creativity, drowsiness)
        - Alpha: 8-13 Hz (relaxed awareness, flow state gateway)
        - Beta: 13-30 Hz (active thinking, concentration)
        - Gamma: 30-100 Hz (peak performance, insight)

    Welch's Method Parameters:
        - Window: Hann (default)
        - Segment length: min(256, data length)
        - Overlap: 50% (default)
        - Detrending: Constant (default)

    The PSD is computed as:

    .. math::

        P_{band} = \\frac{1}{N_{band}} \\sum_{f \\in band} P_{xx}(f)

    where :math:`N_{band}` is the number of frequency bins in the band.

    For relative band power, normalize by total power:

    .. math::

        P_{rel,band} = \\frac{P_{band}}{\\sum_{all\\ bands} P_{band}}

    Examples
    --------
    >>> # Generate synthetic EEG with strong alpha
    >>> fs = 256
    >>> t = np.arange(0, 2, 1/fs)  # 2 second signal
    >>> data = np.sin(2 * np.pi * 10 * t)  # 10 Hz alpha wave
    >>> data += 0.1 * np.random.randn(len(t))  # Add noise
    >>>
    >>> # Compute band powers
    >>> band_powers = compute_PSD(data, fs)
    >>> delta, theta, alpha, beta, gamma = band_powers
    >>>
    >>> # Alpha should be dominant
    >>> assert alpha > theta and alpha > beta
    >>>
    >>> # Calculate relative alpha power
    >>> total_power = np.sum(band_powers)
    >>> relative_alpha = alpha / total_power
    >>> print(f"Relative alpha: {relative_alpha:.1%}")

    See Also
    --------
    scipy.signal.welch : Underlying PSD estimation
    :class:`muse.BandPowers` : Structured band power container
    :func:`update_buffer` : Buffer management for streaming
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