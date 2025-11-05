# Prompt Engineering Guide for Claude Code: Brainwave Visualization

## Core Problem Analysis

### Why Claude Code Is Failing

1. **Image Analysis Limitations**
   - Claude can see images but may not extract precise numerical specifications
   - Color hex codes need to be explicitly provided
   - Layout measurements need to be stated, not inferred

2. **Complexity Overload**
   - Asking for "recreate this image" is too broad
   - Multiple concerns bundled together (data, layout, rendering, styling)
   - No clear starting point or sequence

3. **Missing Context**
   - No data structure definition
   - No performance requirements stated
   - No breakdown of rendering strategy

4. **Scope Ambiguity**
   - Unclear what "done" looks like
   - No intermediate milestones
   - No testing strategy

## Solution: Structured Iterative Prompting

### Principle 1: Single Responsibility per Prompt
Each prompt should have ONE clear objective that can be completed and tested independently.

### Principle 2: Explicit > Implicit
State everything explicitly. Never assume Claude can infer from images:
- ✅ "Use hex color #dd0a0a with 20% opacity"
- ❌ "Use the red color from the image"

### Principle 3: Provide Examples
Show expected input and output for each module:
```javascript
// Example: If I give you this data:
const input = {timestamp: 0, bands: {delta: 0.5, theta: 0.8, ...}};
// You should output:
const output = {x: 0, y: 0, circles: [{radius: 22.5, color: '#dd0a0a', opacity: 0.2}, ...]};
```

### Principle 4: Specify Dependencies
Make dependencies explicit:
- "This module imports BrainwaveConfig from ./config/BrainwaveConfig.js"
- "Use the LayoutEngine.calculatePosition() method from the previous step"

### Principle 5: Include Validation
Every prompt should specify how to verify correctness:
- "Include unit tests that verify..."
- "Add console.log() to show the first 5 calculated positions"
- "Include an FPS counter to verify performance"

## Prompt Templates

### Template 1: Configuration/Constants Module

```
Create a configuration module for [SYSTEM] with the following requirements:

PURPOSE:
[One sentence describing what this module does]

CONSTANTS:
[List all constants with exact values]
- NAME: value
- NAME2: value2

DATA STRUCTURE:
```javascript
const CONFIG = {
  key: value,
  key2: value2
};
```

EXPORTS:
- Export as ES6 module
- Make constants immutable (Object.freeze)

VALIDATION:
- Include a validate() function that checks if values are in expected ranges

DELIVERABLES:
1. Single file: [filename.js]
2. JSDoc comments for all exports
3. Example usage in comments

CONSTRAINTS:
- No external dependencies
- Pure JavaScript (no TypeScript)
- Node.js and browser compatible
```

### Template 2: Data Processing Module

```
Create a data processing module that [SPECIFIC TASK].

INPUT FORMAT:
```javascript
// Describe exactly what comes in
const input = {
  // Include example
};
```

OUTPUT FORMAT:
```javascript
// Describe exactly what goes out
const output = {
  // Include example
};
```

PROCESSING LOGIC:
1. [Step 1]
2. [Step 2]
3. [Step 3]

ERROR HANDLING:
- Validate input shape
- Throw descriptive errors for invalid data
- Include try-catch examples

PERFORMANCE:
- Target: Process N items in X ms
- Use [specific optimization if relevant]

TESTING:
Include test cases:
1. Normal case: [describe]
2. Edge case: [describe]
3. Error case: [describe]

DEPENDENCIES:
- Import [Module1] from ./path/to/module1.js
- Import [Module2] from ./path/to/module2.js
```

### Template 3: Rendering Module

