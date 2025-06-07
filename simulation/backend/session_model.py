import json
import datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Optional

# For simplicity, we'll use a file-based storage
# In production, this would be a database
STORAGE_DIR = Path(__file__).resolve().parent.parent / "data"


class SessionModel:
    """
    Model for managing and persisting session data.
    Handles storage and retrieval of session information, messages, and stage transitions.
    """

    def __init__(self):
        """
        Initialize the session model and ensure storage directory exists
        """
        self.storage_dir = STORAGE_DIR
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a session by ID
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data or empty dict if not found
        """
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            return {}
            
        try:
            return json.loads(session_file.read_text())
        except json.JSONDecodeError:
            return {}
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Save session data to storage
        
        Args:
            session_data: Session data including session_id
            
        Returns:
            True if successful, False otherwise
        """
        if "session_id" not in session_data:
            return False
            
        session_id = session_data["session_id"]
        session_file = self.storage_dir / f"{session_id}.json"
        
        try:
            session_file.write_text(json.dumps(session_data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        Add a message to a session
        
        Args:
            session_id: Session identifier
            message: Message data including sender, text, timestamp
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        
        if not session:
            return False
            
        if "messages" not in session:
            session["messages"] = []
            
        # Ensure timestamp is serializable
        if "timestamp" in message and isinstance(message["timestamp"], dt.datetime):
            message["timestamp"] = message["timestamp"].isoformat()
            
        session["messages"].append(message)
        return self.save_session(session)
    
    def update_stage(self, session_id: str, stage: str, scores: Dict[str, float]) -> bool:
        """
        Update stage and scores for a session
        
        Args:
            session_id: Session identifier
            stage: New stage
            scores: Updated scores
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        
        if not session:
            return False
            
        session["stage"] = stage
        session["scores"] = scores
        session["last_updated"] = dt.datetime.now().isoformat()
        
        # Add stage transition to history
        if "stage_history" not in session:
            session["stage_history"] = []
            
        session["stage_history"].append({
            "timestamp": dt.datetime.now().isoformat(),
            "stage": stage,
            "scores": scores
        })
        
        return self.save_session(session)
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session data
        """
        sessions = []
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                session = json.loads(session_file.read_text())
                if session.get("user_id") == user_id:
                    sessions.append(session)
            except json.JSONDecodeError:
                continue
                
        return sessions
    
    def create_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Create a new session
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            New session data
        """
        session = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": dt.datetime.now().isoformat(),
            "stage": "APP",  # Start in Acquaintance Path
            "scores": {"trust": 0, "open": 0},
            "messages": [],
            "stage_history": [{
                "timestamp": dt.datetime.now().isoformat(),
                "stage": "APP",
                "scores": {"trust": 0, "open": 0}
            }]
        }
        
        self.save_session(session)
        return session
    
    def get_latest_message(self, session_id: str, sender: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the latest message in a session, optionally filtered by sender
        
        Args:
            session_id: Session identifier
            sender: Optional sender filter
            
        Returns:
            Latest message or empty dict if none found
        """
        session = self.get_session(session_id)
        
        if not session or "messages" not in session or not session["messages"]:
            return {}
            
        messages = session["messages"]
        
        if sender:
            messages = [m for m in messages if m.get("sender") == sender]
            
        if not messages:
            return {}
            
        return messages[-1]  # Return the last message