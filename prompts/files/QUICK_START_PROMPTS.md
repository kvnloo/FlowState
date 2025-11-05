# Quick Start: Copy-Paste Prompts for Claude Code

## How to Use This Guide

1. Copy each prompt in sequence
2. Paste into Claude Code
3. Wait for completion and test the output
4. Move to the next prompt only after verifying the previous step works

## Estimated Total Time: 2-3 hours

---

## ✅ PROMPT 1: Project Setup (5 minutes)

```
Set up a new web project for a brainwave visualization application.

CREATE THIS EXACT STRUCTURE:

brainwave-viz/
├── src/
│   ├── config/
│   ├── data/
│   ├── layout/
│   ├── rendering/
│   └── utils/
├── test/
└── public/

CREATE THESE FILES:

1. package.json with:
   - name: "brainwave-visualization"
   - type: "module" (for ES6 imports)
   - scripts for running a local dev server

2. public/index.html with:
   - Canvas element (id="brainwave-canvas")
   - Minimal styling (centered, responsive)
   - Script tag to load main.js as module

3. public/main.js (empty for now, we'll fill it later)

4. .gitignore with standard entries

5. README.md with:
   - Project description
   - Installation instructions  
   - How to run dev server

Use NO frameworks - pure JavaScript, HTML, CSS only.
Include instructions for running with a simple HTTP server (python -m http.server or similar).
```

**After this completes**: Verify you can run the dev server and see empty page with canvas

---

## ✅ PROMPT 2: Configuration Module (10 minutes)

```
Create src/config/BrainwaveConfig.js

This module defines all constants for the brainwave visualization system.

EXPORT 1: BANDS object with EXACT specifications:

export const BANDS = {
  delta: { name: 'delta', color: '#dd0a0a', opacity: 0.20, index: 0, displayName: 'Delta (0.5-4 Hz)' },
  theta: { name: 'theta', color: '#ff8500', opacity: 0.40, index: 1, displayName: 'Theta (4-8 Hz)' },
  lowAlpha: { name: 'lowAlpha', color: '#fcea01', opacity: 0.50, index: 2, displayName: 'Low Alpha (8-10 Hz)' },
  highAlpha: { name: 'highAlpha', color: '#58ed14', opacity: 0.50, index: 3, displayName: 'High Alpha (10-12 Hz)' },
  lowBeta: { name: 'lowBeta', color: '#16caf4', opacity: 0.50, index: 4, displayName: 'Low Beta (12-20 Hz)' },
  highBeta: { name: 'highBeta', color: '#022aba', opacity: 0.50, index: 5, displayName: 'High Beta (20-30 Hz)' },
  lowGamma: { name: 'lowGamma', color: '#6f5ba3', opacity: 0.50, index: 6, displayName: 'Low Gamma (30-40 Hz)' },
  highGamma: { name: 'highGamma', color: '#e50cbc', opacity: 0.50, index: 7, displayName: 'High Gamma (40+ Hz)' }
};

Freeze this object with Object.freeze() at all levels.

EXPORT 2: LAYOUT object:

export const LAYOUT = {
  secondsPerRow: 60,          // Wrap to new row after 60 seconds
  pixelsPerSecond: 10,        // Horizontal spacing
  verticalSpacing: 100,       // Space between rows
  minCircleRadius: 5,         // Minimum circle size
  maxCircleRadius: 40,        // Maximum circle size
  canvasWidth: 800,           // Default canvas width
  canvasHeight: 600           // Default canvas height
};

Freeze this too.

EXPORT 3: Helper functions:

/**
 * Get array of all band names in rendering order
 */
export function getBandNames() {
  return Object.keys(BANDS);
}

/**
 * Get band configuration by name
 */
export function getBand(name) {
  return BANDS[name];
}

/**
 * Convert hex color and opacity to rgba string
 * @param {string} hex - Hex color like '#ff0000'
 * @param {number} opacity - 0-1
 * @returns {string} Like 'rgba(255, 0, 0, 0.5)'
 */
export function hexToRgba(hex, opacity) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Pre-compute rgba strings for all bands (performance optimization)
 */
export function getPrecomputedColors() {
  const colors = {};
  Object.keys(BANDS).forEach(bandName => {
    const band = BANDS[bandName];
    colors[bandName] = hexToRgba(band.color, band.opacity);
  });
  return Object.freeze(colors);
}

TESTING:
Add this at the bottom (commented out):

// Test code (uncomment to run):
// console.log('Band names:', getBandNames());
// console.log('Delta config:', getBand('delta'));
// console.log('Delta color:', hexToRgba('#dd0a0a', 0.2));
// console.log('Precomputed colors:', getPrecomputedColors());

Add comprehensive JSDoc comments to all exports.
Make this production-ready and immutable.
```

