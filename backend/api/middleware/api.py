"""FlowState API Module.

This module provides the FastAPI-based REST and WebSocket endpoints for the FlowState application.
It handles brainwave data processing and provides real-time feedback for focus enhancement.

Typical usage example:
    uvicorn api:app --reload
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from eeg import Band, brain_read, init_buffers
import json

app = FastAPI(
    title="FlowState API",
    description="API for processing brainwave data and providing focus enhancement feedback",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrainwaveData(BaseModel):
    """Data model for brainwave frequency bands.
    
    Attributes:
        delta: Power in the delta band (0.5-4 Hz)
        theta: Power in the theta band (4-8 Hz)
        alpha: Power in the alpha band (8-13 Hz)
        beta: Power in the beta band (13-30 Hz)
        gamma: Power in the gamma band (30-100 Hz)
    """
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float

class StrobePattern(BaseModel):
    """Data model for visual strobe feedback pattern.
    
    Attributes:
        frequency: Strobe frequency in Hz
        intensity: Light intensity between 0.0 and 1.0
        duration: Pattern duration in seconds
    """
    frequency: float
    intensity: float
    duration: float

@app.post("/api/focus")
async def process_focus(data: BrainwaveData) -> StrobePattern:
    """Process brainwave data and generate appropriate strobe pattern for focus enhancement.
    
    Args:
        data: BrainwaveData object containing power values for each frequency band
        
    Returns:
        StrobePattern object with calculated frequency, intensity, and duration
        
    Notes:
        Focus level is calculated using alpha/theta ratio.
        Higher focus results in higher frequency and lower intensity.
        Lower focus results in lower frequency and higher intensity.
    """
    # Calculate focus level based on alpha/theta ratio
    focus_level = data.alpha / (data.theta if data.theta > 0 else 0.1)
    
    # Map focus level to strobe pattern
    # Higher focus = higher frequency, lower intensity
    # Lower focus = lower frequency, higher intensity
    base_frequency = 10  # Hz
    frequency = base_frequency * (0.5 + (focus_level / 2))  # Scale frequency based on focus
    intensity = 1.0 - (focus_level / 2)  # Inverse relationship with focus
    
    return StrobePattern(
        frequency=min(max(frequency, 5), 15),  # Limit between 5-15 Hz
        intensity=min(max(intensity, 0.2), 1.0),  # Limit between 0.2-1.0
        duration=5.0  # Default duration in seconds
    )

@app.websocket("/ws/eeg")
async def websocket_endpoint(websocket: WebSocket):
    """Establish a WebSocket connection for real-time EEG data processing.
    
    Args:
        websocket: WebSocket object for bi-directional communication
        
    Notes:
        This endpoint accepts EEG data from the client, processes it, and sends back the calculated strobe pattern.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            brainwave_data = json.loads(data)
            
            # Process the data and get strobe pattern
            focus_data = BrainwaveData(**brainwave_data)
            pattern = await process_focus(focus_data)
            
            # Send back the strobe pattern
            await websocket.send_json(pattern.dict())
    except Exception as e:
        print(f"Error in websocket: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
