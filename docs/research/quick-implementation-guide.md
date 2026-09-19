# Quick Implementation Guide - Neuroscience Research Findings

**Based on**: Comprehensive research synthesis (January 2025)
**Target**: FlowState EEG/Flow State Detection System

---

## Phase 1: Minimum Viable Flow Detector (2-4 weeks)

### Required Components

#### 1. Artifact Rejection
**Choose ONE approach:**

**Option A: Wavelet-ICA (Reliable, Well-Documented)**
```python
# Implementation: wICA Pipeline
from scipy.signal import hilbert, butter, filtfilt
import pywt
from sklearn.decomposition import FastICA

def wavelet_ica_artifact_removal(eeg_data, fs=250):
    # Step 1: Apply ICA
    ica = FastICA(n_components=eeg_data.shape[0])
    ics = ica.fit_transform(eeg_data.T).T

    # Step 2: Wavelet decomposition of each IC
    cleaned_ics = []
    for ic in ics:
        coeffs = pywt.wavedec(ic, 'db4', level=5)

        # Step 3: Threshold based on kurtosis
        kurt = scipy.stats.kurtosis(ic)
        if abs(kurt) > 3.5:  # Artifact detected
            coeffs_thresh = [pywt.threshold(c, value='universal', mode='soft')
                             for c in coeffs]
            ic_clean = pywt.waverec(coeffs_thresh, 'db4')
        else:
            ic_clean = ic

        cleaned_ics.append(ic_clean)

    # Step 4: Reconstruct EEG
    eeg_clean = ica.inverse_transform(np.array(cleaned_ics).T).T
    return eeg_clean

# Parameters
wavelet_params = {
    'wavelet': 'db4',           # Daubechies 4
    'level': 5,                  # Decomposition levels
    'threshold': 'universal',
    'kurtosis_threshold': 3.5
}
```

**Option B: Deep Learning (State-of-Art, Requires Training Data)**
```python
# Placeholder for AnEEG-style deep learning
# Requires pre-trained model or training dataset
# Target latency: <5ms per 4-second window

# If implementing from scratch:
# 1. Collect paired clean/artifact EEG data
# 2. Train autoencoder architecture
# 3. Deploy with TensorFlow Lite for mobile
# 4. Validate SNR improvement >10dB
```

---

#### 2. Flow State Features

**Extract These Features Every 2 Seconds:**

```python
def extract_flow_features(eeg_clean, fs=250):
    """
    Extract multi-feature flow indicators
    """
    features = {}

    # 1. Frontal Theta Power (4-8 Hz)
    theta_channels = ['Fz', 'F3', 'F4']
    theta_power = []
    for ch in theta_channels:
        power = bandpower(eeg_clean[ch], (4, 8), fs)
        theta_power.append(power)
    features['frontal_theta'] = np.mean(theta_power)

    # 2. Frontocentral Alpha Power (8-13 Hz)
    alpha_channels = ['FCz', 'Cz']
    alpha_power = []
    for ch in alpha_channels:
        power = bandpower(eeg_clean[ch], (8, 13), fs)
        alpha_power.append(power)
    features['frontocentral_alpha'] = np.mean(alpha_power)

    # 3. Theta/Alpha Ratio
    features['theta_alpha_ratio'] = features['frontal_theta'] / features['frontocentral_alpha']

    return features

def bandpower(data, band, fs, method='welch'):
    """
    Calculate power in frequency band using Welch's method
    """
    from scipy.signal import welch
    freqs, psd = welch(data, fs, nperseg=fs*2)
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx_band], freqs[idx_band])
```

---

#### 3. Baseline Calibration

**Run Once Per User/Session:**

```python
def calibrate_baseline(eeg_data, duration=300, fs=250):
    """
    Calibrate individual baseline (5 minutes eyes-open rest)

    Args:
        eeg_data: Resting state EEG (channels x samples)
        duration: Calibration duration in seconds (default: 300)
        fs: Sampling frequency (default: 250 Hz)

    Returns:
        baseline_features: Dictionary of baseline values
    """
    # Extract features from baseline period
    baseline_features = extract_flow_features(eeg_data, fs)

    # Identify individual alpha frequency (IAF)
    alpha_band = (8, 13)
    freqs, psd = welch(eeg_data['Cz'], fs, nperseg=fs*2)
    idx_alpha = np.logical_and(freqs >= alpha_band[0], freqs <= alpha_band[1])
    iaf = freqs[idx_alpha][np.argmax(psd[idx_alpha])]

    baseline_features['individual_alpha_frequency'] = iaf

    return baseline_features
```

