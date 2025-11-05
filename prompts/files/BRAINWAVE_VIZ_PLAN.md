# Brainwave Visualization Implementation Plan

## Executive Summary
This plan outlines a systematic approach to building a complex EEG brainwave visualization webapp that displays 8 frequency bands as overlapping circles over time.

## System Requirements

### Visual Specifications
- **Time representation**: Horizontal layout, 60 seconds per row
- **Data points**: 1 second = 1 point = 8 concentric circles
- **Frequency bands**: 8 bands (delta, theta, low/high alpha, beta, gamma)
- **Rendering**: Semi-transparent overlapping circles with varying radii

### Color and Opacity Mapping
```javascript
const BRAINWAVE_CONFIG = {
  delta: { color: '#dd0a0a', opacity: 0.20, index: 0 },
  theta: { color: '#ff8500', opacity: 0.40, index: 1 },
  lowAlpha: { color: '#fcea01', opacity: 0.50, index: 2 },
  highAlpha: { color: '#58ed14', opacity: 0.50, index: 3 },
  lowBeta: { color: '#16caf4', opacity: 0.50, index: 4 },
  highBeta: { color: '#022aba', opacity: 0.50, index: 5 },
  lowGamma: { color: '#6f5ba3', opacity: 0.50, index: 6 },
  highGamma: { color: '#e50cbc', opacity: 0.50, index: 7 }
};
```

## Architecture

### 1. Data Structure Design

```typescript
// Core data structures
interface BrainwaveReading {
  timestamp: number;  // Unix timestamp or seconds elapsed
  bands: {
    delta: number;      // 0-1 normalized amplitude
    theta: number;
    lowAlpha: number;
    highAlpha: number;
    lowBeta: number;
    highBeta: number;
    lowGamma: number;
    highGamma: number;
  };
}

interface VisualizationPoint {
  x: number;              // Canvas x coordinate
  y: number;              // Canvas y coordinate
  circles: CircleData[];  // 8 circles for this point
}

interface CircleData {
  band: string;           // Band name
  radius: number;         // Calculated from amplitude
  color: string;          // Hex color
  opacity: number;        // 0-1
}
```

### 2. Module Structure

```
src/
├── data/
│   ├── BrainwaveDataProcessor.js   // Parse and normalize data
│   └── DataGenerator.js             // Mock data for testing
├── rendering/
│   ├── CanvasRenderer.js            // Core rendering engine
│   ├── CircleRenderer.js            // Optimized circle drawing
│   └── LayerManager.js              // Multiple canvas layers
├── layout/
│   ├── LayoutEngine.js              // Position calculation
│   └── TimelineMapper.js            // Time to coordinate mapping
├── config/
│   ├── BrainwaveConfig.js           // Colors, opacities, bands
│   └── RenderingConfig.js           // Performance settings
├── utils/
│   ├── ColorUtils.js                // Color manipulation
│   └── PerformanceMonitor.js        // FPS tracking
└── App.js                            // Main application
```

### 3. Rendering Strategy

#### Multi-Layer Canvas Approach
```javascript
// Use multiple canvases for performance
const layers = {
  background: canvas1,  // Grid, axes, static elements
  data: canvas2,        // Main data visualization
  interaction: canvas3, // Hover effects, tooltips
  overlay: canvas4      // Annotations, labels
};
```

#### Batch Rendering Optimization
```javascript
// Instead of drawing circles one at a time:
// BAD:
data.forEach(point => {
  point.circles.forEach(circle => {
    ctx.beginPath();
    ctx.arc(circle.x, circle.y, circle.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${circle.color}, ${circle.opacity})`;
    ctx.fill();
  });
});

