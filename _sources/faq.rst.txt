Frequently Asked Questions (FAQ)
=================================

This page addresses common questions and issues encountered when using FlowState.

Installation & Setup
--------------------

**Q: Which Python version do I need?**
   FlowState requires Python 3.14 or higher. The project uses Pipenv for dependency management, which will handle the virtual environment setup automatically.

**Q: Why am I getting a "requirements.txt not found" error?**
   FlowState uses Pipenv for dependency management. Instead of ``pip install -r requirements.txt``, use:

   .. code-block:: bash

      cd backend
      pipenv install

**Q: Which Muse devices are supported?**
   FlowState supports:

   - Muse 2
   - Muse S
   - Original Muse (2014 model)

   All devices must connect via Bluetooth using BlueMuse (Windows) or muselsl (Linux/macOS).

**Q: Can I use FlowState without a Muse headband?**
   Currently, a Muse headband is required for the core functionality. However, you can run the application in demo mode with simulated data for testing purposes.

Connection Issues
-----------------

**Q: BlueMuse doesn't detect my Muse headband (Windows)**
   Try these steps:

   1. Ensure Bluetooth is enabled in Windows Settings
   2. Turn the Muse off and on again (hold power button for 5 seconds)
   3. Restart BlueMuse
   4. Check if the Muse appears in Windows Bluetooth devices (don't pair it)
   5. If still not working, try updating your Bluetooth drivers

**Q: muselsl stream fails to start (Linux/macOS)**
   Common solutions:

   .. code-block:: bash

      # Install with sudo if permission errors
      sudo pip install muselsl

      # Check if the device is visible
      muselsl list

      # Start stream with specific device
      muselsl stream --name "Muse-XXXX"

**Q: "LSL stream not found" error**
   This indicates the backend can't find the EEG data stream:

   1. Ensure BlueMuse/muselsl is running and connected
   2. Check firewall settings - LSL uses network protocols
   3. Try restarting both the streaming app and backend
   4. Verify no other application is using the LSL stream

Flow State Detection
--------------------

**Q: How accurate is the flow state detection?**
   FlowState uses multiple algorithms for detection:

   - Power Spectral Density analysis (70-80% accuracy)
   - Entropy-based detection (adds 10-15% improvement)
   - Machine learning personalization (improves over time)

   Accuracy improves with calibration and regular use.

**Q: Why isn't FlowState detecting my flow state?**
   Several factors can affect detection:

   - **Poor sensor contact**: Ensure all sensors are touching your skin
   - **Movement artifacts**: Try to minimize head movement
   - **Electrical interference**: Move away from monitors, phones
   - **Individual differences**: Run calibration for personalized baselines
   - **Task type**: Some activities don't induce traditional flow states

**Q: How long does calibration take?**
   Initial calibration takes approximately 6 minutes:

   - 2 minutes eyes closed (baseline)
   - 2 minutes eyes open (alert state)
   - 2 minutes focused task (concentration)

   Recalibration is recommended weekly or when changing environments.

Performance & Technical
-----------------------

**Q: The application is laggy or using high CPU**
   Try these optimizations:

   1. Reduce visualization quality in settings
   2. Lower the update frequency (Settings → Performance)
   3. Disable unnecessary visualizations
   4. Close other applications
   5. Check if your GPU drivers are up to date

**Q: Can I export my session data?**
   Yes, FlowState supports multiple export formats:

   .. code-block:: bash

      # Export as CSV
      python export_data.py --format csv --output sessions.csv

      # Export as JSON
      python export_data.py --format json --output sessions.json

**Q: How much bandwidth does FlowState use?**
   Minimal bandwidth is required:

   - EEG data stream: ~10 KB/s
   - WebSocket communication: ~5 KB/s
   - Total: ~15-20 KB/s

   FlowState works well even on slower connections.

Audio & Binaural Beats
----------------------

**Q: Are binaural beats safe?**
   Binaural beats are generally safe for most people. However:

   - **Epilepsy warning**: Avoid if you have a history of seizures
   - **Hearing sensitivity**: Start with low volumes
   - **Headphones required**: Binaural beats need stereo separation
   - **Not while driving**: Can alter consciousness states

**Q: What frequency ranges are used?**
   FlowState uses these frequency ranges:

   - **Alpha (8-12 Hz)**: Relaxed awareness, creativity
   - **Theta (4-8 Hz)**: Deep meditation, flow states
   - **Beta (13-30 Hz)**: Active concentration
   - **Gamma (30-50 Hz)**: Peak cognitive processing

**Q: Can I customize the audio frequencies?**
   Yes, in ``backend/config.yaml``:

   .. code-block:: yaml

      audio:
        binaural_beats: true
        frequency_range: [8, 12]  # Customize range
        volume: 0.5
        fade_time: 2.0  # seconds

Privacy & Data
--------------

**Q: Is my EEG data stored or shared?**
   - All data is stored **locally** on your device
   - **No cloud upload** unless explicitly enabled
   - **No third-party sharing** ever
   - Data can be deleted anytime via settings

**Q: Can I delete all my data?**
   Yes, to completely remove all data:

   .. code-block:: bash

      python manage_data.py --delete-all --confirm

**Q: Is the application HIPAA compliant?**
   FlowState is designed for personal use and is not HIPAA certified. For medical or clinical use, consult with compliance experts.

Troubleshooting
---------------

**Q: Frontend won't connect to backend**
   Check these common issues:

   1. Backend is running (port 8000 by default)
   2. Frontend ``.env`` file has correct API URL
   3. CORS is properly configured
   4. No firewall blocking local connections
   5. Try accessing ``http://localhost:8000/health``

**Q: "Module not found" errors**
   Ensure you're in the correct virtual environment:

   .. code-block:: bash

      # For backend
      cd backend
      pipenv shell
      pipenv install

      # For frontend
      cd frontend
      npm install

**Q: Tests are failing**
   Common test issues:

   .. code-block:: bash

      # Update test dependencies
      pipenv install --dev

      # Run specific test file
      pipenv run pytest tests/test_flow_detection.py -v

      # Skip integration tests
      pipenv run pytest -m "not integration"

Advanced Usage
--------------

**Q: Can I create custom flow detection algorithms?**
   Yes, implement the ``FlowDetector`` interface:

   .. code-block:: python

      from backend.core.algorithms.base import FlowDetector

      class CustomDetector(FlowDetector):
          def detect(self, eeg_data):
              # Your algorithm here
              return flow_score

**Q: Is there an API for third-party integrations?**
   FlowState provides REST and WebSocket APIs. See the :doc:`/api/modules` documentation for details.

**Q: Can I contribute to the project?**
   Yes! We welcome contributions. See our `GitHub repository <https://github.com/kvnloo/FlowState>`_ for:

   - Contributing guidelines
   - Open issues
   - Feature requests
   - Pull request process

Getting Help
------------

If your question isn't answered here:

1. Check the :doc:`/user_guide` for detailed instructions
2. Review the :doc:`/api/modules` for technical details
3. Search `GitHub Issues <https://github.com/kvnloo/FlowState/issues>`_
4. Ask in our community Discord (coming soon)
5. Create a new issue on GitHub

Common Error Messages
---------------------

**"TypeError: Cannot read property 'channels' of undefined"**
   The EEG data stream is not properly initialized. Check your Muse connection.

**"WebSocket connection failed"**
   The backend server is not running or not accessible. Start it with ``pipenv run python main.py``.

**"CalibrationError: Insufficient baseline data"**
   Complete the full calibration process without interruption.

**"ImportError: No module named 'pylsl'"**
   Install the LSL library: ``pipenv install pylsl``

Version Information
-------------------

- **Current Version**: 0.1.0
- **Python Required**: 3.14+
- **Node.js Required**: 18.0+
- **Last Updated**: November 2025

For version-specific issues, ensure you're using the latest release from the GitHub repository.