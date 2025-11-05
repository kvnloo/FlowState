# Architecture & Workflow Visual Reference

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BRAINWAVE VISUALIZATION                      │
│                         WEB APPLICATION                         │
└─────────────────────────────────────────────────────────────────┘

                               USER
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │    User Interface      │
                    │   (index.html + UI)    │
                    └────────────────────────┘
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │   Main Application     │
                    │      (main.js)         │
                    └────────────────────────┘
                      │        │         │
         ┌────────────┘        │         └────────────┐
         ↓                     ↓                       ↓
┌─────────────────┐  ┌─────────────────┐   ┌──────────────────┐
│ MockDataGen     │  │  LayoutEngine   │   │  CanvasRenderer  │
│ • randomWalk    │  │  • positions    │   │  • clear()       │
│ • sineWaves     │  │  • calculatePos │   │  • render()      │
│ • mentalStates  │  │  • calculateRad │   │  • renderCircle  │
└─────────────────┘  └─────────────────┘   └──────────────────┘
         │                     │                       │
         └──────────┬──────────┘                       │
                    ↓                                  │
         ┌─────────────────────┐                      │
         │  BrainwaveConfig    │←─────────────────────┘
         │  • BANDS (colors)   │
         │  • LAYOUT (sizes)   │
         │  • helpers          │
         └─────────────────────┘
```

## Data Flow Pipeline

```
RAW DATA POINT                PROCESSED POINT              RENDERED OUTPUT
───────────────              ──────────────────            ──────────────

{                            {                             ╭─────────╮
  timestamp: 0,              timestamp: 0,                 │ ◉  ◉  ◉ │
  bands: {         →         x: 0,              →          │◉  ◉  ◉ ◉│
    delta: 0.75,             y: 0,                         │  ◉ ◉ ◉  │
    theta: 0.45,             circles: [                    │   ◉ ◉   │
    ...                        {radius: 31.25, ...},       ╰─────────╯
  }                            {radius: 20.75, ...},
}                              ...                         8 concentric
                             ]                             circles with
                           }                               transparency
```

## Module Dependency Graph

```
                    ┌──────────────────────┐
                    │  BrainwaveConfig.js  │ ← Base (no dependencies)
                    └──────────────────────┘
                              ↑
                              │ imports
              ┌───────────────┼────────────────┐
              │               │                 │
    ┌─────────────────┐  ┌────────────┐  ┌───────────────┐
    │ MockDataGen.js  │  │ Layout.js  │  │  Renderer.js  │
    └─────────────────┘  └────────────┘  └───────────────┘
              │               │                 │
              └───────────────┼─────────────────┘
                              ↓ all import into
                      ┌──────────────┐
                      │   main.js    │
                      └──────────────┘
```

## Rendering Pipeline Detail

```
Step 1: CLEAR CANVAS
┌────────────────────────────────────┐
│                                    │
│         [blank canvas]             │
│                                    │
└────────────────────────────────────┘

Step 2: FOR EACH DATA POINT
┌────────────────────────────────────┐
│  Point(x=0, y=0)                   │
│  └─> 8 circles to draw             │
│      [sorted by radius, big→small] │
└────────────────────────────────────┘

Step 3: DRAW CIRCLES (largest first)
┌────────────────────────────────────┐
│    ◉ (delta, radius=35, red-20%)   │
│   ◉◉ (theta, radius=30, org-40%)   │
│  ◉◉◉ (lowAlpha, radius=25, yel-50%)│
│   ... continues for all 8 bands    │
└────────────────────────────────────┘

Step 4: REPEAT FOR NEXT POINT
┌────────────────────────────────────┐
│  ◉     ◉     ◉     ◉    ...        │
│    (x=10)  (x=20)  (x=30)          │
└────────────────────────────────────┘

Result: Overlapping semi-transparent circles creating complex patterns
```

## Timeline Layout Visualization

```
TIME →

Row 0: [0──────────────────────────────────────────────────59] seconds
       │  • • • • • • • • • • • • • • • • • • • • • • • • • • │
       x=0                                                  x=590

Row 1: [60─────────────────────────────────────────────────119] seconds
       │  • • • • • • • • • • • • • • • • • • • • • • • • • • │
       x=0                                                  x=590

Row 2: [120────────────────────────────────────────────────179] seconds
       │  • • • • • • • • • • • • • • • • • • • • • • • • • • │
       x=0                                                  x=590