**After completion**: Uncomment test code, run in browser console, verify output

---

## ✅ PROMPT 3: Mock Data Generator (15 minutes)

```
Create src/data/MockDataGenerator.js

This generates realistic fake brainwave data for testing.

IMPORT:
import { BANDS } from '../config/BrainwaveConfig.js';

DATA STRUCTURE - each point represents 1 second:
{
  timestamp: 0,  // seconds elapsed (integer)
  bands: {
    delta: 0.75,      // amplitude 0.0 - 1.0
    theta: 0.45,
    lowAlpha: 0.60,
    highAlpha: 0.30,
    lowBeta: 0.55,
    highBeta: 0.40,
    lowGamma: 0.20,
    highGamma: 0.15
  }
}

IMPLEMENT THREE GENERATION MODES:

MODE 1: Random Walk
- Start each band at random 0.3-0.7
- Each step: previous value + random(-0.1, 0.1)
- Clamp to [0, 1]
- Smooth realistic variation

MODE 2: Sine Waves
- delta: Math.sin(timestamp / 30) * 0.4 + 0.5  (slow, 30s period)
- theta: Math.sin(timestamp / 15) * 0.3 + 0.5  (medium, 15s period)
- lowAlpha: Math.sin(timestamp / 10) * 0.3 + 0.5
- highAlpha: Math.sin(timestamp / 10 + 1) * 0.3 + 0.5
- lowBeta: Math.sin(timestamp / 5) * 0.3 + 0.4
- highBeta: Math.sin(timestamp / 5 + 0.5) * 0.3 + 0.4
- lowGamma: Math.sin(timestamp / 3) * 0.2 + 0.3
- highGamma: Math.sin(timestamp / 3 + 1) * 0.2 + 0.2

MODE 3: Mental State Simulation
Simulate different mental states with transitions:
- seconds 0-60: "sleep" (delta 0.7-0.9, others 0.1-0.3)
- seconds 61-120: "waking" (transition)
- seconds 121-180: "focused" (beta 0.7-0.9, alpha 0.4-0.6, others low)
- seconds 181-240: "relaxed" (alpha 0.6-0.8, others medium)

CLASS STRUCTURE:

export class MockDataGenerator {
  constructor(mode = 'randomWalk') {
    // mode: 'randomWalk' | 'sineWaves' | 'mentalStates'
    this.mode = mode;
    this.bandNames = Object.keys(BANDS);
    
    // State for random walk
    this.currentValues = {};
  }
  
  /**
   * Generate specified number of seconds of data
   * @param {number} numSeconds
   * @returns {Array} Array of data points
   */
  generate(numSeconds) {
    const data = [];
    for (let t = 0; t < numSeconds; t++) {
      data.push(this.generatePoint(t));
    }
    return data;
  }
  
  /**
   * Generate a single data point
   * @param {number} timestamp - Seconds elapsed
   * @returns {Object} Data point
   */
  generatePoint(timestamp) {
    const bands = {};
    
    switch(this.mode) {
      case 'randomWalk':
        this.bandNames.forEach(name => {
          bands[name] = this.randomWalkValue(name);
        });
        break;
      
      case 'sineWaves':
        // Implement sine wave generation
        break;
      
      case 'mentalStates':
        // Implement state-based generation
        break;
    }
    
    return { timestamp, bands };
  }
  
  randomWalkValue(bandName) {
    // Initialize if first call
    if (!(bandName in this.currentValues)) {
      this.currentValues[bandName] = 0.5;
    }
    
    // Random walk: add small random change
    const change = (Math.random() - 0.5) * 0.2;
    this.currentValues[bandName] += change;
    
    // Clamp to [0, 1]
    this.currentValues[bandName] = Math.max(0, Math.min(1, this.currentValues[bandName]));
    
    return this.currentValues[bandName];
  }
  
  /**
   * Static convenience method
   */
  static createSampleData(seconds = 180, mode = 'randomWalk') {
    const gen = new MockDataGenerator(mode);
    return gen.generate(seconds);
  }
}

VALIDATION:
Add validation method:

static validate(dataPoint) {
  if (typeof dataPoint.timestamp !== 'number') return false;
  if (!dataPoint.bands) return false;
  
  const bandNames = Object.keys(BANDS);
  for (const name of bandNames) {
    const value = dataPoint.bands[name];
    if (typeof value !== 'number' || value < 0 || value > 1) {
      return false;
    }
  }
  return true;
}

TESTING:
Add commented test code at bottom:

// Test
// const gen1 = new MockDataGenerator('randomWalk');
// const data1 = gen1.generate(60);
// console.log('Random walk:', data1.slice(0, 3));
//
// const gen2 = new MockDataGenerator('sineWaves');
// const data2 = gen2.generate(60);
// console.log('Sine waves:', data2.slice(0, 3));
//
// console.log('Validation:', MockDataGenerator.validate(data1[0]));
//
// const sample = MockDataGenerator.createSampleData(120);
// console.log('Sample data:', sample.length, 'points generated');

Add JSDoc comments. Make all three modes work correctly.
```

