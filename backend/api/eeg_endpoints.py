"""EEG Data Streaming and Binaural Beat Audio API Endpoints.

This module provides FastAPI endpoints for real-time EEG data streaming from Muse headbands
and adaptive binaural beat audio generation for flow state optimization. It implements
WebSocket-based streaming for low-latency EEG data delivery and RESTful endpoints for
device management and audio control.

The API integrates with the Muse EEG headband via Bluetooth, processes brainwave data
in real-time, and generates adaptive binaural beats to facilitate flow state induction.

Architecture
------------
The module uses a multi-tier architecture:
- **WebSocket Layer**: Real-time bidirectional communication for EEG streaming
- **Processing Layer**: EEG signal processing and feature extraction
- **Audio Engine**: Adaptive binaural beat generation based on brainwave response
- **Device Layer**: Bluetooth communication with Muse headband

Key Components:
    - :class:`EEGProcessor`: Handles Muse device connection and raw data acquisition
    - :class:`RealtimeEEGProcessor`: Performs real-time signal processing and feature extraction
    - :class:`AdaptiveAudioEngine`: Generates binaural beats adapted to user's brain state

Examples
--------
Connect to WebSocket for real-time EEG streaming::

    const ws = new WebSocket('ws://localhost:8000/ws/eeg');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Alpha/Theta ratio:', data.alpha_theta_ratio);
        console.log('Band powers:', data.band_powers);
    };

Start adaptive binaural beat audio::

    curl -X POST "http://localhost:8000/api/audio/start" \\
         -H "Content-Type: application/json" \\
         -d '{"target_state": "flow", "user_state": {"baseline_alpha": 10.5}}'

See Also
--------
:mod:`core.inputs.health.providers.muse` : Muse EEG device interface
:mod:`core.algorithms.realtime.realtime_processor` : Real-time EEG processing
:mod:`core.algorithms.realtime.binaural_beats_generator` : Binaural beat generation

Notes
-----
- WebSocket connections automatically start EEG monitoring when the first client connects
- EEG monitoring stops when the last client disconnects to conserve battery
- CORS is enabled for all origins in development; restrict in production
- Audio engine requires API key for production use
"""

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, List, Literal, Optional
import json

from core.inputs.health.providers.muse import EEGProcessor, EEGConfig
from core.algorithms.realtime.realtime_processor import RealtimeEEGProcessor
from core.algorithms.realtime.binaural_beats_generator import AdaptiveAudioEngine

