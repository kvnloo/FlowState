I need help building a complex EEG data visualization dashboard. This is a challenging UI task that requires careful analysis and incremental development.

Reference Files Analysis:
1. meditation_banner.jpg
   - We need to carefully analyze this image in multiple contexts
   - First, count the number of rows to determine total minutes of mock data needed
   - Important: What looks like background gradients is actually many large, overlapping circles
   - Study individual wavelets in the image to understand circle size variations
   - Critical: The intensity of each brainwave type directly controls its circle's SIZE, not opacity
   - During meditation, high brainwave intensities create massive circles that overlap to create the red/orange gradient effect

2. icon.jpg
   - Shows the smallest component (wavelet) structure
   - 8 concentric circles representing different brainwave types
   - Each ring represents a different brainwave type
   - Important: This is just the icon - in actual implementation, circles grow and shrink based on intensity

3. colors.jpg
Core colors for each brainwave type (all use full opacity in implementation):
- Delta (δ): #dd0a0a (red)
- Theta (θ): #ff8500 (orange)
- Low Alpha: #fcea01 (yellow)
- High Alpha: #58ed14 (green)
- Low Beta: #16caf4 (light blue)
- High Beta: #022aba (dark blue)
- Low Gamma: #6f5ba3 (purple)
- High Gamma: #e50cbc (magenta)

4. measurement.jpg
   - Shows how data is structured: 1 point = 1 second = 1 wavelet
   - Each row represents 60 seconds of data
   - Scale reference: 1 raw = 60 seconds
   - Circle sizes in each wavelet vary based on brainwave intensity values

Data Visualization Rules:
- Each wavelet contains 8 concentric circles, one for each brainwave type
- Higher brainwave intensity = Larger circle diameter
- All circles maintain full opacity
- Circles always remain concentric regardless of size
- Larger circles naturally overlap smaller ones
- The overlapping of many large, fully opaque circles creates the gradient-like effect
- CRITICAL SIZING RULE: Even at 100% intensity, each brainwave type has a different maximum diameter
  * Outermost circle (delta) has the largest maximum diameter
  * Each inner circle's maximum diameter is proportionally smaller
  * For example, if base size is 100px:
    - delta (outermost): 100% = 100px diameter
    - theta: 100% = 87.5px diameter
    - lowAlpha: 100% = 75px diameter
    - highAlpha: 100% = 62.5px diameter
    - lowBeta: 100% = 50px diameter
    - highBeta: 100% = 37.5px diameter
    - lowGamma: 100% = 25px diameter
    - highGamma (innermost): 100% = 12.5px diameter
  * Each circle's actual size = (maximum diameter × intensity percentage)
  * This ensures circles remain distinct and visible even at 100% intensity

Development Strategy:
Since this is too complex to build in one go, we need to break it down:

1. Start Small: Wavelet Component
   - Create two versions:
     a. Interactive version: Shows detailed brainwave intensity values on hover
     b. Performance-optimized version: Streamlined for grid display
   - Ensure proper circle size calculations based on intensity values
   - Test thoroughly with varying intensity values to verify circle scaling
        - Before grid implementation, we need to create a single-wavelet demo:
            - Create an interactive demo showing one large wavelet (red circle in example)
            - Below it, display 8 intensity sliders, one for each brainwave type:
            * delta: 0-100% (shown at 100% in demo)
            * theta: 0-100% (shown at 15% in demo)
            * lowAlpha: 0-100% (shown at 100% in demo)
            * highAlpha: 0-100% (shown at 60% in demo)
            * lowBeta: 0-100% (shown at 70% in demo)
            * highBeta: 0-100% (shown at 40% in demo)
            * lowGamma: 0-100% (shown at 20% in demo)
            * highGamma: 0-100% (shown at 99% in demo)
            - Each slider should update its corresponding circle size in real-time
            - This creates an immediate visual feedback loop for testing circle size relationships
            - Use this demo to verify correct circle sizing and overlapping behavior before proceeding to grid layout


2. Grid Layout Testing
   - Start with 5x5 grid (1/12th of full width)
   - Use just 25 wavelets initially
   - Test with varied intensity values to verify overlapping effects
   - Verify that high-intensity data creates proper large circle overlap effects

3. Performance Optimization
   - This visualization involves many dynamically-sized, overlapping elements
   - Need to consider web performance early
   - Plan for efficient loading of large datasets
   - Consider techniques for smooth fullscreen transitions

4. Full Implementation
   - Scale up to 60 columns (full minute)
   - Implement total rows based on meditation_banner.jpg analysis
   - Add fullscreen capability
   - Ensure performance at scale

Key Implementation Challenges:
- Circle sizes must scale correctly with brainwave intensity
- Overlapping of large circles must create smooth gradient effect
- Need to handle potentially large datasets smoothly
- Must maintain performance with many overlapping elements
- Requires both detailed single-wavelet view and optimized grid view

Let's start with Phase 1: creating and testing the basic wavelet component. Should we begin with the interactive or optimized version?