```
Create a canvas rendering module for [SPECIFIC VISUAL ELEMENT].

CANVAS SETUP:
- Canvas size: [width] × [height]
- Context type: 2d
- Background: [color or transparent]

RENDERING REQUIREMENTS:
1. [Requirement 1 with exact measurements]
2. [Requirement 2 with exact colors/sizes]
3. [Requirement 3 with performance target]

VISUAL SPECIFICATIONS:
- Color: [exact hex with opacity]
- Size: [exact pixel dimensions or calculation formula]
- Position: [exact coordinate calculation]
- Layering: [render order]

OPTIMIZATION:
- Use [specific technique]
- Target: [FPS or render time]
- Implement [specific optimization strategy]

INTERACTIVITY (if applicable):
- [Describe mouse/touch interactions]

DEPENDENCIES:
- Uses [Module1] for [purpose]
- Uses [Module2] for [purpose]

DELIVERABLES:
1. [ClassName].js with the following methods:
   - constructor(canvas, config)
   - render(data)
   - clear()
   - [other methods]

2. Include usage example:
```javascript
const renderer = new Renderer(canvas, config);
renderer.render(data);
```

TESTING:
- Visual test: Should produce [describe expected output]
- Performance test: [describe how to measure]
```

## Real-World Prompt Sequence for Brainwave Viz

### Prompt 1: Configuration (15 minutes)

```
Create a configuration module for brainwave visualization with these exact specifications:

FILE: src/config/BrainwaveConfig.js

BRAINWAVE BANDS (in rendering order, largest to smallest):
```javascript
export const BANDS = {
  delta: {
    name: 'delta',
    color: '#dd0a0a',
    opacity: 0.20,
    index: 0,
    displayName: 'Delta'
  },
  theta: {
    name: 'theta',
    color: '#ff8500',
    opacity: 0.40,
    index: 1,
    displayName: 'Theta'
  },
  lowAlpha: {
    name: 'lowAlpha',
    color: '#fcea01',
    opacity: 0.50,
    index: 2,
    displayName: 'Low Alpha'
  },
  highAlpha: {
    name: 'highAlpha',
    color: '#58ed14',
    opacity: 0.50,
    index: 3,
    displayName: 'High Alpha'
  },
  lowBeta: {
    name: 'lowBeta',
    color: '#16caf4',
    opacity: 0.50,
    index: 4,
    displayName: 'Low Beta'
  },
  highBeta: {
    name: 'highBeta',
    color: '#022aba',
    opacity: 0.50,
    index: 5,
    displayName: 'High Beta'
  },
  lowGamma: {
    name: 'lowGamma',
    color: '#6f5ba3',
    opacity: 0.50,
    index: 6,
    displayName: 'Low Gamma'
  },
  highGamma: {
    name: 'highGamma',
    color: '#e50cbc',
    opacity: 0.50,
    index: 7,
    displayName: 'High Gamma'
  }
};
```

LAYOUT CONSTANTS:
```javascript
export const LAYOUT = {
  secondsPerRow: 60,
  pixelsPerSecond: 10,
  verticalSpacing: 100,
  minCircleRadius: 5,
  maxCircleRadius: 40
};
```

DELIVERABLES:
1. Export BANDS as frozen object (Object.freeze)
2. Export LAYOUT as frozen object
3. Export helper function: getBandNames() => string[]
4. Export helper function: getBandByIndex(index) => band object
5. Export helper function: hexToRgba(hex, opacity) => 'rgba(r,g,b,a)' string
6. Include JSDoc comments for all exports
7. Include console.log test at bottom (commented out) showing all band colors

Make this production-ready, immutable, and well-documented.
```

**Expected Time to Complete**: 5-10 minutes
**How to Verify**: Check that all hex colors match, helper functions work
**Next Step**: Use this config in MockDataGenerator

---

### Prompt 2: Mock Data Generator (20 minutes)