app = FastAPI(
    title="FlowState EEG API",
    description="Real-time EEG streaming and adaptive binaural beat generation for flow state optimization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
eeg_processor: Optional[EEGProcessor] = None
realtime_processor: Optional[RealtimeEEGProcessor] = None
audio_engine: Optional[AdaptiveAudioEngine] = None
connected_clients: List[WebSocket] = []

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize EEG processors and audio engine on application startup.

    Creates global instances of:
    - EEG processor for Muse device communication
    - Realtime processor for signal processing and feature extraction
    - Adaptive audio engine for binaural beat generation

    The processors are configured with default parameters optimized for
    flow state detection using 4-second buffers with 1-second epochs.
    """
    global eeg_processor, realtime_processor, audio_engine

    # Initialize Muse EEG processor
    config = EEGConfig(
        buffer_length=4.0,
        epoch_length=1.0,
        overlap_length=0.5,
    )
    eeg_processor = EEGProcessor(config)

    # Initialize realtime processor
    channels = ['TP9', 'AF7', 'AF8', 'TP10']
    realtime_processor = RealtimeEEGProcessor(
        channels=channels,
        sampling_rate=256  # Muse sampling rate
    )

    # Initialize audio engine
    audio_engine = AdaptiveAudioEngine(api_key="development")  # Replace with actual API key in production

@app.websocket("/ws/eeg")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time EEG data streaming.

    Establishes a persistent WebSocket connection for streaming EEG data from a Muse
    headband. The endpoint automatically initiates device connection on first client
    connection and streams processed EEG features including band powers, signal quality,
    and alpha/theta ratio.

    Parameters
    ----------
    websocket : WebSocket
        The WebSocket connection instance.

    WebSocket Protocol
    ------------------
    **Connection**:
        Client initiates WebSocket handshake to ws://host:port/ws/eeg

    **Data Format** (Server -> Client):
        JSON messages sent every ~100ms containing::

            {
                "timestamp": 1234567890.123,
                "alpha_theta_ratio": 1.25,
                "band_powers": {
                    "delta": 2.5,
                    "theta": 8.3,
                    "alpha": 10.4,
                    "beta": 15.2,
                    "gamma": 25.0
                },
                "signal_quality": {
                    "TP9": 0.95,
                    "AF7": 0.98,
                    "AF8": 0.92,
                    "TP10": 0.97
                }
            }

    Raises
    ------
    WebSocketDisconnect
        When client disconnects from the WebSocket.
    Exception
        On EEG processing errors or device communication failures.

    Examples
    --------
    JavaScript client connection::

        const ws = new WebSocket('ws://localhost:8000/ws/eeg');

        ws.onopen = () => {
            console.log('Connected to EEG stream');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateVisualization(data.band_powers);
            updateFlowScore(data.alpha_theta_ratio);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

    Notes
    -----
    - First connection triggers automatic Muse device discovery and connection
    - EEG monitoring stops when last client disconnects to conserve battery
    - Data is sent at ~10Hz (every 100ms) to balance latency and bandwidth
    - Audio engine is automatically updated with brainwave data for adaptation
    """
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        # Start EEG monitoring if not already started
        if not eeg_processor.muse:
            await eeg_processor.connect()

        # Create data queue for realtime processing
        data_queue = asyncio.Queue()

        # Start processing pipeline
        process_task = asyncio.create_task(
            realtime_processor.run_pipeline(data_queue)
        )

        # Stream data to client
        while True:
            # Get latest EEG data
            chunk = await eeg_processor.process_chunk()
            await data_queue.put(chunk)

            # Extract features including Alpha/Theta ratio
            features = await realtime_processor.extract_features()

            # Calculate Alpha/Theta ratio
            alpha = features['band_powers']['alpha']
            theta = features['band_powers']['theta']
            ratio = alpha / theta if theta > 0 else 0

            # Update audio engine with brainwave response
            if audio_engine:
                audio_engine.update_brainwave_response(
                    alpha=alpha,
                    theta=theta,
                    beta=features['band_powers'].get('beta', 0),
                    gamma=features['band_powers'].get('gamma', 0)
                )

            # Prepare data for client
            data = {
                'timestamp': chunk['timestamp'],
                'alpha_theta_ratio': ratio,
                'band_powers': features['band_powers'],
                'signal_quality': features['signal_quality']
            }

            # Send to client
            await websocket.send_text(json.dumps(data))

            # Brief sleep to prevent overwhelming
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        connected_clients.remove(websocket)
        if not connected_clients:
            # Stop monitoring if no clients connected
            eeg_processor.stop_monitoring()
        await websocket.close()

@app.get("/api/devices")
async def get_devices() -> Dict[str, List[Dict[str, str]]]:
    """Discover available Muse EEG devices via Bluetooth.

    Scans for nearby Muse headbands that are in pairing mode. Returns a list
    of discovered devices with their Bluetooth addresses and signal strengths.

    Returns
    -------
    dict
        Response containing list of discovered devices::

            {
                "devices": [
                    {
                        "name": "Muse-1234",
                        "address": "00:55:DA:B1:23:45",
                        "rssi": -65
                    }
                ]
            }

    Raises
    ------
    HTTPException
        500 error if EEG processor is not initialized.

    Examples
    --------
    cURL request::

        curl -X GET "http://localhost:8000/api/devices"

    Python request::

        import requests
        response = requests.get('http://localhost:8000/api/devices')
        devices = response.json()['devices']
        for device in devices:
            print(f"Found: {device['name']} at {device['address']}")

    Notes
    -----
    - Scan duration is approximately 10 seconds
    - Muse device must be powered on and in pairing mode
    - Signal strength (RSSI) indicates proximity; higher values (closer to 0) are better
    """
    if not eeg_processor:
        raise HTTPException(status_code=500, detail="EEG processor not initialized")

    devices = await eeg_processor.discover_devices()
    return {"devices": devices}

@app.post("/api/connect/{address}")
async def connect_device(address: str) -> Dict[str, bool]:
    """Connect to a specific Muse device by Bluetooth address.

    Establishes Bluetooth connection to a Muse headband using its MAC address.
    The connection persists until explicitly disconnected or the device is powered off.

    Parameters
    ----------
    address : str
        Bluetooth MAC address of the Muse device (e.g., "00:55:DA:B1:23:45").

    Returns
    -------
    dict
        Connection result::

            {
                "success": true
            }

    Raises
    ------
    HTTPException
        500 error if EEG processor is not initialized.

    Examples
    --------
    cURL request::

        curl -X POST "http://localhost:8000/api/connect/00:55:DA:B1:23:45"

    Python request::

        import requests
        address = "00:55:DA:B1:23:45"
        response = requests.post(f'http://localhost:8000/api/connect/{address}')
        if response.json()['success']:
            print("Connected successfully")

    Notes
    -----
    - Device must be discoverable and within Bluetooth range
    - Connection typically takes 5-10 seconds
    - Previous connection is automatically closed before new connection
    """
    if not eeg_processor:
        raise HTTPException(status_code=500, detail="EEG processor not initialized")

    success = await eeg_processor.connect(address)
    return {"success": success}

# Audio Control Endpoints

@app.post("/api/audio/start")
async def start_audio(
    target_state: Literal['focus', 'flow', 'meditate'],
    user_state: Optional[Dict] = None
) -> Dict[str, any]:
    """Start adaptive binaural beat audio generation for a target mental state.

    Initiates audio generation optimized for the specified target state (focus, flow,
    or meditate). The audio engine uses AI to determine optimal frequencies and
    adapts in real-time based on EEG feedback.

    Parameters
    ----------
    target_state : {'focus', 'flow', 'meditate'}
        Desired mental state to facilitate:
        - 'focus': Beta frequencies for concentration and alertness
        - 'flow': Alpha-theta crossover for optimal performance
        - 'meditate': Theta frequencies for deep relaxation
    user_state : dict, optional
        User's current brainwave state for personalization::

            {
                "baseline_alpha": 10.5,
                "baseline_theta": 6.3,
                "sensitivity": 0.8
            }

    Returns
    -------
    dict
        Audio generation status and parameters::

            {
                "success": true,
                "strobe_frequency": 10.2,
                "message": "Started audio for flow state"
            }

    Raises
    ------
    HTTPException
        500 error if audio engine is not initialized or generation fails.

    Examples
    --------
    Start flow state audio with defaults::

        curl -X POST "http://localhost:8000/api/audio/start" \\
             -H "Content-Type: application/json" \\
             -d '{"target_state": "flow"}'

    Start with personalized user state::

        curl -X POST "http://localhost:8000/api/audio/start" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "target_state": "flow",
                 "user_state": {
                     "baseline_alpha": 10.5,
                     "baseline_theta": 6.3
                 }
             }'

    Python request::

        import requests
        response = requests.post(
            'http://localhost:8000/api/audio/start',
            json={'target_state': 'flow'}
        )
        if response.json()['success']:
            strobe_freq = response.json()['strobe_frequency']
            print(f"Audio started at {strobe_freq} Hz")

    Notes
    -----
    - Audio adapts automatically based on EEG feedback from WebSocket stream
    - Multiple audio sessions from different clients share the same engine
    - Calling start while audio is already playing will restart with new parameters
    """
    if not audio_engine:
        raise HTTPException(status_code=500, detail="Audio engine not initialized")

    try:
        strobe_freq = await audio_engine.start(target_state, user_state)
        return {
            "success": True,
            "strobe_frequency": strobe_freq,
            "message": f"Started audio for {target_state} state"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/stop")
async def stop_audio() -> Dict[str, any]:
    """Stop binaural beat audio generation.

    Immediately halts audio generation and releases audio resources. Can be called
    even if audio is not currently playing (will return success).

    Returns
    -------
    dict
        Stop operation result::

            {
                "success": true,
                "message": "Stopped audio generation"
            }

    Raises
    ------
    HTTPException
        500 error if audio engine is not initialized or stop operation fails.

    Examples
    --------
    cURL request::

        curl -X POST "http://localhost:8000/api/audio/stop"

    Python request::

        import requests
        response = requests.post('http://localhost:8000/api/audio/stop')
        print(response.json()['message'])

    Notes
    -----
    - Safe to call multiple times
    - Does not disconnect EEG streaming (WebSocket remains active)
    """
    if not audio_engine:
        raise HTTPException(status_code=500, detail="Audio engine not initialized")

    try:
        await audio_engine.stop()
        return {
            "success": True,
            "message": "Stopped audio generation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/volume")
async def set_volume(volume: float) -> Dict[str, any]:
    """Set the audio output volume level.

    Adjusts the playback volume for binaural beat audio. Volume changes take
    effect immediately without interrupting playback.

    Parameters
    ----------
    volume : float
        Volume level from 0.0 (mute) to 1.0 (maximum).

    Returns
    -------
    dict
        Volume update confirmation::

            {
                "success": true,
                "message": "Set volume to 0.7"
            }

    Raises
    ------
    HTTPException
        400 error if volume is outside valid range [0.0, 1.0].
        500 error if audio engine is not initialized or volume update fails.

    Examples
    --------
    Set volume to 70%::

        curl -X POST "http://localhost:8000/api/audio/volume" \\
             -H "Content-Type: application/json" \\
             -d '{"volume": 0.7}'

    Python request::

        import requests
        response = requests.post(
            'http://localhost:8000/api/audio/volume',
            json={'volume': 0.7}
        )
        print(response.json()['message'])

    Notes
    -----
    - Volume is linear from 0.0 to 1.0
    - Recommended range is 0.3 to 0.7 for comfortable listening
    - Volume setting persists across audio start/stop cycles
    """
    if not audio_engine:
        raise HTTPException(status_code=500, detail="Audio engine not initialized")

    if not 0 <= volume <= 1:
        raise HTTPException(status_code=400, detail="Volume must be between 0 and 1")

    try:
        audio_engine.set_volume(volume)
        return {
            "success": True,
            "message": f"Set volume to {volume}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/frequencies")
async def get_frequencies(
    target_state: Literal['focus', 'flow', 'meditate'],
    user_state: Optional[Dict] = None
) -> Dict[str, any]:
    """Get AI-recommended optimal frequency parameters for a target state.

    Uses AI analysis to determine ideal binaural beat frequencies based on the
    target mental state and optional user baseline data. Returns frequency
    recommendations without starting audio playback.

    Parameters
    ----------
    target_state : {'focus', 'flow', 'meditate'}
        Target mental state for frequency optimization.
    user_state : dict, optional
        User's brainwave baseline for personalization (see :func:`start_audio`).

    Returns
    -------
    dict
        Frequency recommendations and confidence score::

            {
                "base_frequency": 200.0,
                "beat_frequency": 10.2,
                "strobe_frequency": 10.2,
                "confidence": 0.87,
                "reasoning": "Alpha-theta crossover optimal for flow state..."
            }

    Raises
    ------
    HTTPException
        500 error if audio engine is not initialized or analysis fails.

    Examples
    --------
    Get flow state recommendations::

        curl -X GET "http://localhost:8000/api/audio/frequencies?target_state=flow"

    Get personalized recommendations::

        curl -X GET "http://localhost:8000/api/audio/frequencies?target_state=focus&user_state=%7B%22baseline_alpha%22:10.5%7D"

    Python request::

        import requests
        response = requests.get(
            'http://localhost:8000/api/audio/frequencies',
            params={'target_state': 'flow'}
        )
        rec = response.json()
        print(f"Base: {rec['base_frequency']} Hz")
        print(f"Beat: {rec['beat_frequency']} Hz")
        print(f"Confidence: {rec['confidence']}")

    Notes
    -----
    - Recommendations are generated by AI based on neuroscience research
    - Confidence score indicates AI's certainty in the recommendation
    - Reasoning field provides human-readable explanation
    - Does not initiate audio playback; use :func:`start_audio` to play
    """
    if not audio_engine:
        raise HTTPException(status_code=500, detail="Audio engine not initialized")

    try:
        recommendation = await audio_engine.get_optimal_frequencies(target_state, user_state)
        return {
            "base_frequency": recommendation.base_freq,
            "beat_frequency": recommendation.beat_freq,
            "strobe_frequency": recommendation.strobe_freq,
            "confidence": recommendation.confidence,
            "reasoning": recommendation.reasoning
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
