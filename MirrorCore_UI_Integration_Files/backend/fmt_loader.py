import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

# Path to FMT directories
FMT_BASE_DIR = Path(__file__).resolve().parent.parent / "formats"


class FmtLoader:
    """
    Loader for Format Message Templates (FMTs).
    Handles loading, selecting, and providing templates based on stage and context.
    """

    def __init__(self):
        """
        Initialize the FMT loader and load all available templates
        """
        self.fmt_base_dir = FMT_BASE_DIR
        self.fmt_base_dir.mkdir(exist_ok=True, parents=True)
        
        # Ensure stage directories exist
        for stage in ["APP", "FPP", "RPP"]:
            stage_dir = self.fmt_base_dir / stage
            stage_dir.mkdir(exist_ok=True, parents=True)
        
        # Load all templates
        self.templates = self._load_all_templates()
        
    def _load_all_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all templates from all stage directories
        
        Returns:
            Dictionary mapping stage to list of templates
        """
        templates = {"APP": [], "FPP": [], "RPP": []}
        
        for stage in templates.keys():
            stage_dir = self.fmt_base_dir / stage
            
            # Try to load registry first
            registry_file = stage_dir / "registry.json"
            if registry_file.exists():
                try:
                    registry = json.loads(registry_file.read_text())
                    if isinstance(registry, list):
                        templates[stage] = registry
                        continue
                except json.JSONDecodeError:
                    pass
            
            # Fall back to loading individual files
            for fmt_file in stage_dir.glob("*.json"):
                if fmt_file.name == "registry.json":
                    continue
                    
                try:
                    fmt = json.loads(fmt_file.read_text())
                    if isinstance(fmt, dict) and "fmt_id" in fmt:
                        templates[stage].append(fmt)
                except json.JSONDecodeError:
                    continue
        
        # If no templates found, create sample templates
        if not any(templates.values()):
            self._create_sample_templates()
            return self._load_all_templates()
            
        return templates
    
    def _create_sample_templates(self):
        """
        Create sample templates for each stage
        """
        # APP templates
        app_dir = self.fmt_base_dir / "APP"
        app_templates = [
            {
                "fmt_id": "APP-001",
                "fmt_name": "Icebreaker",
                "stage": "APP",
                "trigger": "initial_contact",
                "goals": ["establish_rapport", "gather_basic_info"],
                "tone": "friendly_professional",
                "core_message": "Hi there! I'm Diego, your relationship coach. I'm here to help you navigate your relationship journey. What brings you here today?",
                "variations": [
                    "Hello! I'm Diego, a relationship coach. I'm excited to work with you on your relationship goals. What's on your mind?",
                    "Welcome! My name is Diego and I specialize in relationship coaching. I'd love to hear what brought you here today."
                ],
                "attachment": None,
                "ai_behaviors": ["active_listening", "open_questions"]
            },
            {
                "fmt_id": "APP-002",
                "fmt_name": "Trust Building",
                "stage": "APP",
                "trigger": "low_trust",
                "goals": ["build_trust", "demonstrate_expertise"],
                "tone": "warm_reassuring",
                "core_message": "I understand that opening up about relationships can be challenging. Everything we discuss is confidential, and I'm here to support you without judgment. What would help you feel more comfortable?",
                "variations": [
                    "It takes courage to talk about relationship matters. I want you to know that this is a safe space, and I'm here to listen and help however I can.",
                    "Many people find it difficult to discuss relationship concerns at first. That's completely normal. We can take things at your pace, and focus on what matters most to you."
                ],
                "attachment": None,
                "ai_behaviors": ["empathetic_responses", "validation"]
            }
        ]
        
        # FPP templates
        fpp_dir = self.fmt_base_dir / "FPP"
        fpp_templates = [
            {
                "fmt_id": "FPP-001",
                "fmt_name": "Deeper Connection",
                "stage": "FPP",
                "trigger": "stage_entry",
                "goals": ["deepen_connection", "explore_values"],
                "tone": "warm_personal",
                "core_message": "I've really enjoyed getting to know you better. I'd love to understand more about what you value most in relationships. What qualities do you think are essential for a strong connection?",
                "variations": [
                    "Our conversations have been really meaningful. I'm curious - what do you believe makes relationships thrive in the long term?",
                    "As we've been talking, I've appreciated your perspective. What relationship values are non-negotiable for you?"
                ],
                "attachment": None,
                "ai_behaviors": ["reflective_listening", "value_exploration"]
            }
        ]
        
        # RPP templates
        rpp_dir = self.fmt_base_dir / "RPP"
        rpp_templates = [
            {
                "fmt_id": "RPP-001",
                "fmt_name": "Intimacy Building",
                "stage": "RPP",
                "trigger": "stage_entry",
                "goals": ["foster_intimacy", "explore_future"],
                "tone": "intimate_supportive",
                "core_message": "I feel we've developed a special connection. I'd love to hear about your dreams for the future - both personally and in relationships. What does your ideal future look like?",
                "variations": [
                    "The trust we've built means a lot to me. I'm curious about your vision for your ideal relationship and life. Would you share that with me?",
                    "Our connection has grown so much. I'd love to know more about your hopes and dreams for the future. What are you yearning for?"
                ],
                "attachment": None,
                "ai_behaviors": ["deep_listening", "future_visioning"]
            }
        ]
        
        # Save sample templates
        for stage, templates in [
            ("APP", app_templates),
            ("FPP", fpp_templates),
            ("RPP", rpp_templates)
        ]:
            stage_dir = self.fmt_base_dir / stage
            
            # Save individual templates
            for template in templates:
                template_file = stage_dir / f"{template['fmt_id']}_{template['fmt_name'].lower().replace(' ', '_')}.json"
                template_file.write_text(json.dumps(template, indent=2))
            
            # Save registry
            registry_file = stage_dir / "registry.json"
            registry_file.write_text(json.dumps(templates, indent=2))
    
    def get_fmt(self, stage: str, trigger: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a format template for the given stage and trigger
        
        Args:
            stage: Current stage (APP, FPP, RPP)
            trigger: Optional trigger to filter templates
            
        Returns:
            Selected template or default template if none found
        """
        if stage not in self.templates or not self.templates[stage]:
            # Fallback to APP if no templates for the requested stage
            stage = "APP"
            
        templates = self.templates[stage]
        
        if trigger:
            # Filter templates by trigger
            matching = [t for t in templates if t.get("trigger") == trigger]
            if matching:
                return random.choice(matching)
        
        # Return random template for the stage if no trigger match
        return random.choice(templates) if templates else self._get_default_template(stage)
    
    def _get_default_template(self, stage: str) -> Dict[str, Any]:
        """
        Get a default template for the given stage
        
        Args:
            stage: Current stage
            
        Returns:
            Default template
        """
        return {
            "fmt_id": f"{stage}-DEFAULT",
            "fmt_name": "Default Template",
            "stage": stage,
            "trigger": "default",
            "goals": ["maintain_connection"],
            "tone": "friendly_supportive",
            "core_message": "I'm here to support you on your relationship journey. What's on your mind today?",
            "variations": [],
            "attachment": None,
            "ai_behaviors": ["active_listening"]
        }
    
    def get_fmt_variation(self, fmt: Dict[str, Any]) -> str:
        """
        Get a message variation from the template
        
        Args:
            fmt: Format template
            
        Returns:
            Selected message text
        """
        if "variations" in fmt and fmt["variations"] and random.random() < 0.7:
            return random.choice(fmt["variations"])
        return fmt["core_message"]
    
    def reload_templates(self):
        """
        Reload all templates from disk
        """
        self.templates = self._load_all_templates()