**After completion**: Uncomment tests, verify all three modes generate valid data

---

## ✅ PROMPT 4: Layout Engine (20 minutes)

```
Create src/layout/LayoutEngine.js

This converts brainwave data into canvas rendering coordinates.

IMPORTS:
import { BANDS, LAYOUT } from '../config/BrainwaveConfig.js';

CRITICAL LAYOUT RULES:
1. Time flows HORIZONTALLY left-to-right
2. 60 seconds per row, then wrap to new row below
3. X position: seconds_in_row * pixelsPerSecond
4. Y position: row_number * verticalSpacing
5. Each second = 1 point = 8 concentric circles

POSITION CALCULATION EXAMPLES:
- timestamp 0: row=0, col=0, x=0, y=0
- timestamp 30: row=0, col=30, x=300, y=0
- timestamp 59: row=0, col=59, x=590, y=0
- timestamp 60: row=1, col=0, x=0, y=100
- timestamp 125: row=2, col=5, x=50, y=200

RADIUS CALCULATION:
- Input: amplitude (0.0 to 1.0)
- Output: radius in pixels (5 to 40)
- Formula: minRadius + (amplitude * (maxRadius - minRadius))
- Examples:
  - amplitude 0.0 → 5px
  - amplitude 0.5 → 22.5px
  - amplitude 1.0 → 40px

CLASS IMPLEMENTATION:

export class LayoutEngine {
  constructor(config = {}) {
    // Allow overriding defaults
    this.secondsPerRow = config.secondsPerRow || LAYOUT.secondsPerRow;
    this.pixelsPerSecond = config.pixelsPerSecond || LAYOUT.pixelsPerSecond;
    this.verticalSpacing = config.verticalSpacing || LAYOUT.verticalSpacing;
    this.minRadius = config.minRadius || LAYOUT.minCircleRadius;
    this.maxRadius = config.maxRadius || LAYOUT.maxCircleRadius;
  }
  
  /**
   * Calculate canvas position from timestamp
   * @param {number} timestamp - Seconds elapsed
   * @returns {{x: number, y: number, row: number, col: number}}
   */
  calculatePosition(timestamp) {
    const row = Math.floor(timestamp / this.secondsPerRow);
    const col = timestamp % this.secondsPerRow;
    
    return {
      x: col * this.pixelsPerSecond,
      y: row * this.verticalSpacing,
      row: row,
      col: col
    };
  }
  
  /**
   * Calculate circle radius from amplitude
   * @param {number} amplitude - 0.0 to 1.0
   * @returns {number} Radius in pixels
   */
  calculateRadius(amplitude) {
    // Clamp amplitude to valid range
    const clamped = Math.max(0, Math.min(1, amplitude));
    
    // Linear interpolation
    return this.minRadius + (clamped * (this.maxRadius - this.minRadius));
  }
  
  /**
   * Process single data point into renderable format
   * @param {Object} dataPoint - From MockDataGenerator
   * @returns {Object} Processed point with position and circles
   */
  processDataPoint(dataPoint) {
    const position = this.calculatePosition(dataPoint.timestamp);
    
    // Create circle data for each band
    const circles = Object.keys(BANDS).map(bandName => {
      const band = BANDS[bandName];
      const amplitude = dataPoint.bands[bandName];
      
      return {
        bandName: bandName,
        band: band,  // Include full band config
        amplitude: amplitude,
        radius: this.calculateRadius(amplitude)
      };
    });
    
    // Sort circles by radius (largest first for proper layering)
    circles.sort((a, b) => b.radius - a.radius);
    
    return {
      ...position,  // x, y, row, col
      timestamp: dataPoint.timestamp,
      circles: circles,
      maxRadius: Math.max(...circles.map(c => c.radius))  // For culling
    };
  }
  
  /**
   * Process array of data points
   * @param {Array} dataPoints - From MockDataGenerator
   * @returns {Array} Processed points ready for rendering
   */
  processDataPoints(dataPoints) {
    return dataPoints.map(point => this.processDataPoint(point));
  }
  
  /**
   * Calculate required canvas dimensions for given data
   * @param {Array} dataPoints
   * @returns {{width: number, height: number}}
   */
  calculateCanvasDimensions(dataPoints) {
    if (dataPoints.length === 0) {
      return { width: LAYOUT.canvasWidth, height: LAYOUT.canvasHeight };
    }
    
    const maxTimestamp = Math.max(...dataPoints.map(p => p.timestamp));
    const maxRow = Math.floor(maxTimestamp / this.secondsPerRow);
    
    return {
      width: this.secondsPerRow * this.pixelsPerSecond + 50,  // +50 for margin
      height: (maxRow + 1) * this.verticalSpacing + 50  // +50 for margin
    };
  }
}

UNIT TESTS (commented out):

// Tests
// const layout = new LayoutEngine();
// 
// // Test position calculation
// console.log('Position tests:');
// console.log('t=0:', layout.calculatePosition(0));   // {x:0, y:0, row:0, col:0}
// console.log('t=30:', layout.calculatePosition(30)); // {x:300, y:0, row:0, col:30}
// console.log('t=60:', layout.calculatePosition(60)); // {x:0, y:100, row:1, col:0}
// console.log('t=125:', layout.calculatePosition(125)); // {x:50, y:200, row:2, col:5}
//
// // Test radius calculation
// console.log('\nRadius tests:');
// console.log('amp=0:', layout.calculateRadius(0));    // 5
// console.log('amp=0.5:', layout.calculateRadius(0.5)); // 22.5
// console.log('amp=1:', layout.calculateRadius(1));    // 40
//
// // Test with real data
// import { MockDataGenerator } from '../data/MockDataGenerator.js';
// const data = MockDataGenerator.createSampleData(120);
// const processed = layout.processDataPoints(data);
// console.log('\nProcessed data:');
// console.log('First point:', processed[0]);
// console.log('Point at t=60:', processed[60]);
// console.log('Canvas dimensions:', layout.calculateCanvasDimensions(data));

Add comprehensive JSDoc comments.
Make calculations mathematically precise.
```