```
Create a mock data generator for testing the brainwave visualization.

FILE: src/data/MockDataGenerator.js

DEPENDENCIES:
```javascript
import { BANDS } from '../config/BrainwaveConfig.js';
```

DATA STRUCTURE:
Each data point represents 1 second of brainwave readings.

```javascript
// Expected output format:
{
  timestamp: 0,  // seconds elapsed
  bands: {
    delta: 0.75,      // amplitude 0-1
    theta: 0.45,
    lowAlpha: 0.60,
    highAlpha: 0.30,
    lowBeta: 0.55,
    highBeta: 0.40,
    lowGamma: 0.20,
    highGamma: 0.15
  }
}
```

GENERATION ALGORITHMS:

1. **Random Walk**: Each band value changes gradually from previous
   - Start with random value 0.3-0.7
   - Each step: += random(-0.1, 0.1)
   - Clamp to [0, 1]

2. **Sine Waves**: Smooth oscillations
   - delta: slow oscillation (period: 30s)
   - theta: medium oscillation (period: 15s)
   - alpha: faster oscillation (period: 10s)
   - beta/gamma: rapid oscillation (period: 5s)

3. **State Simulation**: Simulate different mental states
   - "sleep": delta high (0.7-0.9), others low (0.1-0.3)
   - "awake": alpha/beta high (0.5-0.8), delta low (0.1-0.2)
   - "focus": beta high (0.7-0.9), alpha medium, others low
   - "meditation": alpha/theta high, beta/gamma low

CLASS STRUCTURE:
```javascript
export class MockDataGenerator {
  constructor(algorithm = 'randomWalk') {
    // algorithm: 'randomWalk' | 'sineWaves' | 'stateSimulation'
  }
  
  generate(numSeconds) {
    // Returns array of numSeconds data points
    // Each point has timestamp and bands
  }
  
  generateForDuration(startTime, endTime) {
    // Alternative: generate for time range
  }
}
```

VALIDATION:
- All band values must be 0-1
- Timestamps must be sequential integers starting from 0
- No missing bands

DELIVERABLES:
1. MockDataGenerator class with all three algorithms
2. Static method: MockDataGenerator.createSampleData(seconds = 120) 
3. Unit tests showing each algorithm produces valid data
4. Example usage in comments showing how to generate 300 seconds of data

TESTING:
Include commented-out test code at bottom:
```javascript
// Test code (uncomment to run):
// const gen = new MockDataGenerator('randomWalk');
// const data = gen.generate(10);
// console.log('Generated', data.length, 'data points');
// console.log('First point:', data[0]);
// console.log('All values in range?', 
//   data.every(p => Object.values(p.bands).every(v => v >= 0 && v <= 1))
// );
```

Make this flexible, well-tested, and easy to use.
```

**Expected Time**: 15-20 minutes
**Verification**: Run test code, check data validity
**Next Step**: Use generated data with LayoutEngine

---

### Prompt 3: Layout Engine (25 minutes)

```
Create a layout engine that converts brainwave data to canvas coordinates.

FILE: src/layout/LayoutEngine.js

DEPENDENCIES:
```javascript
import { BANDS, LAYOUT } from '../config/BrainwaveConfig.js';
```

LAYOUT RULES (CRITICAL):
1. Time flows HORIZONTALLY, left to right
2. Each row = 60 seconds
3. After 60 seconds, wrap to next row below
4. Each second = 1 point = 8 concentric circles
5. Horizontal spacing: 10 pixels per second
6. Vertical spacing: 100 pixels per row

COORDINATE CALCULATION:
```javascript
// Example: timestamp 0 (first second)
// Position: x=0, y=0, row=0, col=0

// Example: timestamp 30 (31st second)
// Position: x=300, y=0, row=0, col=30

// Example: timestamp 60 (61st second, first of new row)
// Position: x=0, y=100, row=1, col=0

// Example: timestamp 125
// Row: 125 / 60 = 2.083... => row 2
// Col: 125 % 60 = 5
// Position: x=50, y=200
```

CIRCLE RADIUS CALCULATION:
```javascript
// Amplitude range: [0, 1]
// Radius range: [5px, 40px]
// Formula: radius = 5 + (amplitude * 35)