---

#### 4. Real-Time Flow Classification

```python
class MinimalFlowDetector:
    def __init__(self, baseline_features):
        self.baseline = baseline_features
        self.buffer = []  # 2-second sliding window

    def process_realtime(self, eeg_chunk):
        """
        Process 2-second EEG chunk for flow detection
        """
        # Step 1: Artifact removal
        eeg_clean = wavelet_ica_artifact_removal(eeg_chunk)

        # Step 2: Extract features
        features = extract_flow_features(eeg_clean)

        # Step 3: Normalize to baseline
        normalized = {
            'theta_change': (features['frontal_theta'] - self.baseline['frontal_theta'])
                            / self.baseline['frontal_theta'],
            'alpha_stability': abs(features['frontocentral_alpha'] - self.baseline['frontocentral_alpha'])
                               / self.baseline['frontocentral_alpha'],
            'ta_ratio': features['theta_alpha_ratio'],
        }

        # Step 4: Simple flow classification
        flow_score = self.classify_flow(normalized)

        return {
            'flow_state': flow_score > 0.6,
            'flow_score': flow_score,
            'features': features,
            'normalized': normalized
        }

    def classify_flow(self, normalized_features):
        """
        Simple weighted flow score (0-1)
        """
        # Flow indicators (based on research):
        # - Moderate theta increase (not too high)
        # - Stable alpha (not suppressed, not elevated)
        # - Optimal theta/alpha ratio

        theta_score = 1.0 if 0.1 < normalized['theta_change'] < 0.4 else 0.5
        alpha_score = 1.0 if normalized['alpha_stability'] < 0.2 else 0.5
        ratio_score = 1.0 if 0.8 < normalized['ta_ratio'] < 1.5 else 0.5

        # Weighted average
        flow_score = (0.4 * theta_score +
                      0.3 * alpha_score +
                      0.3 * ratio_score)

        return flow_score
```

---

### Usage Example

```python
# Setup
fs = 250  # Hz sampling rate

# 1. Calibration phase (5 minutes resting)
baseline_eeg = record_eeg(duration=300, state='eyes_open_rest')
baseline_features = calibrate_baseline(baseline_eeg, duration=300, fs=fs)

# 2. Create detector
detector = MinimalFlowDetector(baseline_features)

# 3. Real-time monitoring (2-second chunks)
while task_active:
    eeg_chunk = record_eeg(duration=2)  # 2-second window
    result = detector.process_realtime(eeg_chunk)

    print(f"Flow State: {result['flow_state']}")
    print(f"Flow Score: {result['flow_score']:.2f}")

    # Optional: Log for validation
    log_flow_data(result, timestamp=time.time())
```

---

## Phase 2: Enhanced Features (4-6 weeks)

### Add These Once Phase 1 is Working

#### 1. DMN Suppression Index

```python
def calculate_dmn_suppression(eeg_data, baseline_alpha):
    """
    Calculate DMN suppression from midline alpha
    """
    midline_channels = ['Fz', 'Cz', 'Pz']
    alpha_band = (8, 13)

    task_alpha = []
    for ch in midline_channels:
        power = bandpower(eeg_data[ch], alpha_band, fs=250)
        task_alpha.append(power)

    task_alpha_mean = np.mean(task_alpha)

    # Suppression index (higher = more suppression = potential flow)
    suppression = (baseline_alpha - task_alpha_mean) / baseline_alpha

    return suppression

# Integration into classifier
def enhanced_flow_score(normalized_features, dmn_suppression):
    flow_score = (
        0.25 * theta_score +
        0.20 * alpha_score +
        0.20 * ratio_score +
        0.35 * (1.0 if dmn_suppression > 0.3 else 0.5)  # NEW
    )
    return flow_score
```

---

#### 2. Theta-Gamma Phase-Amplitude Coupling

