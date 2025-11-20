"""
EDEN Planning Server
FastAPI server for planning layer (separate from brain_server)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
from datetime import datetime
import time

from .cosmos_planner import CosmosLite
from .ollama_planner import OllamaPlanner
from .config import *


app = FastAPI(title="EDEN Planning Layer API")

# Initialize planners
cosmos_planner = None
ollama_planner = None

# Planning history (for context)
planning_history = []


class PlanningRequest(BaseModel):
    goal: str
    scene_description: str
    context: Optional[Dict] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None


class PlanningResponse(BaseModel):
    plan_id: str
    actions: List[str]
    reasoning: str
    confidence: float
    model_used: str
    inference_time: float
    timestamp: str
    
    class Config:
        protected_namespaces = ()


@app.on_event("startup")
async def startup_event():
    """Initialize planners on startup"""
    global cosmos_planner, ollama_planner
    
    print("[PlanningServer] Initializing planners...")
    
    # Try to initialize Cosmos planner
    try:
        cosmos_planner = CosmosLite()
        if cosmos_planner.is_available():
            print("[PlanningServer] ✓ Cosmos planner available")
        else:
            print("[PlanningServer] ⚠ Cosmos planner not available (will use Ollama)")
            cosmos_planner = None
    except Exception as e:
        print(f"[PlanningServer] Cosmos initialization error: {e}")
        cosmos_planner = None
    
    # Initialize Ollama planner
    try:
        ollama_planner = OllamaPlanner()
        if ollama_planner.is_available():
            print("[PlanningServer] ✓ Ollama planner available")
        else:
            print("[PlanningServer] ⚠ Ollama planner not available")
            ollama_planner = None
    except Exception as e:
        print(f"[PlanningServer] Ollama initialization error: {e}")
        ollama_planner = None
    
    if not cosmos_planner and not ollama_planner:
        print("[PlanningServer] ⚠ No planners available! Planning will fail.")
    else:
        print("[PlanningServer] ✓ Planning server ready")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "EDEN Planning Layer",
        "status": "running",
        "cosmos_available": cosmos_planner.is_available() if cosmos_planner else False,
        "ollama_available": ollama_planner.is_available() if ollama_planner else False
    }


@app.get("/api/plan/status")
async def get_status():
    """Get planner status"""
    return {
        "cosmos_available": cosmos_planner.is_available() if cosmos_planner else False,
        "ollama_available": ollama_planner.is_available() if ollama_planner else False,
        "active_planner": "cosmos" if cosmos_planner and cosmos_planner.is_available() else ("ollama" if ollama_planner else "none")
    }


@app.post("/api/plan/generate", response_model=PlanningResponse)
async def generate_plan(request: PlanningRequest):
    """
    Generate action plan based on goal and scene description.
    
    Input from cognitive layer:
    - goal: What the robot should do
    - scene_description: Current scene context from VLM
    - context: Additional context from cognitive layer
    """
    global planning_history, cosmos_planner, ollama_planner
    
    # Validate input
    if not request.goal or not request.scene_description:
        raise HTTPException(status_code=400, detail="goal and scene_description are required")
    
    # Truncate inputs if too long
    goal = request.goal[:500] if len(request.goal) > 500 else request.goal
    scene_description = request.scene_description[:MAX_SCENE_DESCRIPTION_LENGTH]
    
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    # Try Cosmos first, fallback to Ollama
    result = None
    planner_used = None
    
    try:
        # Try Cosmos if available
        if cosmos_planner and cosmos_planner.is_available():
            try:
                result = cosmos_planner.plan(
                    goal=goal,
                    scene_description=scene_description,
                    context=request.context
                )
                planner_used = "cosmos"
                
                # Check if inference was too slow
                if result.get("inference_time", 0) > INFERENCE_TIMEOUT:
                    print(f"[PlanningServer] Cosmos inference slow ({result['inference_time']:.2f}s), but completed")
                    
            except Exception as e:
                print(f"[PlanningServer] Cosmos planning failed: {e}")
                print("[PlanningServer] Falling back to Ollama...")
                # Don't set cosmos_planner = None here, just fall through to Ollama
        
        # Fallback to Ollama
        if not result and ollama_planner and ollama_planner.is_available():
            try:
                result = ollama_planner.plan(
                    goal=goal,
                    scene_description=scene_description,
                    context=request.context
                )
                planner_used = "ollama"
            except Exception as e:
                print(f"[PlanningServer] Ollama planning failed: {e}")
        
        if not result:
            raise HTTPException(
                status_code=503,
                detail="No planners available. Check GPU/Cosmos setup or Ollama service."
            )
        
        # Add to history (limit size)
        planning_history.append({
            "plan_id": plan_id,
            "goal": goal,
            "timestamp": datetime.now().isoformat(),
            "model_used": planner_used
        })
        if len(planning_history) > MAX_PLANNING_HISTORY:
            planning_history.pop(0)
        
        # Format response
        response = PlanningResponse(
            plan_id=plan_id,
            actions=result.get("actions", []),
            reasoning=result.get("reasoning", ""),
            confidence=result.get("confidence", 0.5),
            model_used=result.get("model_used", planner_used),
            inference_time=result.get("inference_time", time.time() - start_time),
            timestamp=datetime.now().isoformat()
        )
        
        print(f"[PlanningServer] ✓ Plan generated: {plan_id} ({planner_used}, {len(response.actions)} actions)")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PlanningServer] Planning error: {e}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@app.get("/api/plan/history")
async def get_history():
    """Get recent planning history"""
    return {
        "history": planning_history,
        "count": len(planning_history)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