// Example: amplitude = 0 => radius = 5px
// Example: amplitude = 0.5 => radius = 22.5px
// Example: amplitude = 1 => radius = 40px
```

CLASS STRUCTURE:
```javascript
export class LayoutEngine {
  constructor(config = {}) {
    // Allow overriding LAYOUT constants
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
    // Implement calculation here
  }
  
  /**
   * Calculate circle radius from amplitude
   * @param {number} amplitude - Value from 0 to 1
   * @returns {number} Radius in pixels
   */
  calculateRadius(amplitude) {
    // Implement calculation here
  }
  
  /**
   * Process a data point into renderable format
   * @param {Object} dataPoint - From MockDataGenerator
   * @returns {Object} Position and circle data
   */
  processDataPoint(dataPoint) {
    const pos = this.calculatePosition(dataPoint.timestamp);
    
    const circles = Object.keys(BANDS).map(bandName => {
      const amplitude = dataPoint.bands[bandName];
      const band = BANDS[bandName];
      
      return {
        bandName: bandName,
        radius: this.calculateRadius(amplitude),
        color: band.color,
        opacity: band.opacity,
        amplitude: amplitude
      };
    });
    
    return {
      x: pos.x,
      y: pos.y,
      row: pos.row,
      col: pos.col,
      timestamp: dataPoint.timestamp,
      circles: circles
    };
  }
  
  /**
   * Process multiple data points
   * @param {Array} dataPoints - Array from MockDataGenerator
   * @returns {Array} Array of processable points
   */
  processDataPoints(dataPoints) {
    return dataPoints.map(p => this.processDataPoint(p));
  }
}
```

VALIDATION:
- Positions must never be negative
- Radius must be between min and max
- All circle properties must be present

UNIT TESTS:
Include comprehensive tests:
```javascript
// Test cases (include these):
// 1. Position for timestamp 0
// 2. Position for timestamp 59 (last of first row)
// 3. Position for timestamp 60 (first of second row)
// 4. Radius for amplitude 0, 0.5, 1
// 5. Process full data point with all bands
```

DELIVERABLES:
1. LayoutEngine class with all methods
2. Comprehensive JSDoc comments
3. Unit test code (commented but runnable)
4. Example usage showing processing 120 seconds of data

TESTING:
```javascript
// Test code (uncomment to run):
// import { MockDataGenerator } from '../data/MockDataGenerator.js';
// const gen = new MockDataGenerator();
// const data = gen.generate(120);
// const layout = new LayoutEngine();
// const positions = layout.processDataPoints(data);
// console.log('Processed', positions.length, 'points');
// console.log('First point:', positions[0]);
// console.log('Point at 60 seconds:', positions[60]);
// console.log('Point at 120 seconds:', positions[119]);
```

Make this mathematically precise and thoroughly tested.
```

**Expected Time**: 20-30 minutes
**Verification**: Run tests, verify calculations are correct
**Next Step**: Use with CanvasRenderer

---

### Prompt 4: Basic Renderer (30 minutes)

```
Create a basic canvas renderer for brainwave visualization (unoptimized first version).

FILE: src/rendering/CanvasRenderer.js

DEPENDENCIES:
```javascript
import { BANDS, LAYOUT } from '../config/BrainwaveConfig.js';
```

PURPOSE:
Render processed data points (from LayoutEngine) onto HTML5 canvas.
This is the SIMPLE version - we'll optimize later.

RENDERING APPROACH:
1. Clear canvas
2. For each data point:
   3. For each circle (8 per point):
      4. Set fill style (color + opacity)
      5. Draw circle at (x, y) with calculated radius

RENDER ORDER (IMPORTANT):
Draw circles from BACK TO FRONT based on radius:
- Largest radius first (background)
- Smallest radius last (foreground)
This ensures proper visual layering.

COLOR CONVERSION:
```javascript
// Convert hex + opacity to rgba string
// Example: hex='#dd0a0a', opacity=0.2
// Result: 'rgba(221, 10, 10, 0.2)'