```python
def calculate_theta_gamma_pac(eeg_data, fs=250):
    """
    Calculate theta-gamma phase-amplitude coupling
    """
    from scipy.signal import hilbert

    # Extract theta phase (4-8 Hz)
    theta_filtered = bandpass_filter(eeg_data, (4, 8), fs)
    theta_analytic = hilbert(theta_filtered)
    theta_phase = np.angle(theta_analytic)

    # Extract gamma amplitude (30-80 Hz)
    gamma_filtered = bandpass_filter(eeg_data, (30, 80), fs)
    gamma_analytic = hilbert(gamma_filtered)
    gamma_amplitude = np.abs(gamma_analytic)

    # Bin phase into 18 bins (20° each)
    n_bins = 18
    phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)

    binned_amplitude = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (theta_phase >= phase_bins[i]) & (theta_phase < phase_bins[i+1])
        binned_amplitude[i] = np.mean(gamma_amplitude[mask])

    # Normalize
    amp_dist = binned_amplitude / np.sum(binned_amplitude)

    # Calculate Modulation Index
    MI = 0
    for p in amp_dist:
        if p > 0:
            MI += p * np.log(p / (1/n_bins))
    MI /= np.log(n_bins)

    return MI

def bandpass_filter(data, band, fs):
    from scipy.signal import butter, filtfilt
    nyq = fs / 2
    low = band[0] / nyq
    high = band[1] / nyq
    b, a = butter(4, [low, high], btype='band')
    return filtfilt(b, a, data)
```

---

#### 3. Isochronic Tone Entrainment

```python
def generate_isochronic_tone(duration=240, carrier_freq=250,
                              modulation_freq=10, fs=44100):
    """
    Generate isochronic tone for brainwave entrainment

    Args:
        duration: Session duration in seconds (default: 4 minutes)
        carrier_freq: Carrier frequency in Hz (default: 250)
        modulation_freq: Target brain frequency (default: 10 Hz alpha)
        fs: Audio sampling rate (default: 44100 Hz)

    Returns:
        audio: Isochronic tone audio signal
    """
    t = np.linspace(0, duration, int(duration * fs))

    # Carrier wave
    carrier = np.sin(2 * np.pi * carrier_freq * t)

    # Modulation envelope (square wave for isochronic)
    modulation = (np.sign(np.sin(2 * np.pi * modulation_freq * t)) + 1) / 2

    # Apply envelope
    isochronic = carrier * modulation

    # Normalize
    isochronic = isochronic / np.max(np.abs(isochronic)) * 0.8

    return isochronic

# Usage
alpha_tone = generate_isochronic_tone(duration=240, carrier_freq=250,
                                       modulation_freq=10)  # 10 Hz alpha

# Play during task to enhance alpha entrainment
# Validate by monitoring alpha power increase in real-time
```

---

## Validation Protocol

### Data Collection During Development

```python
class FlowValidationLogger:
    def __init__(self, output_dir='validation_data'):
        self.output_dir = output_dir
        self.session_data = []

    def log_measurement(self, eeg_features, subjective_rating,
                        task_performance, timestamp):
        """
        Log comprehensive validation data
        """
        measurement = {
            'timestamp': timestamp,

            # EEG features
            'frontal_theta': eeg_features['frontal_theta'],
            'frontocentral_alpha': eeg_features['frontocentral_alpha'],
            'theta_alpha_ratio': eeg_features['theta_alpha_ratio'],
            'flow_score': eeg_features.get('flow_score', None),

            # Ground truth
            'subjective_flow': subjective_rating,  # 1-10 scale
            'task_accuracy': task_performance['accuracy'],
            'task_speed': task_performance['speed'],
            'errors': task_performance['errors'],
        }

        self.session_data.append(measurement)

    def save_session(self, session_id):
        """
        Save session data for offline analysis
        """
        df = pd.DataFrame(self.session_data)
        df.to_csv(f'{self.output_dir}/session_{session_id}.csv', index=False)

        # Clear for next session
        self.session_data = []

    def analyze_correlation(self):
        """
        Analyze EEG features vs subjective flow
        """
        df = pd.DataFrame(self.session_data)

        # Correlation analysis
        correlations = df.corr()['subjective_flow'].drop('subjective_flow')

        print("Feature-Flow Correlations:")
        print(correlations.sort_values(ascending=False))

        return correlations

# Usage
logger = FlowValidationLogger()

# During task, every 2-3 minutes:
while task_running:
    # Collect EEG features
    features = detector.process_realtime(eeg_chunk)

    # Get subjective rating (every 2-3 min)
    if time_for_rating():
        rating = prompt_user_flow_rating()  # 1-10 scale
        performance = get_current_task_performance()

        logger.log_measurement(features['features'], rating,
                               performance, time.time())

# End of session
logger.save_session(session_id)
logger.analyze_correlation()
```

---

### Validation Metrics to Track

