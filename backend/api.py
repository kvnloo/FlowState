from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from eeg import Band, brain_read, init_buffers
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrainwaveData(BaseModel):
    delta: float
    theta: float
    alpha: float
    beta: float
    gamma: float

class StrobePattern(BaseModel):
    frequency: float
    intensity: float
    duration: float

@app.post("/api/focus")
async def process_focus(data: BrainwaveData):
    """Process brainwave data and return appropriate strobe pattern"""
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