function hexToRgba(hex, opacity) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}
```

CLASS STRUCTURE:
```javascript
export class CanvasRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;
  }
  
  /**
   * Clear the entire canvas
   */
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
  }
  
  /**
   * Render a single circle
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate  
   * @param {number} radius - Circle radius
   * @param {string} color - Hex color
   * @param {number} opacity - Opacity 0-1
   */
  renderCircle(x, y, radius, color, opacity) {
    this.ctx.fillStyle = this.hexToRgba(color, opacity);
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.fill();
  }
  
  /**
   * Render a single data point (8 circles)
   * @param {Object} point - Processed point from LayoutEngine
   */
  renderPoint(point) {
    // Sort circles by radius (largest first)
    const sorted = [...point.circles].sort((a, b) => b.radius - a.radius);
    
    // Draw each circle
    sorted.forEach(circle => {
      this.renderCircle(
        point.x,
        point.y,
        circle.radius,
        circle.color,
        circle.opacity
      );
    });
  }
  
  /**
   * Render multiple data points
   * @param {Array} points - Array of processed points
   */
  render(points) {
    this.clear();
    points.forEach(point => this.renderPoint(point));
  }
  
  /**
   * Convert hex color to rgba string
   * @param {string} hex - Hex color like '#ff0000'
   * @param {number} opacity - Opacity 0-1
   * @returns {string} RGBA string like 'rgba(255,0,0,0.5)'
   */
  hexToRgba(hex, opacity) {
    // Implement conversion
  }
}
```

CANVAS SETUP:
```javascript
// Example HTML setup:
// <canvas id="brainwave-canvas" width="800" height="600"></canvas>