**After completion**: Uncomment tests, verify calculations are correct

---

## ✅ PROMPT 5: Canvas Renderer (25 minutes)

```
Create src/rendering/CanvasRenderer.js

This renders processed brainwave data onto HTML5 canvas.
This is the SIMPLE version - we'll optimize later if needed.

IMPORTS:
import { hexToRgba } from '../config/BrainwaveConfig.js';

RENDERING STRATEGY:
1. Clear canvas
2. For each processed data point:
   3. For each circle in point (already sorted by radius):
      4. Set fill style (rgba color)
      5. Begin path
      6. Draw arc (circle)
      7. Fill

WHY THIS ORDER:
Circles are pre-sorted largest-to-smallest radius, so we draw:
- Largest (background) first
- Smallest (foreground) last
This creates proper visual layering with transparency.

CLASS IMPLEMENTATION:

export class CanvasRenderer {
  constructor(canvas) {
    if (!canvas) {
      throw new Error('Canvas element required');
    }
    
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;
    
    // Performance tracking
    this.lastRenderTime = 0;
    this.frameCount = 0;
  }
  
  /**
   * Clear entire canvas
   */
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
  }
  
  /**
   * Render a single circle
   * @param {number} x - Center X
   * @param {number} y - Center Y
   * @param {number} radius - Circle radius
   * @param {string} rgbaColor - Pre-computed 'rgba(...)' string
   */
  renderCircle(x, y, radius, rgbaColor) {
    this.ctx.fillStyle = rgbaColor;
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.fill();
  }
  
  /**
   * Render single data point (8 concentric circles)
   * @param {Object} point - Processed point from LayoutEngine
   */
  renderPoint(point) {
    // Circles already sorted largest-to-smallest
    point.circles.forEach(circle => {
      // Convert to rgba
      const rgba = hexToRgba(circle.band.color, circle.band.opacity);
      
      this.renderCircle(
        point.x,
        point.y,
        circle.radius,
        rgba
      );
    });
  }
  
  /**
   * Render multiple data points
   * @param {Array} points - Processed points
   * @returns {Object} Render stats
   */
  render(points) {
    const startTime = performance.now();
    
    this.clear();
    
    points.forEach(point => {
      this.renderPoint(point);
    });
    
    const endTime = performance.now();
    this.lastRenderTime = endTime - startTime;
    this.frameCount++;
    
    return {
      renderTime: this.lastRenderTime,
      pointCount: points.length,
      circleCount: points.length * 8,
      fps: this.calculateFPS()
    };
  }
  
  /**
   * Calculate approximate FPS based on render time
   * @returns {number} Estimated FPS
   */
  calculateFPS() {
    if (this.lastRenderTime === 0) return 0;
    return Math.round(1000 / this.lastRenderTime);
  }
  
  /**
   * Resize canvas and update internal dimensions
   * @param {number} width
   * @param {number} height
   */
  resize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
    this.width = width;
    this.height = height;
  }
  
  /**
   * Get rendering statistics
   * @returns {Object} Stats object
   */
  getStats() {
    return {
      lastRenderTime: this.lastRenderTime,
      frameCount: this.frameCount,
      estimatedFPS: this.calculateFPS(),
      canvasSize: { width: this.width, height: this.height }
    };
  }
}

ADD THIS TEST FILE: test/renderer-test.html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renderer Test</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: monospace;
      background: #222;
    }
    canvas {
      border: 2px solid #666;
      background: #fff;
      display: block;
      margin: 20px 0;
    }
    .stats {
      color: #fff;
      padding: 10px;
      background: #333;
      border-radius: 4px;
      margin: 10px 0;
    }
    .stats div {
      margin: 5px 0;
    }
  </style>
</head>
<body>
  <h1 style="color: #fff;">Brainwave Renderer Test</h1>
  
  <div class="stats" id="stats">
    <div>Loading...</div>
  </div>
  
  <canvas id="canvas" width="800" height="400"></canvas>
  
  <script type="module">
    import { MockDataGenerator } from '../src/data/MockDataGenerator.js';
    import { LayoutEngine } from '../src/layout/LayoutEngine.js';
    import { CanvasRenderer } from '../src/rendering/CanvasRenderer.js';
    
    // Generate data
    console.log('Generating data...');
    const generator = new MockDataGenerator('randomWalk');
    const data = generator.generate(120);  // 2 minutes
    console.log('Generated', data.length, 'data points');
    
    // Process layout
    console.log('Processing layout...');
    const layout = new LayoutEngine();
    const points = layout.processDataPoints(data);
    const dimensions = layout.calculateCanvasDimensions(data);
    console.log('Processed', points.length, 'points');
    console.log('Canvas dimensions:', dimensions);
    
    // Setup renderer
    const canvas = document.getElementById('canvas');
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;
    const renderer = new CanvasRenderer(canvas);
    
    // Render
    console.log('Rendering...');
    const stats = renderer.render(points);
    console.log('Render complete:', stats);
    
    // Display stats
    document.getElementById('stats').innerHTML = `
      <div><strong>Render Statistics</strong></div>
      <div>Points rendered: ${stats.pointCount}</div>
      <div>Circles rendered: ${stats.circleCount}</div>
      <div>Render time: ${stats.renderTime.toFixed(2)}ms</div>
      <div>Estimated FPS: ${stats.fps}</div>
      <div>Canvas size: ${dimensions.width} × ${dimensions.height}</div>
    `;
  </script>
</body>
</html>

Add comprehensive JSDoc comments.
Focus on correctness, not optimization yet.
```

