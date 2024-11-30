"""FastAPI endpoints for EEG data streaming and analysis."""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, List, Literal, Optional
import json

from core.inputs.health.providers.muse import EEGProcessor, EEGConfig
from core.algorithms.realtime.realtime_processor import RealtimeEEGProcessor
from core.algorithms.realtime.binaural_beats_generator import AdaptiveAudioEngine

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
eeg_processor = None
realtime_processor = None
audio_engine = None
connected_clients: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize processors on startup."""
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
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming EEG data."""
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
            
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
    finally:
        connected_clients.remove(websocket)
        if not connected_clients:
            # Stop monitoring if no clients connected
            eeg_processor.stop_monitoring()
        await websocket.close()

@app.get("/api/devices")
async def get_devices():
    """Get list of available Muse devices."""
    if not eeg_processor:
        return {"error": "EEG processor not initialized"}
    
    devices = await eeg_processor.discover_devices()
    return {"devices": devices}

@app.post("/api/connect/{address}")
async def connect_device(address: str):
    """Connect to a specific Muse device."""
    if not eeg_processor:
        return {"error": "EEG processor not initialized"}
    
    success = await eeg_processor.connect(address)
    return {"success": success}

# Audio Control Endpoints

@app.post("/api/audio/start")
async def start_audio(target_state: Literal['focus', 'flow', 'meditate'], user_state: Optional[Dict] = None):
    """Start binaural beat generation for a target state."""
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
async def stop_audio():
    """Stop binaural beat generation."""
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
async def set_volume(volume: float):
    """Set the audio output volume."""
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
async def get_frequencies(target_state: Literal['focus', 'flow', 'meditate'], user_state: Optional[Dict] = None):
    """Get optimal frequency recommendations."""
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
