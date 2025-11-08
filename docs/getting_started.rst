Getting Started
===============

Welcome to FlowState - a Brain-Computer Interface (BCI) application that optimizes your cognitive performance through real-time EEG neurofeedback.

What is FlowState?
------------------

FlowState is a proof-of-concept application that uses EEG signals from your brain to detect when you're in a flow state - that optimal state of consciousness where you're fully immersed and performing at your peak. The system provides real-time feedback through audio, visual, and haptic signals to help you maintain and deepen these flow states.

Key capabilities:

* **Attention-based video speed control**: Automatically adjusts YouTube playback speed based on your focus level
* **Binaural beat generation**: Creates custom audio frequencies to entrain your brainwaves
* **Real-time flow detection**: Monitors your EEG patterns to identify flow states
* **Multi-modal feedback**: Coordinated audio, visual, and haptic feedback systems

Prerequisites
-------------

Hardware Requirements
~~~~~~~~~~~~~~~~~~~~~

* **Muse Headband**: A consumer EEG device (Muse 2, Muse S, or original Muse)
* **Computer**: Windows, macOS, or Linux with Bluetooth support
* **Optional**: Strobe glasses for visual stimulation

Software Requirements
~~~~~~~~~~~~~~~~~~~~~

* Python 3.12 or higher
* Node.js 18+ (for the frontend)
* Git

Installation
------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/kvnloo/FlowState.git
   cd FlowState

2. Backend Setup
~~~~~~~~~~~~~~~~

The backend handles all EEG processing and flow state detection:

.. code-block:: bash

   cd backend
   pipenv install
   pipenv shell

3. Frontend Setup
~~~~~~~~~~~~~~~~~

The frontend provides the user interface and visualization:

.. code-block:: bash

   cd frontend
   npm install

4. Connect Your Muse Headband
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Windows**
^^^^^^^^^^^

1. Download and install `BlueMuse <https://github.com/kowalej/BlueMuse>`_
2. Start BlueMuse
3. Turn on your Muse headband
4. BlueMuse will detect and connect to your device automatically

**macOS/Linux**
^^^^^^^^^^^^^^^

1. Install muselsl:

   .. code-block:: bash

      pip install muselsl

2. Start the LSL stream:

   .. code-block:: bash

      muselsl stream

3. Turn on your Muse headband and wait for connection

Running FlowState
-----------------

1. Start the Backend
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd backend
   pipenv run python main.py

The backend will:

* Connect to your Muse headband via LSL
* Start processing EEG signals at 256Hz
* Begin flow state detection algorithms

2. Start the Frontend
~~~~~~~~~~~~~~~~~~~~~

In a new terminal:

.. code-block:: bash

   cd frontend
   npm run dev

Navigate to ``http://localhost:3000`` in your browser.

3. Begin Your Session
~~~~~~~~~~~~~~~~~~~~~

1. Ensure your Muse headband is properly positioned on your head
2. Check the signal quality indicators in the UI
3. Start with a calibration session to establish your baseline
4. Begin your work or learning activity
5. FlowState will provide real-time feedback to optimize your state

First-Time Setup
----------------

Calibration
~~~~~~~~~~~

On first use, FlowState needs to calibrate to your unique brainwave patterns:

1. Click "Start Calibration" in the UI
2. Follow the on-screen prompts:

   * 2 minutes eyes closed (resting state)
   * 2 minutes eyes open (alert state)
   * 2 minutes focused task (concentration state)

3. The system will create your personal baseline profile

Configuration
~~~~~~~~~~~~~

You can customize FlowState's behavior in ``backend/config.yaml``:

.. code-block:: yaml

   # Feedback modalities
   audio:
     binaural_beats: true
     frequency_range: [8, 12]  # Alpha range

   visual:
     strobe_glasses: false
     screen_feedback: true

   # Detection thresholds
   flow_detection:
     alpha_threshold: 0.7
     theta_threshold: 0.6

Quick Test
----------

To verify everything is working:

1. Run the test suite:

   .. code-block:: bash

      cd backend
      pipenv run pytest

2. Check EEG signal reception:

   .. code-block:: bash

      pipenv run python -m backend.core.tests.test_connection

Troubleshooting
---------------

Muse Connection Issues
~~~~~~~~~~~~~~~~~~~~~~

* **Bluetooth not enabled**: Ensure Bluetooth is turned on
* **Headband not detected**: Try turning the Muse off and on again
* **Poor signal quality**: Adjust headband position, wet the sensors slightly

Python Environment Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Import errors**: Ensure you're in the pipenv shell (``pipenv shell``)
* **Version conflicts**: Check Python version with ``python --version``

Next Steps
----------

* Explore the :doc:`/architecture/index` to understand how FlowState works
* Read about the :doc:`/research/index` behind flow state detection
* Check the :doc:`/api/modules` for technical details
* Join our community for tips and support

Support
-------

* GitHub Issues: https://github.com/kvnloo/FlowState/issues
* Documentation: https://kvnloo.github.io/FlowState/
* Community Discord: [Coming Soon]