**After completion**: Open test/renderer-test.html, should see colorful brainwave visualization

---

## ✅ PROMPT 6: Main Application (30 minutes)

```
Create public/main.js - the main application file that ties everything together.

This will be imported by index.html and run when page loads.

IMPORTS:
import { MockDataGenerator } from '../src/data/MockDataGenerator.js';
import { LayoutEngine } from '../src/layout/LayoutEngine.js';
import { CanvasRenderer } from '../src/rendering/CanvasRenderer.js';
import { BANDS, getBandNames } from '../src/config/BrainwaveConfig.js';

FEATURES TO IMPLEMENT:

1. Canvas initialization
2. Data generation with controls
3. Rendering
4. Legend showing band colors
5. Performance stats display
6. Controls for regenerating data

APPLICATION STRUCTURE:

class BrainwaveApp {
  constructor() {
    this.canvas = null;
    this.renderer = null;
    this.layout = null;
    this.data = null;
    this.processedPoints = null;
    
    this.init();
  }
  
  init() {
    // Setup canvas
    this.canvas = document.getElementById('brainwave-canvas');
    if (!this.canvas) {
      console.error('Canvas not found');
      return;
    }
    
    // Initialize components
    this.layout = new LayoutEngine();
    this.renderer = new CanvasRenderer(this.canvas);
    
    // Generate initial data
    this.generateAndRender('randomWalk', 180);
    
    // Setup UI controls
    this.setupControls();
    
    // Setup legend
    this.createLegend();
  }
  
  generateAndRender(mode = 'randomWalk', seconds = 180) {
    console.log(`Generating ${seconds}s of data (mode: ${mode})...`);
    
    // Generate data
    const generator = new MockDataGenerator(mode);
    this.data = generator.generate(seconds);
    
    // Process layout
    this.processedPoints = this.layout.processDataPoints(this.data);
    
    // Resize canvas to fit data
    const dimensions = this.layout.calculateCanvasDimensions(this.data);
    this.renderer.resize(dimensions.width, dimensions.height);
    
    // Render
    const stats = this.renderer.render(this.processedPoints);
    
    // Update stats display
    this.updateStats(stats);
    
    console.log('Render complete:', stats);
  }
  
  setupControls() {
    // Create control panel
    const controls = document.createElement('div');
    controls.id = 'controls';
    controls.innerHTML = `
      <div class="control-group">
        <label>Generation Mode:</label>
        <select id="mode-select">
          <option value="randomWalk">Random Walk</option>
          <option value="sineWaves">Sine Waves</option>
          <option value="mentalStates">Mental States</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>Duration (seconds):</label>
        <input type="number" id="duration-input" value="180" min="10" max="600" step="10">
      </div>
      
      <div class="control-group">
        <button id="regenerate-btn">Regenerate Data</button>
      </div>
      
      <div id="stats-display" class="stats-panel">
        <div>Ready</div>
      </div>
    `;
    
    // Insert before canvas
    this.canvas.parentNode.insertBefore(controls, this.canvas);
    
    // Setup event listeners
    document.getElementById('regenerate-btn').addEventListener('click', () => {
      const mode = document.getElementById('mode-select').value;
      const duration = parseInt(document.getElementById('duration-input').value);
      this.generateAndRender(mode, duration);
    });
  }
  
  createLegend() {
    const legend = document.createElement('div');
    legend.id = 'legend';
    legend.innerHTML = '<h3>Brainwave Bands</h3>';
    
    const bandNames = getBandNames();
    bandNames.forEach(name => {
      const band = BANDS[name];
      const item = document.createElement('div');
      item.className = 'legend-item';
      item.innerHTML = `
        <div class="legend-color" style="background-color: ${band.color}; opacity: ${band.opacity};"></div>
        <div class="legend-label">${band.displayName}</div>
      `;
      legend.appendChild(item);
    });
    
    document.body.appendChild(legend);
  }
  
  updateStats(stats) {
    const display = document.getElementById('stats-display');
    if (display) {
      display.innerHTML = `
        <div><strong>Render Statistics</strong></div>
        <div>Points: ${stats.pointCount}</div>
        <div>Circles: ${stats.circleCount}</div>
        <div>Time: ${stats.renderTime.toFixed(2)}ms</div>
        <div>FPS: ${stats.fps}</div>
      `;
    }
  }
}

// Initialize app when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  new BrainwaveApp();
});

ALSO UPDATE public/index.html:

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Brainwave Visualization</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #1a1a1a;
      color: #fff;
      padding: 20px;
    }
    
    h1 {
      margin-bottom: 20px;
      font-size: 28px;
    }
    
    #controls {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 20px;
    }
    
    .control-group {
      margin-bottom: 15px;
    }
    
    .control-group label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
    }
    
    select, input {
      padding: 8px;
      border-radius: 4px;
      border: 1px solid #444;
      background: #333;
      color: #fff;
      font-size: 14px;
    }
    
    button {
      padding: 10px 20px;
      background: #0066cc;
      color: #fff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
    }
    
    button:hover {
      background: #0052a3;
    }
    
    .stats-panel {
      margin-top: 15px;
      padding: 15px;
      background: #333;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
    }
    
    .stats-panel div {
      margin: 5px 0;
    }
    
    #brainwave-canvas {
      background: #fff;
      border: 2px solid #444;
      border-radius: 8px;
      display: block;
      margin: 20px 0;
      max-width: 100%;
      height: auto;
    }
    
    #legend {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      margin-top: 20px;
    }
    
    #legend h3 {
      margin-bottom: 15px;
      font-size: 18px;
    }
    
    .legend-item {
      display: flex;
      align-items: center;
      margin: 10px 0;
    }
    
    .legend-color {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      margin-right: 10px;
      border: 2px solid #444;
    }
    
    .legend-label {
      font-size: 14px;
    }
  </style>
</head>
<body>
  <h1>🧠 Brainwave Visualization</h1>
  
  <!-- Controls and canvas will be inserted by main.js -->
  <canvas id="brainwave-canvas"></canvas>
  
  <script type="module" src="./main.js"></script>
</body>
</html>

Make this a complete, working application with good UI/UX.
Add error handling and loading states.
```