```python
def evaluate_flow_detector(predictions, ground_truth):
    """
    Evaluate flow detector performance

    Args:
        predictions: Binary flow predictions (0/1)
        ground_truth: Subjective flow ratings (1-10) or binary

    Returns:
        metrics: Dictionary of performance metrics
    """
    from sklearn.metrics import accuracy_score, precision_score, recall_score

    # If ground truth is continuous (1-10), threshold at 6
    if np.max(ground_truth) > 1:
        ground_truth_binary = (ground_truth >= 6).astype(int)
    else:
        ground_truth_binary = ground_truth

    metrics = {
        'accuracy': accuracy_score(ground_truth_binary, predictions),
        'sensitivity': recall_score(ground_truth_binary, predictions),
        'specificity': recall_score(1 - ground_truth_binary, 1 - predictions),
        'precision': precision_score(ground_truth_binary, predictions),
    }

    # Check against targets
    print("Target vs Actual:")
    print(f"Sensitivity: >0.80 → {metrics['sensitivity']:.2f}")
    print(f"Specificity: >0.75 → {metrics['specificity']:.2f}")

    return metrics
```

---

## Quick Reference: Key Parameters

### Frequency Bands
```python
bands = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 80),
    'low_gamma': (30, 60),
    'high_gamma': (60, 80),
}
```

### Electrodes for Flow Detection
```python
electrodes = {
    'frontal_theta': ['Fz', 'F3', 'F4'],
    'frontocentral_alpha': ['FCz', 'Cz'],
    'dmn_midline': ['Fz', 'Cz', 'Pz'],
}
```

### Thresholds
```python
thresholds = {
    'flow_score': 0.6,           # Minimum for flow state
    'dmn_suppression': 0.3,      # 30% alpha reduction
    'theta_increase': (0.1, 0.4), # 10-40% above baseline
    'alpha_stability': 0.2,      # Within 20% of baseline
}
```

### Timing
```python
timing = {
    'baseline_calibration': 300,  # seconds (5 minutes)
    'processing_window': 2,       # seconds (real-time chunks)
    'subjective_rating_interval': 150,  # seconds (2-3 minutes)
    'entrainment_session': 240,   # seconds (4 minutes)
}
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Insufficient Baseline
**Problem**: Using single baseline for all tasks/sessions
**Solution**: Recalibrate baseline for each session and task type

### Pitfall 2: Single Feature Dependency
**Problem**: Relying only on frontal theta
**Solution**: Always use multi-feature weighted approach

### Pitfall 3: Ignoring Individual Variability
**Problem**: Fixed frequency bands for all users
**Solution**: Identify individual alpha frequency (IAF) during calibration

### Pitfall 4: No Ground Truth Validation
**Problem**: Trusting EEG features without validation
**Solution**: Always collect subjective flow ratings + task performance

### Pitfall 5: Real-Time Artifacts
**Problem**: Moving, blinking during EEG recording
**Solution**: Robust artifact rejection (wICA or deep learning)

---

## Next Steps After Implementation

1. **Collect Validation Data** (2-3 weeks)
   - 10+ users, 5+ sessions each
   - Diverse tasks (creative, cognitive, athletic)
   - Full validation logging

2. **Analyze & Refine** (1-2 weeks)
   - Feature-flow correlations
   - Optimal weight tuning
   - Individual vs population models

3. **Iterate to Phase 2** (4-6 weeks)
   - Add DMN suppression index
   - Integrate theta-gamma PAC
   - Deploy isochronic entrainment
   - Advanced multi-feature classifier

4. **Production Optimization** (2-3 weeks)
   - Mobile deployment (if applicable)
   - Latency optimization
   - User experience refinement

---

## Resources

**Full Research Report**: `/home/kvn/workspace/evolve/repos/FlowState/docs/research/neuroscience-findings.md`

**Key Libraries**:
- **Signal Processing**: scipy, numpy
- **EEG Analysis**: mne (optional but recommended)
- **Wavelet Transform**: pywt
- **ICA**: sklearn.decomposition.FastICA
- **Deep Learning**: tensorflow/pytorch (for Phase 2+)

**Validation Tools**:
- **Flow Measurement**: Flow Short Scale questionnaire
- **Performance Tracking**: Task-specific metrics
- **Statistical Analysis**: pandas, sklearn.metrics

---

**Document Status**: Ready for implementation
**Last Updated**: 2025-01-08
**Confidence**: High (85%) based on peer-reviewed research