// Example usage:
const canvas = document.getElementById('brainwave-canvas');
const renderer = new CanvasRenderer(canvas);
renderer.render(processedPoints);
```

DELIVERABLES:
1. CanvasRenderer class with all methods
2. Helper function: hexToRgba()
3. JSDoc comments for all methods
4. Example usage in comments

TESTING:
Create a simple HTML test file that:
1. Creates a canvas
2. Generates 60 seconds of mock data
3. Processes it with LayoutEngine
4. Renders it with CanvasRenderer
5. Should see colorful overlapping circles

```html
<!-- test.html (create this to test) -->
<!DOCTYPE html>
<html>
<head>
  <title>Brainwave Renderer Test</title>
  <style>
    canvas { border: 1px solid #ccc; }
  </style>
</head>
<body>
  <canvas id="canvas" width="800" height="400"></canvas>
  <script type="module">
    import { MockDataGenerator } from './src/data/MockDataGenerator.js';
    import { LayoutEngine } from './src/layout/LayoutEngine.js';
    import { CanvasRenderer } from './src/rendering/CanvasRenderer.js';
    
    const canvas = document.getElementById('canvas');
    const gen = new MockDataGenerator('randomWalk');
    const data = gen.generate(60);
    const layout = new LayoutEngine();
    const points = layout.processDataPoints(data);
    const renderer = new CanvasRenderer(canvas);
    renderer.render(points);
    
    console.log('Rendered', points.length, 'points');
  </script>
</body>
</html>
```

CONSTRAINTS:
- Don't worry about performance yet
- Focus on correctness
- Make sure colors and opacity match spec exactly
- Verify circle layering (largest first)

Make this simple, correct, and testable. We'll optimize in the next step.
```

**Expected Time**: 25-35 minutes
**Verification**: Open test.html, see colorful circles
**Next Step**: Optimize the renderer

---

## Advanced Prompting Techniques

### Technique 1: Specification First, Code Second

**Bad Prompt**:
"Create a renderer for the visualization"

**Good Prompt**:
"Before writing any code, first create a specification document that describes:
1. Inputs and outputs
2. Rendering algorithm step-by-step
3. Performance targets
4. Testing criteria

Then, based on the spec, implement the code."

### Technique 2: Iterative Refinement

**First Iteration**:
"Create a basic working version without optimization"

**Second Iteration**:
"Now optimize the renderer using these techniques:
1. Batch rendering by color
2. Pre-compute rgba strings
3. Minimize ctx state changes

Keep the same interface but improve performance."

### Technique 3: Constraint-Driven Development

```
Create [MODULE] with these HARD CONSTRAINTS:

MUST HAVE:
- [Requirement 1]
- [Requirement 2]

MUST NOT:
- [Anti-requirement 1]  
- [Anti-requirement 2]

PERFORMANCE:
- [Specific metric]

If any constraint cannot be met, explain why before implementing.
```

### Technique 4: Test-Driven Prompting

```
Create unit tests for [MODULE] first.

TESTS SHOULD VERIFY:
1. [Test case 1]
2. [Test case 2]
3. [Test case 3]

After tests are written, implement the module to pass all tests.
```

## Troubleshooting Guide

### Problem: Claude creates different structure than specified

**Solution**: Be more explicit about file structure
```
Create EXACTLY this file structure:

src/
├── config/
│   └── BrainwaveConfig.js   <-- CREATE THIS FILE FIRST
├── data/
│   └── MockDataGenerator.js <-- CREATE THIS FILE SECOND
...

Each file should start with:
// Filename: [exact path]
// Purpose: [one line]
// Dependencies: [list imports]
```

### Problem: Code doesn't match visual specification

**Solution**: Include visual examples in the prompt
```
The output should look EXACTLY like this:

[Describe visual appearance in detail]
- Color at position X: #ff0000
- Circle at timestamp 0: center (0, 0), radius 22.5px
- Circle at timestamp 60: center (0, 100), radius varies

Include a console log that verifies these exact values.
```

### Problem: Performance is not good enough

**Solution**: Specify performance testing
```
Implement with these performance requirements:

TARGET: Render 1000 points at 60 FPS

MEASUREMENT:
Include a performance monitor that logs:
- Frame time in ms
- FPS
- Number of draw calls

If performance is below target, try these optimizations:
1. [Optimization 1]
2. [Optimization 2]

Report actual performance achieved.
```

### Problem: Code works but is hard to modify

**Solution**: Emphasize modularity and documentation
```
Create with EXTREME MODULARITY:

PRINCIPLES:
- Single Responsibility: Each function does ONE thing
- Pure Functions: No side effects where possible
- Clear Interfaces: Well-defined inputs/outputs
- Comprehensive Docs: Every function has JSDoc

CODE REVIEW CRITERIA:
- Can I understand each function in < 30 seconds?
- Can I test each function independently?
- Can I swap implementations without breaking users?

If answer is No to any question, refactor.
```

## Checklist for Every Prompt

Before sending a prompt to Claude Code, verify:

- [ ] Single clear objective
- [ ] Exact specifications (numbers, colors, sizes)
- [ ] Input/output examples
- [ ] Dependencies explicitly listed
- [ ] Success criteria defined
- [ ] Testing approach specified
- [ ] Performance targets stated (if relevant)
- [ ] File structure specified
- [ ] Coding standards mentioned (ES6, JSDoc, etc.)
- [ ] Verification steps included

## Summary: Key Principles

1. **Break down complexity** into bite-sized modules
2. **Be explicit** about everything - never assume Claude can infer
3. **Provide examples** of inputs, outputs, and usage
4. **Specify dependencies** and module interfaces
5. **Include testing** and verification criteria
6. **Iterate** - build simple first, then optimize
7. **Document** intentions and expected behavior
8. **Measure** performance and correctness

Following these principles will dramatically improve your success rate with Claude Code for complex visualization projects.