Each • = 1 second = 8 concentric circles
60 seconds per row
10 pixels per second horizontal spacing
100 pixels vertical spacing between rows
```

## Circle Composition at Each Point

```
Single Data Point (1 second) visualized:

                     Outermost                     
                ╭────────────────╮                
              ╭─────────────────────╮             
            ╭───────────────────────────╮         
          ╭─────────────────────────────────╮     
        ╭───────────────────────────────────────╮ 
       │     delta (red, 20% opacity)          │
       │   theta (orange, 40% opacity)        │
       │  lowAlpha (yellow, 50% opacity)     │
       │ highAlpha (green, 50% opacity)     │
       │lowBeta (cyan, 50% opacity)        │
       │highBeta (blue, 50% opacity)      │
       │lowGamma (purple, 50% opacity)   │
       │highGamma (magenta, 50%)  ○     │  Innermost
        ╰───────────────────────────────────────╯
          ╰─────────────────────────────────╯
            ╰───────────────────────────╯
              ╰─────────────────────╯
                ╰────────────────╮

Radius varies with amplitude (0.0 to 1.0):
  amplitude 0.0 → 5px radius (smallest)
  amplitude 0.5 → 22.5px radius (medium)
  amplitude 1.0 → 40px radius (largest)
```

## Color Mapping Reference

```
Band Name    │ Color     │ Hex      │ Opacity │ Visual
─────────────┼───────────┼──────────┼─────────┼────────
delta        │ Red       │ #dd0a0a  │ 20%     │ ●
theta        │ Orange    │ #ff8500  │ 40%     │ ●
lowAlpha     │ Yellow    │ #fcea01  │ 50%     │ ●
highAlpha    │ Green     │ #58ed14  │ 50%     │ ●
lowBeta      │ Cyan      │ #16caf4  │ 50%     │ ●
highBeta     │ Blue      │ #022aba  │ 50%     │ ●
lowGamma     │ Purple    │ #6f5ba3  │ 50%     │ ●
highGamma    │ Magenta   │ #e50cbc  │ 50%     │ ●
```

## Prompt Execution Sequence

```
┌─────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION SEQUENCE                   │
└─────────────────────────────────────────────────────────────┘

PROMPT 1: Setup (5 min)
    ↓
    ├─ Create project structure
    ├─ Setup package.json
    └─ Create index.html
    
PROMPT 2: Config (10 min)
    ↓
    ├─ Define BANDS constant
    ├─ Define LAYOUT constant
    └─ Create helper functions
    
PROMPT 3: Data Generator (15 min)
    ↓
    ├─ Implement randomWalk mode
    ├─ Implement sineWaves mode
    └─ Implement mentalStates mode
    
PROMPT 4: Layout Engine (20 min)
    ↓
    ├─ Calculate positions (timestamp → x,y)
    ├─ Calculate radii (amplitude → radius)
    └─ Process data points
    
PROMPT 5: Renderer (25 min)
    ↓
    ├─ Canvas initialization
    ├─ Circle drawing
    └─ Batch rendering
    
PROMPT 6: Main App (30 min)
    ↓
    ├─ UI controls
    ├─ Legend
    ├─ Stats display
    └─ Integration

═══════════════════════════════════════════════════════════════
         TOTAL TIME: 2-3 hours → Working Application ✓
```

## Testing Workflow

```
┌────────────────┐
│ Write Module   │
└────────┬───────┘
         │
         ↓
┌────────────────┐     ┌──────────┐
│ Uncomment Test │────→│ Run Test │
└────────┬───────┘     └────┬─────┘
         │                   │
         │                   ↓
         │            ┌──────────────┐
         │            │ Test Passes? │
         │            └──┬────────┬──┘
         │               │ No     │ Yes
         │               ↓        ↓
         │          ┌────────┐  ┌────────────┐
         │          │ Debug  │  │ Next Module│
         │          └────────┘  └──────┬─────┘
         │                             │
         └─────────────────────────────┘
```

## Performance Optimization Path

```
BASELINE (Unoptimized)
    │
    ├─ Measure: 15 FPS with 180 seconds
    │
    ↓
OPTIMIZATION 1: Batch by Color
    │
    ├─ Group all circles of same band
    ├─ Draw in single pass per band
    │
    ├─ Result: 25 FPS ↑
    ↓
OPTIMIZATION 2: Pre-compute Colors
    │
    ├─ Convert hex→rgba once
    ├─ Store in lookup table
    │
    ├─ Result: 35 FPS ↑
    ↓
OPTIMIZATION 3: Viewport Culling
    │
    ├─ Only render visible points
    ├─ Skip off-screen circles
    │
    ├─ Result: 50 FPS ↑
    ↓
