"""FastAPI endpoints for EEG data streaming and analysis."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict, List
import json

from ..core.inputs.health.providers.muse import EEGProcessor, EEGConfig
from ..core.algorithms.realtime.realtime_processor import RealtimeEEGProcessor

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
connected_clients: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize EEG processors on startup."""
    global eeg_processor, realtime_processor
    
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
