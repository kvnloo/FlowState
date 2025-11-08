# FlowState Frontend

The frontend application for FlowState - providing real-time visualization and user interaction for flow state optimization.

## Overview

This React-based frontend provides:
- Real-time EEG signal visualization
- Flow state indicators and metrics
- Interactive controls for binaural beats
- Session management and progress tracking
- Data export and analytics dashboard

## Prerequisites

- Node.js 18.0 or higher
- npm 9.0 or higher
- Modern web browser with WebSocket support
- Backend service running on port 8000

## Installation

```bash
# Install dependencies
npm install

# Or using yarn
yarn install
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FlowStateMonitor.js
│   │   ├── BiometricDisplay.js
│   │   ├── BrainwaveBanner.tsx
│   │   ├── WaveChart.tsx
│   │   └── Wavelet.tsx
│   ├── services/         # API and WebSocket services
│   ├── hooks/            # Custom React hooks
│   ├── store/            # State management (Zustand)
│   ├── styles/           # CSS and styling
│   ├── utils/            # Utility functions
│   ├── App.js            # Main application component
│   └── index.js          # Application entry point
├── public/               # Static assets
├── package.json          # Dependencies and scripts
└── vite.config.js        # Build configuration
```

## Running the Frontend

### Development Mode
```bash
# Start development server with hot-reload
npm run dev

# Or specify a different port
npm run dev -- --port 3001
```

The application will be available at `http://localhost:3000` (or your specified port).

### Production Build
```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview

# Serve production build
npm run serve
```

## Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_MOCK_DATA=false
VITE_DEBUG_MODE=true
```

### Build Configuration
The project uses Vite for fast development and optimized production builds. Configuration is in `vite.config.js`.

## Key Features

### Real-Time Visualization
- **EEG Waveforms**: Live display of all 4 Muse channels
- **Power Spectral Display**: Frequency domain analysis
- **Flow Score Meter**: Visual indicator of current flow state
- **Trend Charts**: Historical flow patterns over session

### User Controls
- **Session Management**: Start, pause, resume, end sessions
- **Calibration Wizard**: Guided setup for personalized baselines
- **Audio Controls**: Binaural beat frequency and volume adjustment
- **Export Options**: Download session data in CSV/JSON formats

### State Management
The application uses Zustand for state management:

```javascript
// Example store usage
import { useFlowStore } from './store/flowStore';

function FlowIndicator() {
  const flowScore = useFlowStore(state => state.flowScore);
  return <div>Flow Score: {flowScore}</div>;
}
```

## Component Documentation

### Core Components

#### `<FlowStateMonitor />`
Main monitoring dashboard displaying real-time flow metrics
- Props: `sessionId`, `onStateChange`
- Events: Emits flow state changes

#### `<BiometricDisplay />`
Displays biometric data integration (heart rate, HRV)
- Props: `data`, `updateFrequency`

#### `<BrainwaveBanner />`
Animated visualization of current brainwave patterns
- Props: `frequencies`, `amplitude`

#### `<WaveChart />`
Real-time chart component for EEG signals
- Props: `channels`, `sampleRate`, `bufferSize`

## API Integration

### WebSocket Connections
```javascript
// EEG data stream
const eegSocket = new WebSocket('ws://localhost:8000/ws/eeg');

// Audio control
const audioSocket = new WebSocket('ws://localhost:8000/ws/audio');
```

### REST API Calls
```javascript
// Start session
fetch('/api/session/start', {
  method: 'POST',
  body: JSON.stringify(preferences)
});

// Get metrics
fetch(`/api/session/${sessionId}/metrics`);
```

## Testing

```bash
# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run end-to-end tests
npm run test:e2e
```

## Development Tools

### ESLint and Prettier
```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

### Type Checking (TypeScript)
```bash
# Type check
npm run type-check

# Type check in watch mode
npm run type-check:watch
```

## Performance Optimization

- Implements React.memo for expensive components
- Uses virtual scrolling for large data sets
- Debounces WebSocket updates to prevent overwhelming
- Lazy loads heavy visualization libraries
- Implements code splitting for route-based chunks

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

WebGL support required for advanced visualizations.

## Troubleshooting

### Common Issues

**Backend Connection Failed**
- Verify backend is running on expected port
- Check CORS configuration
- Ensure WebSocket protocol matches (ws:// vs wss://)

**Visualization Not Rendering**
- Check WebGL support in browser
- Verify GPU acceleration is enabled
- Try reducing visualization quality in settings

**High CPU Usage**
- Reduce update frequency in settings
- Disable unnecessary visualizations
- Check for memory leaks in DevTools

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader friendly
- High contrast mode available
- Customizable font sizes

## Contributing

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/kvnloo/FlowState/issues
- Documentation: https://kvnloo.github.io/FlowState/