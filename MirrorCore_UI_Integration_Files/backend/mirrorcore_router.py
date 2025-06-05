from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
import datetime as dt
from typing import Dict, Any, List, Optional

# Change from relative to absolute imports
from stage_controller import StageController
from session_model import SessionModel
from fmt_loader import FmtLoader

# Create router
router = APIRouter(prefix="/mirrorcore", tags=["mirrorcore"])

# Models
class Message(BaseModel):
    text: str
    sender: str  # "diego" or "client"
    timestamp: Optional[dt.datetime] = None

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    stage: str
    scores: Dict[str, float]
    flags: Optional[Dict[str, Any]] = None

class FmtResponse(BaseModel):
    message: str
    fmt_id: str
    fmt_name: str
    stage: str
    tone: str
    ai_behaviors: List[str]

# Dependencies
def get_session_model():
    return SessionModel()

def get_stage_controller(user_id: str):
    return StageController(user_id)

def get_fmt_loader():
    return FmtLoader()

# Routes
@router.post("/message", response_model=FmtResponse)
async def process_message(
    message: Message,
    user_id: str = Body(...),
    session_id: Optional[str] = Body(None),
    session_model: SessionModel = Depends(get_session_model),
    fmt_loader: FmtLoader = Depends(get_fmt_loader)
):
    """
    Process a message from the client and return a response
    """
    # Set timestamp if not provided
    if not message.timestamp:
        message.timestamp = dt.datetime.now()
    
    # Get or create session
    if not session_id:
        # Create new controller for this user
        controller = StageController(user_id)
        session_id = controller.session_id
        # Create new session in storage
        session_model.create_session(user_id, session_id)
    else:
        # Load existing session
        session = session_model.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        # Create controller with existing session data
        controller = StageController(user_id)
        controller.session_id = session_id
        controller.current_stage = session.get("stage", "APP")
        # Load flags if available
        if "flags" in session:
            controller.flags = session["flags"]
    
    # Get last Diego message if available
    last_diego = session_model.get_latest_message(session_id, "diego")
    if last_diego and "text" in last_diego and "timestamp" in last_diego:
        # Parse timestamp if it's a string
        ts = last_diego["timestamp"]
        if isinstance(ts, str):
            ts = dt.datetime.fromisoformat(ts)
        controller.record_diego(last_diego["text"], ts)
    
    # Process client message
    result = controller.record_cl(message.text, message.timestamp)
    
    # Save message to session
    session_model.add_message(session_id, {
        "sender": message.sender,
        "text": message.text,
        "timestamp": message.timestamp
    })
    
    # Update session with new stage and scores
    session_model.update_stage(session_id, result["stage"], result["scores"])
    
    # Get appropriate FMT based on stage
    fmt = fmt_loader.get_fmt(result["stage"])
    message_text = fmt_loader.get_fmt_variation(fmt)
    
    # Create response
    response = FmtResponse(
        message=message_text,
        fmt_id=fmt["fmt_id"],
        fmt_name=fmt["fmt_name"],
        stage=result["stage"],
        tone=fmt["tone"],
        ai_behaviors=fmt["ai_behaviors"]
    )
    
    return response

@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    session_model: SessionModel = Depends(get_session_model)
):
    """
    Get session information
    """
    session = session_model.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionInfo(
        session_id=session_id,
        user_id=session.get("user_id", ""),
        stage=session.get("stage", "APP"),
        scores=session.get("scores", {"trust": 0, "open": 0}),
        flags=session.get("flags", {})
    )

@router.post("/flag/{session_id}")
async def set_flag(
    session_id: str,
    flag_name: str = Body(...),
    flag_value: Any = Body(...),
    session_model: SessionModel = Depends(get_session_model)
):
    """
    Set a flag for a session
    """
    session = session_model.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "flags" not in session:
        session["flags"] = {}
    
    session["flags"][flag_name] = flag_value
    session_model.save_session(session)
    
    return {"status": "success", "message": f"Flag {flag_name} set to {flag_value}"}

@router.get("/user/{user_id}/sessions", response_model=List[SessionInfo])
async def get_user_sessions(
    user_id: str,
    session_model: SessionModel = Depends(get_session_model)
):
    """
    Get all sessions for a user
    """
    sessions = session_model.get_user_sessions(user_id)
    
    return [
        SessionInfo(
            session_id=session.get("session_id", ""),
            user_id=user_id,
            stage=session.get("stage", "APP"),
            scores=session.get("scores", {"trust": 0, "open": 0}),
            flags=session.get("flags", {})
        )
        for session in sessions
    ]