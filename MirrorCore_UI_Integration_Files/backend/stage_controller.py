import json
import uuid
import datetime as dt
from pathlib import Path
from typing import Dict, Any, Optional, List

# Change from relative to absolute import
from score_interpreter import score_interaction, RollingScorer

# Path to stage definitions file
CFG_PATH = Path(__file__).resolve().parent.parent / "config" / "stage_definitions.json"


class StageController:
    """
    Controller for stage orchestration in the MirrorCore system.
    Handles stage transitions based on interaction scores and defined rules.
    """

    def __init__(self, user_id: str):
        """
        Initialize a new StageController for a user
        
        Args:
            user_id: Unique identifier for the user
        """
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.load_stage_config()
        self.current_stage = "APP"  # Start in Acquaintance Path
        self.history = RollingScorer(window=10)
        self.last_diego_msg = ""
        self.last_diego_ts = None
        self.consecutive_meaningful = 0  # resets on meaningless reply
        self.flags = {}  # Custom flags for stage transitions

    def load_stage_config(self):
        """
        Load stage definitions from the configuration file
        """
        try:
            self.stage_cfg = json.loads(Path(CFG_PATH).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading stage definitions: {e}")
            # Fallback to default configuration
            self.stage_cfg = {
                "APP": {
                    "name": "Acquaintance Path",
                    "entry": {"trigger": "initial_contact"},
                    "maintain": {"max_silence_hours": 72, "polite_required": True},
                    "exit": {"trust": 60, "open": 40, "consecutive_meaningful": 3},
                    "next_stage": "FPP"
                },
                "FPP": {
                    "name": "Friendship Path",
                    "entry": {"prev_stage": "APP"},
                    "maintain": {"photo_exchange": True, "emotion_reflection": True},
                    "exit": {"trust": 75, "open": 60, "answered_fears": True},
                    "next_stage": "RPP"
                },
                "RPP": {
                    "name": "Relationship Path",
                    "entry": {"prev_stage": "FPP"},
                    "maintain": {"romantic_cues": 3, "future_vision": True},
                    "exit": {"commitment": True, "retraction": True},
                    "next_stage": "COMPLETED"
                }
            }

    # ----------  helpers  ----------
    def _hours_since_last(self, ts: dt.datetime) -> float:
        """
        Calculate hours since last Diego message
        
        Args:
            ts: Current timestamp
            
        Returns:
            Hours since last Diego message, or 0.0 if no previous message
        """
        if self.last_diego_ts is None:
            return 0.0
        return (ts - self.last_diego_ts).total_seconds() / 3600.0

    def _meaningful(self, txt: str) -> bool:
        """
        Check if a message is meaningful (more than 4 words)
        
        Args:
            txt: Message text
            
        Returns:
            True if message is meaningful, False otherwise
        """
        return len(txt.split()) > 4  # tweak as needed

    # ----------  public API  ----------
    def record_diego(self, text: str, ts: dt.datetime):
        """
        Record a message from Diego
        
        Args:
            text: Message text
            ts: Message timestamp
        """
        self.last_diego_msg, self.last_diego_ts = text, ts

    def record_cl(self, text: str, ts: dt.datetime) -> Dict[str, Any]:
        """
        Record a message from the client and update scores and stage
        
        Args:
            text: Message text
            ts: Message timestamp
            
        Returns:
            Dictionary with session state including stage and scores
        """
        latency = self._hours_since_last(ts)
        agg = score_interaction(
            cl_msg=text,
            diego_prev=self.last_diego_msg,
            latency_hours=latency,
            history=self.history
        )

        # update consecutive meaningful counter
        if self._meaningful(text):
            self.consecutive_meaningful += 1
        else:
            self.consecutive_meaningful = 0

        # Check for stage transition
        self._maybe_advance_stage(agg, text)

        # return full context to upstream code
        return {
            "session_id": self.session_id,
            "stage": self.current_stage,
            "scores": agg,
            "consecutive_meaningful": self.consecutive_meaningful,
            "flags": self.flags
        }

    def set_flag(self, flag_name: str, value: Any):
        """
        Set a custom flag for stage transitions
        
        Args:
            flag_name: Name of the flag
            value: Value to set
        """
        self.flags[flag_name] = value

    # ----------  private  ----------
    def _rule_passed(self, rule_key: str, rule_val: Any, context: Dict[str, Any]) -> bool:
        """
        Check if a rule is passed based on the context
        
        Args:
            rule_key: Rule key from stage definition
            rule_val: Expected value for the rule
            context: Current context with scores and message
            
        Returns:
            True if rule is passed, False otherwise
        """
        if rule_key in ("trust", "open"):
            return context["scores"][rule_key] >= rule_val
        if rule_key == "consecutive_meaningful":
            return self.consecutive_meaningful >= rule_val
        if rule_key == "answered_fears":
            return "fear" in context.get("cl_text", "").lower()
        if rule_key == "photo_exchange":
            return self.flags.get("photo_exchange", False)
        if rule_key == "emotion_reflection":
            return self.flags.get("emotion_reflection", False)
        if rule_key == "romantic_cues":
            return self.flags.get("romantic_cues_count", 0) >= rule_val
        if rule_key == "future_vision":
            return self.flags.get("future_vision", False)
        if rule_key == "commitment":
            return self.flags.get("commitment", False)
        if rule_key == "retraction":
            return self.flags.get("retraction", False)
        # Default to False for unknown rules
        return False

    def _maybe_advance_stage(self, context_scores: Dict[str, float], cl_text: str):
        """
        Check if stage should advance based on exit conditions
        
        Args:
            context_scores: Current scores
            cl_text: Client message text
        """
        # Skip if we're already at the final stage
        if self.current_stage == "COMPLETED":
            return
            
        # Get exit conditions for current stage
        cfg = self.stage_cfg[self.current_stage]["exit"]
        ctx = {"scores": context_scores, "cl_text": cl_text}

        # Check if all exit conditions are met
        if all(self._rule_passed(k, v, ctx) for k, v in cfg.items()):
            next_stage = self.stage_cfg[self.current_stage]["next_stage"]
            print(f"[MirrorCore] Transition {self.current_stage} → {next_stage}")
            self.current_stage = next_stage
            # Reset counters where appropriate
            self.consecutive_meaningful = 0
            # Don't reset history to maintain score continuity