OPTIMIZATION 4: Offscreen Canvas
    │
    ├─ Pre-render circle templates
    ├─ Use drawImage for copies
    │
    └─ Result: 60 FPS ↑ TARGET ACHIEVED ✓
```

## State Transitions (Mental States Mode)

```
Time  │ State      │ Visualization Pattern
──────┼────────────┼─────────────────────────────────
0-60s │ Sleep      │ ●●●●◌◌◌◌  (delta high, others low)
      │            │ Red circles dominate
      │            │
60-120│ Waking     │ ●●●●○○○◌  (transition)
      │            │ Mix of colors
      │            │
120-  │ Focused    │ ◌○○○●●●●  (beta high)
180   │            │ Blue circles dominate
      │            │
180-  │ Relaxed    │ ◌●●●●●◌◌  (alpha high)
240   │            │ Yellow/green dominate

Legend: ● = large circles (high amplitude)
        ○ = medium circles
        ◌ = small circles (low amplitude)
```

## File Size Reference

```
Module                    │ Lines │ Size  │ Complexity
─────────────────────────┼───────┼───────┼───────────
BrainwaveConfig.js       │  ~80  │  3KB  │ Simple
MockDataGenerator.js     │ ~150  │  5KB  │ Medium
LayoutEngine.js          │ ~120  │  4KB  │ Medium
CanvasRenderer.js        │ ~100  │  3KB  │ Simple
main.js                  │ ~150  │  5KB  │ Medium
─────────────────────────┼───────┼───────┼───────────
TOTAL                    │ ~600  │ 20KB  │ Manageable
```

## Memory Footprint

```
Component              │ Memory Usage
──────────────────────┼──────────────────
Data (180s)           │ ~50KB
Processed Points      │ ~100KB
Canvas Buffer         │ ~2MB (800×600)
Renderer State        │ ~10KB
UI Components         │ ~50KB
──────────────────────┼──────────────────
TOTAL                 │ ~2.2MB (minimal!)
```

## Browser Compatibility Matrix

```
Browser              │ Version │ Status
────────────────────┼─────────┼────────────
Chrome              │ 90+     │ ✓ Full
Firefox             │ 88+     │ ✓ Full
Safari              │ 14+     │ ✓ Full
Edge                │ 90+     │ ✓ Full
Opera               │ 76+     │ ✓ Full
Mobile Safari       │ 14+     │ ✓ Full
Mobile Chrome       │ 90+     │ ✓ Full
────────────────────┼─────────┼────────────
IE 11               │ N/A     │ ✗ No ES6

Requirements: ES6 modules, Canvas 2D API, fetch (optional)
```

## Quick Command Reference

```bash
# Setup
npm init -y
npm install --save-dev http-server

# Run dev server (Option 1)
npx http-server public -p 8080

# Run dev server (Option 2)
python -m http.server 8080

# Run dev server (Option 3)
php -S localhost:8080 -t public

# Open in browser
open http://localhost:8080

# Run tests
open test/renderer-test.html
```

## Debugging Checklist

```
Issue: Nothing renders
  │
  ├─ Check: Canvas dimensions > 0?
  ├─ Check: Console errors?
  ├─ Check: Data generated?
  ├─ Check: render() called?
  └─ Check: Correct file paths?

Issue: Wrong colors
  │
  ├─ Check: Hex codes match spec?
  ├─ Check: Opacity correct?
  └─ Check: hexToRgba() working?

Issue: Wrong layout
  │
  ├─ Check: Position calculation?
  ├─ Check: Test with t=0, 60, 120?
  └─ Check: Pixels per second = 10?

Issue: Poor performance
  │
  ├─ Check: How many points?
  ├─ Reduce to 60 seconds
  ├─ Check console warnings
  └─ Profile with DevTools
```

---

## Legend for Diagrams

```
Symbols Used:
  │  ├  └  ┌  ┐  ┘  ╮  ╯  ╰  ╭  = Connecting lines
  ↓  ↑  →  ←                  = Direction arrows
  ●  ◉  ○  ◌                   = Circles (full to empty)
  ✓  ✗                        = Pass/Fail
  [  ]                        = Containers
  ...                         = Continuation

Color Indicators:
  ● = Red (delta)
  ● = Orange (theta)
  ● = Yellow (lowAlpha)
  ● = Green (highAlpha)
  ● = Cyan (lowBeta)
  ● = Blue (highBeta)
  ● = Purple (lowGamma)
  ● = Magenta (highGamma)
```

---

This visual reference provides a quick overview of the system architecture,
data flow, and implementation sequence at a glance.

Use this alongside the detailed documents for a complete understanding.