// GOOD:
// Group by band/color first, then batch render
Object.keys(bands).forEach(bandName => {
  const band = bands[bandName];
  ctx.fillStyle = `rgba(${band.color}, ${band.opacity})`;
  
  // Draw all circles of this band in one batch
  band.circles.forEach(circle => {
    ctx.beginPath();
    ctx.arc(circle.x, circle.y, circle.r, 0, Math.PI * 2);
    ctx.fill();
  });
});
```

### 4. Layout Algorithm

```javascript
class LayoutEngine {
  constructor(config) {
    this.secondsPerRow = 60;
    this.pixelsPerSecond = 10;
    this.verticalSpacing = 100;
    this.baseCircleSize = 5;
    this.maxCircleSize = 40;
  }
  
  calculatePosition(timestamp, rowIndex = null) {
    // Convert timestamp to row and column
    const secondsElapsed = timestamp;
    const row = Math.floor(secondsElapsed / this.secondsPerRow);
    const col = secondsElapsed % this.secondsPerRow;
    
    return {
      x: col * this.pixelsPerSecond,
      y: row * this.verticalSpacing,
      row: row,
      col: col
    };
  }
  
  calculateCircleRadius(amplitude) {
    // Map amplitude (0-1) to radius (min-max)
    return this.baseCircleSize + 
           (amplitude * (this.maxCircleSize - this.baseCircleSize));
  }
}
```

### 5. Performance Optimization

#### Offscreen Canvas for Pre-rendering
```javascript
class CircleCache {
  constructor() {
    this.cache = new Map();
  }
  
  // Pre-render circle templates
  createTemplate(band, radius) {
    const key = `${band}-${radius}`;
    
    if (this.cache.has(key)) {
      return this.cache.get(key);
    }
    
    const tempCanvas = document.createElement('canvas');
    const size = radius * 2;
    tempCanvas.width = size;
    tempCanvas.height = size;
    const ctx = tempCanvas.getContext('2d');
    
    // Draw circle on temporary canvas
    const config = BRAINWAVE_CONFIG[band];
    ctx.fillStyle = this.rgbaColor(config.color, config.opacity);
    ctx.beginPath();
    ctx.arc(radius, radius, radius, 0, Math.PI * 2);
    ctx.fill();
    
    this.cache.set(key, tempCanvas);
    return tempCanvas;
  }
  
  rgbaColor(hex, opacity) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }
}
```

#### Viewport Culling
```javascript
class ViewportCuller {
  isVisible(point, viewport) {
    return (
      point.x + point.maxRadius > viewport.left &&
      point.x - point.maxRadius < viewport.right &&
      point.y + point.maxRadius > viewport.top &&
      point.y - point.maxRadius < viewport.bottom
    );
  }
  
  getVisiblePoints(allPoints, viewport) {
    return allPoints.filter(point => this.isVisible(point, viewport));
  }
}
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic infrastructure with mock data

1. Set up project structure
2. Create data structure definitions
3. Implement mock data generator
4. Create basic canvas setup
5. Implement simple circle rendering (single band)

**Deliverable**: Single-band visualization with mock data

### Phase 2: Core Rendering (Week 2)
**Goal**: Full 8-band rendering without optimization

1. Implement all 8 brainwave bands
2. Add color and opacity system
3. Implement layout engine
4. Add time-to-coordinate mapping
5. Basic interactivity (pan/zoom)

**Deliverable**: Complete but unoptimized visualization

### Phase 3: Optimization (Week 3)
**Goal**: Performance tuning for smooth rendering

1. Implement multi-layer canvas system
2. Add batch rendering
3. Implement circle caching
4. Add viewport culling
5. Optimize draw calls

**Deliverable**: Smooth 60fps rendering

### Phase 4: Features (Week 4)
**Goal**: Polish and additional features

1. Add annotations system
2. Implement tooltips
3. Add timeline/scrubbing
4. Data export/import
5. Responsive design

**Deliverable**: Production-ready application

## Prompt Engineering Strategy for Claude Code

### Problem: Why Previous Attempts Failed

1. **Too much at once**: Trying to build everything in one go
2. **Unclear data structure**: No specification of input format
3. **Missing constraints**: Performance requirements not stated
4. **No examples**: No sample data provided