**After completion**: Open index.html, should see full working application with controls

---

## Verification Checklist

After completing all prompts, verify:

- [ ] Can run local server
- [ ] Page loads without errors
- [ ] Can see colorful brainwave visualization
- [ ] Can select different generation modes
- [ ] Can change duration and regenerate
- [ ] Legend shows all 8 bands with correct colors
- [ ] Stats show render performance
- [ ] Console logs show no errors

## What You Should See

A working visualization showing:
- Multiple rows of colorful overlapping circles
- Each second = cluster of 8 circles
- 60 seconds per row before wrapping
- Circles vary in size based on amplitude
- Colors match the specification exactly
- Smooth transitions (if using sine waves or mental states)

## Next Steps (Optional Optimizations)

If performance is < 30 FPS with large datasets:

1. Implement batch rendering (group by color)
2. Add viewport culling (only render visible points)
3. Use offscreen canvas for circle templates
4. Implement dirty rectangle optimization
5. Add WebGL renderer option

## Troubleshooting

**Problem**: "Module not found" errors
**Solution**: Check that file structure matches exactly, use correct relative paths

**Problem**: Nothing renders
**Solution**: Open browser console, check for errors, verify canvas dimensions > 0

**Problem**: Colors don't match
**Solution**: Verify hex codes in BrainwaveConfig.js match specification exactly

**Problem**: Layout is wrong
**Solution**: Check LayoutEngine calculations against examples in prompt

**Problem**: Performance is poor
**Solution**: Check number of points being rendered, start with smaller datasets

## Support Resources

- MDN Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- Chrome DevTools: https://developer.chrome.com/docs/devtools/
- Performance profiling: https://developer.chrome.com/docs/devtools/performance/

---

Total estimated time: 2-3 hours to complete all prompts
Expected result: Fully functional brainwave visualization web application
