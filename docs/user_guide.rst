User Guide
==========

This guide covers how to use FlowState effectively for optimizing your cognitive performance and achieving flow states.

Understanding Flow States
-------------------------

What is a Flow State?
~~~~~~~~~~~~~~~~~~~~~

A flow state is a mental state of complete immersion and focused energy. Characteristics include:

* **Complete focus** on the task at hand
* **Loss of self-consciousness** - ego dissolves
* **Time distortion** - hours pass like minutes
* **Intrinsic motivation** - the activity itself is rewarding
* **Peak performance** - operating at maximum capability

FlowState helps you recognize, achieve, and maintain these optimal states through real-time neurofeedback.

How FlowState Detects Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

FlowState monitors several brainwave patterns:

* **Alpha waves (8-12 Hz)**: Relaxed awareness, creativity
* **Theta waves (4-8 Hz)**: Deep meditation, flow states
* **Beta waves (13-30 Hz)**: Active concentration
* **Gamma waves (30-100 Hz)**: High-level cognitive processing

The system uses a proprietary algorithm that analyzes the ratios and coherence between these frequencies to detect when you enter flow.

Using FlowState
---------------

Daily Workflow
~~~~~~~~~~~~~~

1. **Morning Calibration** (2 minutes)

   * Put on your Muse headband
   * Run a quick calibration check
   * Ensures accurate readings for the day

2. **Work Sessions** (25-90 minutes)

   * Start FlowState before beginning focused work
   * Monitor the flow indicator in the UI
   * Adjust based on feedback signals

3. **Break Periods**

   * Review your session statistics
   * Note what activities triggered flow
   * Plan optimization for next session

Feedback Modes
~~~~~~~~~~~~~~

Audio Feedback
^^^^^^^^^^^^^^

FlowState generates binaural beats that adapt to your current state:

* **Approaching flow**: Beats gradually shift to optimal frequencies
* **In flow**: Maintains entrainment frequency
* **Losing flow**: Gentle alerts to refocus

To enable/disable:

.. code-block:: python

   Settings → Audio → Binaural Beats [ON/OFF]

Visual Feedback
^^^^^^^^^^^^^^^

Multiple visual feedback options:

* **Screen overlay**: Subtle color shifts indicate state
* **Peripheral indicators**: Corner animations for non-intrusive feedback
* **Strobe glasses**: Advanced option for visual entrainment

Configuration:

.. code-block:: python

   Settings → Visual → Feedback Mode [Overlay/Peripheral/Strobe]

Haptic Feedback
^^^^^^^^^^^^^^^

For devices with haptic support:

* **Gentle pulses**: Indicate state transitions
* **Rhythmic patterns**: Maintain flow awareness
* **Alert vibrations**: Signal attention drops

Activities & Optimization
--------------------------

Best Activities for Flow
~~~~~~~~~~~~~~~~~~~~~~~~~

FlowState works best with:

* **Programming**: Complex problem-solving
* **Writing**: Creative or technical writing
* **Learning**: Video courses, reading, research
* **Design**: Visual or system design work
* **Music**: Practice or composition

YouTube Integration
~~~~~~~~~~~~~~~~~~~

FlowState can automatically adjust YouTube playback speed based on your attention:

1. Install the FlowState browser extension
2. Navigate to any YouTube video
3. Click the FlowState icon to enable
4. Video speed adjusts automatically:

   * High focus: 1.5x - 2x speed
   * Normal focus: 1x speed
   * Low focus: 0.75x speed

This helps you consume information at your optimal processing rate.

Session Types
~~~~~~~~~~~~~

Focus Session
^^^^^^^^^^^^^

For deep work requiring sustained attention:

* Duration: 45-90 minutes
* Binaural beats: Beta range (15-20 Hz)
* Visual: Minimal feedback
* Goal: Maintain steady focus

Creative Session
^^^^^^^^^^^^^^^^

For brainstorming and creative tasks:

* Duration: 30-60 minutes
* Binaural beats: Alpha range (8-12 Hz)
* Visual: Color-shifting overlay
* Goal: Relaxed awareness

