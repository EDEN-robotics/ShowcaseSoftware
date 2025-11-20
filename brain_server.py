"""
EDEN Brain Server: FastAPI backend with WebSocket support for real-time graph updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import asyncio
from cognitive_layer.ego_core import EgoGraph

app = FastAPI(title="EDEN Cognitive Layer API")

# Initialize the Ego Graph
ego_graph = EgoGraph()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast graph state to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()


# Pydantic models for request/response
class PersonalityUpdate(BaseModel):
    trait: str
    value: float

class InteractionRequest(BaseModel):
    user: str
    action: str

class EventRequest(BaseModel):
    event_type: str  # "trauma" or "kindness"
    description: str

class EventFrameRequest(BaseModel):
    frame_id: Optional[str] = None
    timestamp: Optional[str] = None
    description: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    detected_objects: Optional[List[str]] = None
    detected_actions: Optional[List[str]] = None
    emotional_tone: Optional[str] = None
    scene_context: Optional[str] = None
    metadata: Optional[Dict] = None
    source: str = "camera_frame"

class BatchEventRequest(BaseModel):
    events: List[EventFrameRequest]


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the frontend HTML"""
    template_path = os.path.join(os.path.dirname(__file__), "cognitive_layer", "templates", "index.html")
    with open(template_path, "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/god_mode/set_personality")
async def set_personality(update: PersonalityUpdate):
    """Update personality trait and broadcast graph state"""
    result = ego_graph.update_personality(update.trait, update.value)
    
    # Broadcast to all WebSocket clients
    await manager.broadcast({
        "type": "personality_update",
        "data": result
    })
    
    return {
        "status": "success",
        "personality": result["personality"],
        "message": f"Updated {update.trait} to {update.value}"
    }


@app.post("/api/interact")
async def interact(request: InteractionRequest):
    """Process an interaction and return thought trace"""
    result = ego_graph.process_interaction(request.user, request.action)
    
    # Broadcast graph update
    await manager.broadcast({
        "type": "interaction",
        "data": result
    })
    
    return result


@app.post("/api/event/inject")
async def inject_event(event: EventRequest):
    """Inject a trauma or kindness event"""
    if event.event_type == "trauma":
        result = ego_graph.inject_trauma(event.description)
    elif event.event_type == "kindness":
        result = ego_graph.inject_kindness(event.description)
    else:
        return {"status": "error", "message": "Unknown event type"}
    
    # Broadcast graph update
    await manager.broadcast({
        "type": "event_injected",
        "event_type": event.event_type,
        "data": result
    })
    
    return {
        "status": "success",
        "event_type": event.event_type,
        "data": result
    }


@app.get("/api/graph/state")
async def get_graph_state():
    """Get current graph state"""
    return ego_graph.get_graph_state()


@app.post("/api/events/process")
async def process_event(event: EventFrameRequest):
    """Process a single event frame through cognitive analysis"""
    event_dict = event.dict()
    result = ego_graph.process_event_frame(event_dict)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "event_processed",
        "data": result
    })
    
    return result


@app.post("/api/events/batch")
async def process_event_batch(batch: BatchEventRequest):
    """Process a batch of events"""
    events_list = [e.dict() for e in batch.events]
    result = ego_graph.process_event_batch(events_list)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "batch_processed",
        "data": result
    })
    
    return result


@app.get("/api/events/config")
async def get_event_config():
    """Get event processing configuration"""
    from cognitive_layer import config
    return {
        "ollama_url": config.OLLAMA_BASE_URL,
        "model": config.DEFAULT_MODEL,
        "thresholds": config.THRESHOLDS,
        "personality_modulation": config.PERSONALITY_MODULATION,
        "ollama_available": ego_graph.cognitive_analyzer._check_ollama_available()
    }


@app.post("/api/events/config")
async def update_event_config(config_update: Dict):
    """Update event processing configuration"""
    from cognitive_layer import config
    
    if "ollama_url" in config_update:
        ego_graph.cognitive_analyzer.ollama_url = config_update["ollama_url"]
        config.OLLAMA_BASE_URL = config_update["ollama_url"]
    
    if "model" in config_update:
        ego_graph.cognitive_analyzer.model_name = config_update["model"]
        config.DEFAULT_MODEL = config_update["model"]
    
    return {
        "status": "updated",
        "config": {
            "ollama_url": ego_graph.cognitive_analyzer.ollama_url,
            "model": ego_graph.cognitive_analyzer.model_name
        }
    }


@app.post("/api/events/process")
async def process_event(event: EventFrameRequest):
    """Process a single event frame through cognitive analysis"""
    event_dict = event.dict()
    result = ego_graph.process_event_frame(event_dict)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "event_processed",
        "data": result
    })
    
    return result


@app.post("/api/events/batch")
async def process_event_batch(batch: BatchEventRequest):
    """Process a batch of events"""
    events_list = [e.dict() for e in batch.events]
    result = ego_graph.process_event_batch(events_list)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "batch_processed",
        "data": result
    })
    
    return result


@app.get("/api/events/config")
async def get_event_config():
    """Get event processing configuration"""
    from cognitive_layer import config
    return {
        "ollama_url": config.OLLAMA_BASE_URL,
        "model": config.DEFAULT_MODEL,
        "thresholds": config.THRESHOLDS,
        "personality_modulation": config.PERSONALITY_MODULATION,
        "ollama_available": ego_graph.cognitive_analyzer._check_ollama_available()
    }


@app.post("/api/events/config")
async def update_event_config(config_update: Dict):
    """Update event processing configuration"""
    from cognitive_layer import config
    
    if "ollama_url" in config_update:
        ego_graph.cognitive_analyzer.ollama_url = config_update["ollama_url"]
        config.OLLAMA_BASE_URL = config_update["ollama_url"]
    
    if "model" in config_update:
        ego_graph.cognitive_analyzer.model_name = config_update["model"]
        config.DEFAULT_MODEL = config_update["model"]
    
    return {
        "status": "updated",
        "config": {
            "ollama_url": ego_graph.cognitive_analyzer.ollama_url,
            "model": ego_graph.cognitive_analyzer.model_name
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time graph updates"""
    await manager.connect(websocket)
    
    # Send initial graph state
    initial_state = ego_graph.get_graph_state()
    await websocket.send_json({
        "type": "initial_state",
        "data": initial_state
    })
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """Initialize demo data on startup"""
    # Add some initial demo memories
    from cognitive_layer.ego_core import MemoryNode
    
    # Add a user node for demo
    demo_memory = MemoryNode(
        id="demo_001",
        content="Initial system state: EDEN is ready to interact",
        importance=0.3,
        user_context=None,
        node_type="memory"
    )
    ego_graph.add_memory_node(demo_memory)
    
    print("EDEN Cognitive Layer initialized")
    print(f"Graph nodes: {ego_graph.graph.number_of_nodes()}")
    print(f"Graph edges: {ego_graph.graph.number_of_edges()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