### Solution: Iterative Prompting Approach

#### Round 1: Data Foundation
```
Create a JavaScript module for handling brainwave visualization data with the following requirements:

DATA STRUCTURE:
- Each data point represents 1 second of recording
- Contains 8 frequency bands: delta, theta, lowAlpha, highAlpha, lowBeta, highBeta, lowGamma, highGamma
- Each band has an amplitude value between 0 and 1

CONFIGURATION:
Use this exact color and opacity mapping:
- delta: #dd0a0a, 20% opacity
- theta: #ff8500, 40% opacity
- lowAlpha: #fcea01, 50% opacity
- highAlpha: #58ed14, 50% opacity
- lowBeta: #16caf4, 50% opacity
- highBeta: #022aba, 50% opacity
- lowGamma: #6f5ba3, 50% opacity
- highGamma: #e50cbc, 50% opacity

DELIVERABLES:
1. BrainwaveConfig.js - Configuration constants
2. BrainwaveData.js - Data structure and validation
3. MockDataGenerator.js - Generate random sample data for testing

Create clean, well-documented ES6 modules. Include JSDoc comments.
```

#### Round 2: Layout System
```
Create a layout engine for positioning brainwave visualization elements with these exact requirements:

LAYOUT RULES:
- Timeline flows horizontally
- 60 seconds = 1 row
- Each second = 1 point on canvas
- Each point contains 8 concentric circles (one per frequency band)
- Vertical spacing between rows: 100px
- Horizontal spacing: 10px per second

COORDINATE SYSTEM:
- Input: timestamp in seconds
- Output: {x, y} canvas coordinates

CIRCLE SIZING:
- Minimum radius: 5px (amplitude = 0)
- Maximum radius: 40px (amplitude = 1)
- Linear interpolation between min and max

DELIVERABLES:
1. LayoutEngine.js - Main layout calculator
2. Include method: calculatePosition(timestamp) => {x, y, row, col}
3. Include method: calculateCircleRadius(amplitude) => radius
4. Include comprehensive unit tests

Use the BrainwaveConfig from the previous step.
```

#### Round 3: Rendering System
```
Create an optimized canvas rendering system for the brainwave visualization:

REQUIREMENTS:
- Use HTML5 Canvas 2D context
- Render 8 semi-transparent overlapping circles per data point
- Support thousands of data points (60 seconds/row × many rows)

OPTIMIZATION STRATEGIES:
1. Batch rendering by band (draw all circles of same color together)
2. Use offscreen canvas for circle templates
3. Implement viewport culling (only render visible elements)

ARCHITECTURE:
- CanvasRenderer.js - Main rendering coordinator
- CircleRenderer.js - Optimized circle drawing
- CircleCache.js - Template caching system

RENDERING ORDER:
Draw bands from largest to smallest radius to ensure proper layering:
1. Outer rings first (typically higher amplitude bands)
2. Inner rings last

PERFORMANCE TARGET:
- 60 FPS with 1000+ data points
- Use requestAnimationFrame for smooth updates

Use the LayoutEngine and BrainwaveConfig from previous steps.
Include FPS counter for performance monitoring.
```

#### Round 4: Integration & Interaction
```
Create the main application that integrates all components:

FEATURES:
1. Canvas initialization and sizing
2. Data loading and visualization
3. Basic pan and zoom
4. Timeline scrubbing
5. Hover tooltips showing band amplitudes

USER INTERFACE:
- Full-screen canvas
- Timeline controls at bottom
- Legend showing band colors
- Performance stats (FPS counter)

INTEGRATION:
Import and use:
- BrainwaveConfig
- MockDataGenerator
- LayoutEngine  
- CanvasRenderer

DELIVERABLES:
1. App.js - Main application
2. index.html - HTML structure
3. styles.css - Styling
4. README.md - Usage instructions

Make it production-ready with error handling and responsive design.
```