Learning Session
^^^^^^^^^^^^^^^^

For studying and skill acquisition:

* Duration: 25-45 minutes
* Binaural beats: Theta-Alpha bridge (6-10 Hz)
* Visual: Peripheral indicators
* Goal: Enhanced memory formation

Advanced Features
-----------------

Custom Protocols
~~~~~~~~~~~~~~~~

Create personalized neurofeedback protocols:

.. code-block:: python

   # backend/protocols/custom.yaml
   my_protocol:
     name: "Deep Focus Protocol"
     stages:
       - duration: 300  # 5 minutes warm-up
         target_state: "alpha_dominant"
       - duration: 2400  # 40 minutes deep work
         target_state: "theta_alpha_bridge"
       - duration: 300  # 5 minutes cool-down
         target_state: "alpha_dominant"

Data Export
~~~~~~~~~~~

Export your session data for analysis:

.. code-block:: bash

   # Export as CSV
   python export_data.py --format csv --output my_sessions.csv

   # Export as JSON
   python export_data.py --format json --output my_sessions.json

Integration with Other Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FlowState can integrate with:

* **Pomodoro timers**: Sync with work/break cycles
* **Task managers**: Log flow states per task
* **Calendar apps**: Schedule optimal work times
* **Quantified self platforms**: Export to services like Exist.io

Troubleshooting Sessions
------------------------

Common Issues
~~~~~~~~~~~~~

**"Can't achieve flow"**

* Ensure proper headband fit (sensors making good contact)
* Try different activities (not all tasks induce flow)
* Check environmental factors (noise, interruptions)
* Review caffeine/stimulant intake

**"Feedback is distracting"**

* Reduce feedback intensity in settings
* Switch to peripheral visual mode
* Use audio-only feedback
* Decrease update frequency

**"Inconsistent readings"**

* Clean Muse sensors with rubbing alcohol
* Slightly wet sensors or use conductive gel
* Check Bluetooth connection stability
* Recalibrate baseline

Optimization Tips
~~~~~~~~~~~~~~~~~

1. **Environment Setup**

   * Minimize distractions
   * Consistent lighting
   * Comfortable temperature
   * Good posture and ergonomics

2. **Timing**

   * Track your best flow times
   * Most people: 2-4 hours after waking
   * Avoid right after meals
   * Respect your chronotype

3. **Preparation**

   * Clear task definition
   * All materials ready
   * Notifications disabled
   * Hydration prepared

4. **Recovery**

   * Don't force extended sessions
   * Take breaks when indicated
   * Review session data
   * Note successful patterns

Metrics & Progress
------------------

Understanding Your Data
~~~~~~~~~~~~~~~~~~~~~~~

Key metrics FlowState tracks:

* **Flow Score**: 0-100 rating of flow quality
* **Flow Duration**: Total time in flow per session
* **Entry Time**: How quickly you achieve flow
* **Stability**: How well you maintain flow
* **Recovery**: How quickly you return after interruption

Progress Indicators
~~~~~~~~~~~~~~~~~~~

Track improvement over time:

* **Weekly averages**: Compare week-over-week
* **Personal records**: Best sessions highlighted
* **Trend analysis**: Long-term improvement curves
* **Pattern recognition**: What conditions work best

Setting Goals
~~~~~~~~~~~~~

Realistic progression:

* **Week 1-2**: Learn to recognize flow feelings
* **Week 3-4**: Achieve flow 1-2 times per week
* **Month 2**: Increase duration and frequency
* **Month 3+**: Consistent daily flow sessions

Privacy & Data
--------------

Your EEG data is:

* Stored locally on your device
* Never sent to external servers
* Exportable in open formats
* Completely under your control

To delete all data:

.. code-block:: bash

   python manage_data.py --delete-all --confirm

Support Resources
-----------------

* **Quick Start Video**: [YouTube Tutorial]
* **Community Forum**: Share tips and experiences
* **FAQ**: :doc:`/faq`
* **Research Papers**: :doc:`/research/index`
* **API Documentation**: :doc:`/api/modules`