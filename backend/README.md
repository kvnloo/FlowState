# FlowState Backend

The backend service for FlowState - a Brain-Computer Interface (BCI) application that optimizes flow states through real-time EEG neurofeedback.

## Overview

This backend service handles:
- Real-time EEG signal processing from Muse headbands via LSL protocol
- Flow state detection using advanced algorithms
- Binaural beat generation for brainwave entrainment
- WebSocket communication with the frontend
- Data persistence and session management

## Prerequisites

- Python 3.14 or higher
- Pipenv for dependency management
- Muse headband (Muse 2, Muse S, or original Muse)
- BlueMuse (Windows) or muselsl (Linux/macOS) for device connectivity

## Installation

```bash
# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Install development dependencies (optional)
pipenv install --dev
```

## Project Structure

```
backend/
├── api/                  # API endpoints and WebSocket handlers
│   ├── eeg_endpoints.py # EEG data streaming endpoints
│   ├── health/          # Health check endpoints
│   └── middleware/      # Request/response middleware
├── core/                # Core business logic
│   ├── algorithms/      # Flow state detection algorithms
│   ├── models/          # Data models
│   ├── research/        # Research implementations
│   └── utils/           # Utility functions
├── mlops/               # Machine learning operations
├── quantum/             # Quantum computing integrations
├── main.py              # Application entry point
├── Pipfile              # Dependencies specification
└── Pipfile.lock         # Locked dependencies
```

## Running the Backend

### Development Mode
```bash
# Start the backend server
pipenv run python main.py

# Or with hot-reload
pipenv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Using Gunicorn
pipenv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Configuration

Configuration is managed through environment variables and `config.yaml`:

```yaml
# Example config.yaml
eeg:
  sample_rate: 256
  channels: 4
  buffer_size: 512

flow_detection:
  alpha_threshold: 0.7
  theta_threshold: 0.6
  update_frequency: 10  # Hz

audio:
  binaural_beats: true
  frequency_range: [8, 12]  # Alpha range
```

## API Documentation

### WebSocket Endpoints

#### `/ws/eeg`
Real-time EEG data streaming
- Receives: Raw EEG signals from Muse device
- Sends: Processed EEG data and flow state metrics

#### `/ws/audio`
Binaural beat control
- Receives: Audio control commands
- Sends: Frequency adjustments and entrainment parameters

### REST Endpoints

#### `GET /health`
Health check endpoint
- Returns: Server status and system metrics

#### `POST /session/start`
Start a new flow session
- Body: User preferences and calibration data
- Returns: Session ID and initial configuration

#### `GET /session/{session_id}/metrics`
Get session metrics
- Returns: Flow scores, duration, stability metrics

## Core Algorithms

### Flow State Detection
The system uses multiple algorithms for flow state detection:

1. **Power Spectral Density Analysis**: Monitors alpha/theta ratios
2. **Entropy-Based Detection**: Measures signal complexity
3. **Cross-Hemisphere Synchronization**: Analyzes bilateral coherence
4. **Machine Learning Models**: Personalized flow state prediction

### Binaural Beat Generation
Dynamic frequency generation based on current brainwave state:
- Alpha entrainment (8-12 Hz) for relaxed focus
- Theta entrainment (4-8 Hz) for deep flow
- Gamma bursts (30-50 Hz) for cognitive enhancement

## Testing

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov=backend

# Run specific test suite
pipenv run pytest tests/test_flow_detection.py
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Document all public APIs with docstrings

### Adding New Features
1. Create feature branch from `dev`
2. Implement with tests
3. Update documentation
4. Submit pull request

### Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
pipenv run python main.py

# Use debugger
pipenv run python -m pdb main.py
```

## Troubleshooting

### Common Issues

**Muse Connection Failed**
- Ensure Bluetooth is enabled
- Check BlueMuse/muselsl is running
- Verify device is powered on and in range

**LSL Stream Not Found**
- Restart the Muse streaming application
- Check firewall settings
- Verify LSL protocol version compatibility

**High Latency**
- Reduce buffer size in configuration
- Check CPU usage and system resources
- Consider using compiled Cython extensions

## Performance Optimization

- Uses NumPy for efficient signal processing
- Implements sliding window buffers for real-time analysis
- Utilizes multiprocessing for parallel algorithm execution
- Caches frequently accessed computations

## Security

- All WebSocket connections use authentication tokens
- Session data encrypted at rest
- No PII stored without explicit consent
- Regular security audits and dependency updates

## Contributing

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/kvnloo/FlowState/issues
- Documentation: https://kvnloo.github.io/FlowState/