## Testing Strategy

### Unit Tests
```javascript
// Test data structures
describe('BrainwaveData', () => {
  test('validates band values are 0-1', () => {
    // Test code
  });
});

// Test layout calculations
describe('LayoutEngine', () => {
  test('calculates correct position for timestamp', () => {
    const layout = new LayoutEngine();
    const pos = layout.calculatePosition(0);
    expect(pos).toEqual({x: 0, y: 0, row: 0, col: 0});
  });
  
  test('wraps to new row after 60 seconds', () => {
    const layout = new LayoutEngine();
    const pos = layout.calculatePosition(60);
    expect(pos.row).toBe(1);
    expect(pos.col).toBe(0);
  });
});
```

### Performance Tests
```javascript
// Measure rendering performance
class PerformanceMonitor {
  constructor() {
    this.frames = [];
    this.lastTime = performance.now();
  }
  
  tick() {
    const now = performance.now();
    const delta = now - this.lastTime;
    this.frames.push(delta);
    
    if (this.frames.length > 60) {
      this.frames.shift();
    }
    
    this.lastTime = now;
  }
  
  getFPS() {
    if (this.frames.length === 0) return 0;
    const avg = this.frames.reduce((a, b) => a + b) / this.frames.length;
    return Math.round(1000 / avg);
  }
}
```

## Common Pitfalls to Avoid

### 1. Context State Management
```javascript
// BAD: Not saving/restoring context
ctx.globalAlpha = 0.5;
drawCircles();
// Now everything after is at 0.5 alpha!

// GOOD: Save and restore
ctx.save();
ctx.globalAlpha = 0.5;
drawCircles();
ctx.restore();
```

### 2. Excessive beginPath/closePath
```javascript
// BAD: Too many state changes
circles.forEach(c => {
  ctx.beginPath();
  ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
  ctx.closePath();
  ctx.fill();
});

// GOOD: Minimize state changes
ctx.beginPath();
circles.forEach(c => {
  ctx.moveTo(c.x + c.r, c.y);
  ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
});
ctx.fill();
```

### 3. Color String Creation
```javascript
// BAD: Creating strings in render loop
function render() {
  circles.forEach(c => {
    ctx.fillStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${c.a})`;
    ctx.fill();
  });
}

// GOOD: Pre-compute color strings
const colors = Object.keys(BRAINWAVE_CONFIG).reduce((acc, band) => {
  const c = BRAINWAVE_CONFIG[band];
  const r = parseInt(c.color.slice(1, 3), 16);
  const g = parseInt(c.color.slice(3, 5), 16);
  const b = parseInt(c.color.slice(5, 7), 16);
  acc[band] = `rgba(${r}, ${g}, ${b}, ${c.opacity})`;
  return acc;
}, {});
```

## Sample Implementation Timeline

**Day 1-2**: Data structures and configuration
**Day 3-4**: Layout engine and positioning
**Day 5-7**: Basic rendering (unoptimized)
**Day 8-10**: Optimization (batching, caching)
**Day 11-12**: Interactivity and controls
**Day 13-14**: Polish and testing

## Success Metrics

- ✅ Renders 3600+ points (60 seconds × 60 rows)
- ✅ Maintains 60 FPS during pan/zoom
- ✅ Accurate color and opacity matching
- ✅ Proper circle layering
- ✅ Responsive to window resize
- ✅ Memory-efficient (no leaks)

## Next Steps

1. **Review this plan** with stakeholders
2. **Create sample data** to validate data structure
3. **Set up project** with proper tooling
4. **Follow iterative approach** - build and test each module
5. **Measure performance** at each stage
6. **Iterate based on feedback**

## Resources

- HTML5 Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- Performance optimization: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas
- Color theory for data viz: https://colorbrewer2.org/

---

This plan provides a roadmap for systematic development of the brainwave visualization system. Each phase builds on the previous one, with clear deliverables and success criteria.
