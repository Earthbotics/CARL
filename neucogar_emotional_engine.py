#!/usr/bin/env python3
"""
NEUCOGAR Emotional Engine
=========================

This module implements the NEUCOGAR emotional engine inside CARL based on the 
Lövheim Cube of Emotion (Lövheim, 2012), which maps emotional states using 
three key neurotransmitters:

- **Dopamine (DA)** — reward/motivation
- **Serotonin (5-HT)** — mood/stability/confidence  
- **Noradrenaline (NE)** — arousal/alertness

The system represents a 3D cube space with each axis ranging from -1.0 to +1.0,
mapping core emotions and sub-emotions to specific coordinates based on the 
relative dominance of these neurotransmitters.

Extended to include all 8 major neurotransmitters with realistic baseline levels:
- **GABA** — inhibition/calmness
- **Glutamate** — excitation/learning
- **Acetylcholine** — attention/memory
- **Oxytocin** — social bonding/trust
- **Endorphins** — pain relief/euphoria
"""

import json
import math
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

@dataclass
class NeuroCoordinates:
    """Represents neurotransmitter levels in 3D space."""
    dopamine: float      # DA: reward/motivation (-1.0 to +1.0)
    serotonin: float     # 5-HT: mood/stability/confidence (-1.0 to +1.0)
    noradrenaline: float # NE: arousal/alertness (-1.0 to +1.0)
    
    def __post_init__(self):
        """Clamp values to valid range."""
        self.dopamine = max(-1.0, min(1.0, self.dopamine))
        self.serotonin = max(-1.0, min(1.0, self.serotonin))
        self.noradrenaline = max(-1.0, min(1.0, self.noradrenaline))
    
    def distance_to(self, other: 'NeuroCoordinates') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return math.sqrt(
            (self.dopamine - other.dopamine) ** 2 +
            (self.serotonin - other.serotonin) ** 2 +
            (self.noradrenaline - other.noradrenaline) ** 2
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            "dopamine": self.dopamine,
            "serotonin": self.serotonin,
            "noradrenaline": self.noradrenaline
        }

@dataclass
class AffectSnapshot:
    """Snapshot of emotional state for STM entries."""
    primary_emotion: str
    sub_emotion: str
    neuro_coordinates: NeuroCoordinates
    extended_neurotransmitters: 'ExtendedNeurotransmitters'
    intensity: float
    triggers: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "primary_emotion": self.primary_emotion,
            "sub_emotion": self.sub_emotion,
            "neuro_coordinates": self.neuro_coordinates.to_dict(),
            "extended_neurotransmitters": self.extended_neurotransmitters.to_dict(),
            "intensity": self.intensity,
            "triggers": self.triggers,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ExtendedNeurotransmitters:
    """Represents all 8 major neurotransmitters with realistic baseline levels."""
    dopamine: float = 0.3      # DA: reward/motivation (0.0-1.0, baseline 0.3)
    serotonin: float = 0.4     # 5-HT: mood/stability/confidence (0.0-1.0, baseline 0.4)
    norepinephrine: float = 0.2 # NE: arousal/alertness (0.0-1.0, baseline 0.2)
    gaba: float = 0.35         # GABA: inhibition/calmness (0.0-1.0, baseline 0.35)
    glutamate: float = 0.45    # Glutamate: excitation/learning (0.0-1.0, baseline 0.45)
    acetylcholine: float = 0.3  # ACh: attention/memory (0.0-1.0, baseline 0.3)
    oxytocin: float = 0.25     # Oxytocin: social bonding/trust (0.0-1.0, baseline 0.25)
    endorphins: float = 0.2    # Endorphins: pain relief/euphoria (0.0-1.0, baseline 0.2)
    
    def __post_init__(self):
        """Clamp all values to valid range."""
        self.dopamine = max(0.0, min(1.0, self.dopamine))
        self.serotonin = max(0.0, min(1.0, self.serotonin))
        self.norepinephrine = max(0.0, min(1.0, self.norepinephrine))
        self.gaba = max(0.0, min(1.0, self.gaba))
        self.glutamate = max(0.0, min(1.0, self.glutamate))
        self.acetylcholine = max(0.0, min(1.0, self.acetylcholine))
        self.oxytocin = max(0.0, min(1.0, self.oxytocin))
        self.endorphins = max(0.0, min(1.0, self.endorphins))
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            "dopamine": self.dopamine,
            "serotonin": self.serotonin,
            "norepinephrine": self.norepinephrine,
            "gaba": self.gaba,
            "glutamate": self.glutamate,
            "acetylcholine": self.acetylcholine,
            "oxytocin": self.oxytocin,
            "endorphins": self.endorphins
        }
    
    def apply_homeostasis(self, decay_rate: float = 0.02):
        """Apply realistic homeostasis to return to baseline levels."""
        baselines = {
            "dopamine": 0.3,
            "serotonin": 0.4,
            "norepinephrine": 0.2,
            "gaba": 0.35,
            "glutamate": 0.45,
            "acetylcholine": 0.3,
            "oxytocin": 0.25,
            "endorphins": 0.2
        }
        
        for nt_name, baseline in baselines.items():
            current = getattr(self, nt_name)
            if current > baseline:
                setattr(self, nt_name, max(baseline, current - decay_rate))
            elif current < baseline:
                setattr(self, nt_name, min(baseline, current + decay_rate * 0.5))  # Slower recovery
    
    def get_neucogar_coordinates(self) -> NeuroCoordinates:
        """Convert to NEUCOGAR 3D coordinates (-1.0 to +1.0 range)."""
        return NeuroCoordinates(
            dopamine=(self.dopamine - 0.5) * 2.0,
            serotonin=(self.serotonin - 0.5) * 2.0,
            noradrenaline=(self.norepinephrine - 0.5) * 2.0
        )

@dataclass
class EmotionalState:
    """Represents a complete emotional state."""
    primary: str
    sub_emotion: str
    detail: str
    neuro_coordinates: NeuroCoordinates
    extended_neurotransmitters: ExtendedNeurotransmitters
    intensity: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return {
            "primary": self.primary,
            "sub_emotion": self.sub_emotion,
            "detail": self.detail,
            "neuro_coordinates": self.neuro_coordinates.to_dict(),
            "extended_neurotransmitters": self.extended_neurotransmitters.to_dict(),
            "intensity": self.intensity,
            "timestamp": self.timestamp.isoformat()
        }

class NEUCOGAREmotionalEngine:
    """
    NEUCOGAR Emotional Engine implementing the Lövheim Cube of Emotion.
    
    Maps emotional states to 3D neurotransmitter space and provides
    dynamic emotional state management with session logging.
    Extended to include all 8 major neurotransmitters with realistic baseline levels.
    """
    
    def __init__(self):
        """Initialize the NEUCOGAR emotional engine."""
        self.logger = logging.getLogger(__name__)
        
        # Current emotional state with extended neurotransmitters
        self.current_state = self._initialize_neutral_state()
        
        # Session logging
        self.session_log: List[EmotionalState] = []
        self.session_start_time = datetime.now()
        
        # Core emotions mapping to neurotransmitter coordinates
        self.core_emotions = self._initialize_core_emotions()
        
        # Sub-emotions with depth mapping (surface vs deep processing)
        self.sub_emotions = self._initialize_sub_emotions()
        
        # Initialize session with baseline emotional data
        self._initialize_session_data()
        
        # Emotional triggers and their effects
        self.emotional_triggers = self._initialize_emotional_triggers()
        
        # Extended neurotransmitter effects
        self.extended_neuro_effects = self._initialize_extended_neuro_effects()
    
    def _initialize_session_data(self):
        """Initialize session with baseline emotional data to ensure we have data for reports."""
        # Add initial neutral state
        self._log_emotional_transition(self.current_state)
        
        # Add a few baseline emotional states to ensure we have data
        baseline_states = [
            ("neutral", "calm", 0.3),
            ("joy", "content", 0.4),
            ("neutral", "focused", 0.5)
        ]
        
        for primary, sub_emotion, intensity in baseline_states:
            # Create a baseline state with realistic neurotransmitter levels
            coords = NeuroCoordinates(0.1, 0.2, 0.1)  # Slight positive baseline
            extended_nt = ExtendedNeurotransmitters()  # Use realistic baselines
            state = EmotionalState(
                primary=primary,
                sub_emotion=sub_emotion,
                detail=f"Baseline {primary} state",
                neuro_coordinates=coords,
                extended_neurotransmitters=extended_nt,
                intensity=intensity,
                timestamp=datetime.now()
            )
            self.session_log.append(state)
    
    def _initialize_neutral_state(self) -> EmotionalState:
        """Initialize with a neutral emotional state and realistic neurotransmitter levels."""
        return EmotionalState(
            primary="neutral",
            sub_emotion="calm",
            detail="balanced",
            neuro_coordinates=NeuroCoordinates(0.0, 0.0, 0.0),
            extended_neurotransmitters=ExtendedNeurotransmitters(),
            intensity=0.0,
            timestamp=datetime.now()
        )
    
    def _initialize_core_emotions(self) -> Dict[str, NeuroCoordinates]:
        """
        Initialize core emotions mapped to Lövheim Cube coordinates.
        
        Based on Lövheim (2012) research on neurotransmitter dominance:
        - Anger: High NE, High DA, Low 5-HT
        - Sadness: Low DA, High 5-HT, Low NE  
        - Fear: Low DA, Low 5-HT, High NE
        - Joy/Happiness: High DA, High 5-HT, Moderate NE
        - Surprise: High NE, Moderate DA/5-HT
        - Disgust: Low DA, High 5-HT, High NE
        """
        return {
            "anger": NeuroCoordinates(0.8, -0.6, 0.9),      # High DA, Low 5-HT, High NE
            "sadness": NeuroCoordinates(-0.7, 0.8, -0.5),    # Low DA, High 5-HT, Low NE
            "fear": NeuroCoordinates(-0.6, -0.7, 0.8),       # Low DA, Low 5-HT, High NE
            "joy": NeuroCoordinates(0.9, 0.8, 0.3),          # High DA, High 5-HT, Moderate NE
            "surprise": NeuroCoordinates(0.4, 0.3, 0.9),     # Moderate DA/5-HT, High NE
            "disgust": NeuroCoordinates(-0.5, 0.7, 0.6),     # Low DA, High 5-HT, High NE
            "neutral": NeuroCoordinates(0.0, 0.0, 0.0),      # Balanced state
            "excitement": NeuroCoordinates(0.8, 0.4, 0.7),   # High DA, Moderate 5-HT, High NE
            "anxiety": NeuroCoordinates(-0.3, -0.5, 0.6),    # Low DA, Low 5-HT, Moderate NE
            "contentment": NeuroCoordinates(0.6, 0.8, -0.2), # High DA, High 5-HT, Low NE
            "frustration": NeuroCoordinates(0.3, -0.4, 0.7), # Moderate DA, Low 5-HT, High NE
            "gratitude": NeuroCoordinates(0.7, 0.9, 0.2),    # High DA, High 5-HT, Low NE
            "curiosity": NeuroCoordinates(0.5, 0.3, 0.4),    # Moderate DA, Moderate 5-HT, Moderate NE
            "amusement": NeuroCoordinates(0.8, 0.5, 0.4),    # High DA, Moderate 5-HT, Moderate NE
            "wonder": NeuroCoordinates(0.4, 0.6, 0.5),       # Moderate DA, High 5-HT, Moderate NE
            "determination": NeuroCoordinates(0.7, 0.4, 0.6), # High DA, Moderate 5-HT, High NE
            "relaxation": NeuroCoordinates(0.3, 0.7, -0.3),  # Moderate DA, High 5-HT, Low NE
            "confusion": NeuroCoordinates(-0.2, -0.3, 0.4),  # Low DA, Low 5-HT, Moderate NE
            "satisfaction": NeuroCoordinates(0.6, 0.8, 0.1), # High DA, High 5-HT, Low NE
            "anticipation": NeuroCoordinates(0.7, 0.3, 0.5)  # High DA, Low 5-HT, Moderate NE
        }
    
    def _initialize_sub_emotions(self) -> Dict[str, Dict[str, Tuple[str, float]]]:
        """
        Initialize sub-emotions with depth mapping.
        
        Each sub-emotion maps to (parent_emotion, depth_factor) where:
        - depth_factor: 0.0 = surface level (corner), 1.0 = deep/internal (center)
        - Closer to amygdala (more unconscious) as depth increases
        """
        return {
            # Anger sub-emotions
            "frustrated": ("anger", 0.3),      # Surface level
            "irritated": ("anger", 0.4),       # Surface level
            "annoyed": ("anger", 0.2),         # Surface level
            "enraged": ("anger", 0.9),         # Deep/internal
            "furious": ("anger", 0.8),         # Deep/internal
            "livid": ("anger", 0.95),          # Deep/internal
            
            # Sadness sub-emotions
            "melancholy": ("sadness", 0.7),    # Deep/internal
            "depressed": ("sadness", 0.9),     # Deep/internal
            "gloomy": ("sadness", 0.4),        # Surface level
            "sorrowful": ("sadness", 0.6),     # Moderate depth
            "heartbroken": ("sadness", 0.95),  # Deep/internal
            "disappointed": ("sadness", 0.3),  # Surface level
            
            # Fear sub-emotions
            "anxious": ("fear", 0.5),          # Moderate depth
            "terrified": ("fear", 0.9),        # Deep/internal
            "worried": ("fear", 0.3),          # Surface level
            "panicked": ("fear", 0.8),         # Deep/internal
            "nervous": ("fear", 0.4),          # Surface level
            "scared": ("fear", 0.6),           # Moderate depth
            
            # Joy sub-emotions (aligned with main system: happiness/joyful -> [ecstatic, delighted])
            "ecstatic": ("joy", 0.9),          # Deep/internal - valid sub-emotion for joyful
            "delighted": ("joy", 0.5),         # Moderate depth - valid sub-emotion for joyful
            # Note: "thrilled", "elated", "pleased", "happy" removed to align with main system mapping
            
            # Surprise sub-emotions
            "shocked": ("surprise", 0.8),      # Deep/internal
            "amazed": ("surprise", 0.6),       # Moderate depth
            "astonished": ("surprise", 0.7),   # Moderate depth
            "startled": ("surprise", 0.4),     # Surface level
            "bewildered": ("surprise", 0.5),   # Moderate depth
            "stunned": ("surprise", 0.9),      # Deep/internal
            
            # Disgust sub-emotions
            "repulsed": ("disgust", 0.7),      # Moderate depth
            "revolted": ("disgust", 0.8),      # Deep/internal
            "appalled": ("disgust", 0.6),      # Moderate depth
            "nauseated": ("disgust", 0.9),     # Deep/internal
            "offended": ("disgust", 0.3),      # Surface level
            "disturbed": ("disgust", 0.5),     # Moderate depth
            
            # Neutral sub-emotions
            "calm": ("neutral", 0.3),          # Surface level
            "balanced": ("neutral", 0.5),      # Moderate depth
            "centered": ("neutral", 0.7),      # Moderate depth
            "peaceful": ("neutral", 0.6),      # Moderate depth
            "serene": ("neutral", 0.8),        # Deep/internal
            "tranquil": ("neutral", 0.4),      # Surface level
        }
    
    def _initialize_emotional_triggers(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize emotional triggers and their neurotransmitter effects.
        
        Each trigger maps to neurotransmitter adjustments:
        {dopamine_change, serotonin_change, noradrenaline_change}
        """
        return {
            # Positive triggers
            "praise": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "success": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "laughter": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "music": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.1},
            "dance": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.2},
            "exercise": {"dopamine": 0.2, "serotonin": 0.3, "noradrenaline": 0.3},
            "learning": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.2},
            "creativity": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "connection": {"dopamine": 0.2, "serotonin": 0.3, "noradrenaline": 0.1},
            "achievement": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            
            # Toy and play triggers (enhanced for Chomp and favorite toys)
            "toy": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "chomp": {"dopamine": 0.6, "serotonin": 0.4, "noradrenaline": 0.3},  # Enhanced for favorite toy
            "play": {"dopamine": 0.5, "serotonin": 0.3, "noradrenaline": 0.2},
            "favorite": {"dopamine": 0.5, "serotonin": 0.4, "noradrenaline": 0.2},
            "amusement": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "joy": {"dopamine": 0.5, "serotonin": 0.4, "noradrenaline": 0.2},
            
            # Negative triggers
            "criticism": {"dopamine": -0.2, "serotonin": -0.3, "noradrenaline": 0.2},
            "failure": {"dopamine": -0.3, "serotonin": -0.4, "noradrenaline": 0.1},
            "rejection": {"dopamine": -0.3, "serotonin": -0.4, "noradrenaline": 0.2},
            "conflict": {"dopamine": -0.2, "serotonin": -0.3, "noradrenaline": 0.4},
            "stress": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3},
            "loneliness": {"dopamine": -0.2, "serotonin": -0.3, "noradrenaline": -0.1},
            "boredom": {"dopamine": -0.2, "serotonin": -0.1, "noradrenaline": -0.2},
            "uncertainty": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.2},
            "overwhelm": {"dopamine": -0.2, "serotonin": -0.3, "noradrenaline": 0.4},
            "disappointment": {"dopamine": -0.3, "serotonin": -0.2, "noradrenaline": 0.1},
            
            # Neutral/contextual triggers
            "surprise": {"dopamine": 0.1, "serotonin": 0.0, "noradrenaline": 0.3},
            "change": {"dopamine": 0.1, "serotonin": -0.1, "noradrenaline": 0.2},
            "challenge": {"dopamine": 0.2, "serotonin": -0.1, "noradrenaline": 0.3},
            "discovery": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.2},
            "reflection": {"dopamine": 0.0, "serotonin": 0.1, "noradrenaline": -0.1},
            "rest": {"dopamine": 0.1, "serotonin": 0.2, "noradrenaline": -0.2},
            
            # Self-awareness and self-recognition triggers
            "me": {"dopamine": 0.3, "serotonin": 0.4, "noradrenaline": 0.2},  # Self-recognition: curiosity + confidence
            "self_recognition": {"dopamine": 0.3, "serotonin": 0.4, "noradrenaline": 0.2},  # Explicit self-recognition
            "mirror_test": {"dopamine": 0.4, "serotonin": 0.5, "noradrenaline": 0.3},  # Mirror test success
            "self_awareness": {"dopamine": 0.2, "serotonin": 0.3, "noradrenaline": 0.1},  # General self-awareness
            "identity_confirmation": {"dopamine": 0.3, "serotonin": 0.4, "noradrenaline": 0.2},  # Identity confirmation
            
            # Role-playing emotional triggers (for verbal requests)
            "act_amazed": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.4},
            "act_surprised": {"dopamine": 0.1, "serotonin": 0.0, "noradrenaline": 0.3},
            "act_amused": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "act_joyful": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "act_ecstatic": {"dopamine": 0.5, "serotonin": 0.4, "noradrenaline": 0.3},
            "act_terrified": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.5},
            "act_scared": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "act_irritated": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3},
            "act_angry": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "act_sad": {"dopamine": -0.2, "serotonin": 0.1, "noradrenaline": -0.1},
            
            # Role-playing action triggers
            "pretend_amazed": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.4},
            "pretend_surprised": {"dopamine": 0.1, "serotonin": 0.0, "noradrenaline": 0.3},
            "pretend_amused": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "pretend_joyful": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "pretend_ecstatic": {"dopamine": 0.5, "serotonin": 0.4, "noradrenaline": 0.3},
            "pretend_terrified": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.5},
            "pretend_scared": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "pretend_irritated": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3},
            "pretend_angry": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "pretend_sad": {"dopamine": -0.2, "serotonin": 0.1, "noradrenaline": -0.1},
            
            # Show/demonstrate triggers
            "show_amazed": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.4},
            "show_surprised": {"dopamine": 0.1, "serotonin": 0.0, "noradrenaline": 0.3},
            "show_amused": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
            "show_joyful": {"dopamine": 0.4, "serotonin": 0.3, "noradrenaline": 0.2},
            "show_ecstatic": {"dopamine": 0.5, "serotonin": 0.4, "noradrenaline": 0.3},
            "show_terrified": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.5},
            "show_scared": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "show_irritated": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3},
            "show_angry": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.4},
            "show_sad": {"dopamine": -0.2, "serotonin": 0.1, "noradrenaline": -0.1},
        }
    
    def _initialize_body_movement_scripts(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize body movement scripts that automatically execute based on NUECOGAR levels.
        
        Each script maps to specific emotions and sub-emotions with execution conditions.
        """
        return {
            # Eye expressions (RGB Animator commands)
            "eyes_joy": {
                "type": "eye_expression",
                "command": "eyes_joy",
                "triggers": ["reaction_amused"],
                "emotions": ["joy", "happiness", "ecstatic", "delighted"],
                "intensity_threshold": 0.4,
                "description": "Joyful eye expression for positive emotions"
            },
            "eyes_surprise": {
                "type": "eye_expression", 
                "command": "eyes_surprise",
                "triggers": ["reaction_amazed", "reaction_ecstatic"],
                "emotions": ["surprise", "amazed", "astonished", "startled", "bewildered", "stunned"],
                "intensity_threshold": 0.3,
                "description": "Surprised eye expression for amazement and shock"
            },
            "eyes_sad": {
                "type": "eye_expression",
                "command": "eyes_sad", 
                "triggers": ["reaction_terrified", "reaction_irritated"],
                "emotions": ["sadness", "melancholy", "depressed", "gloomy", "sorrowful", "heartbroken", "disappointed"],
                "intensity_threshold": 0.3,
                "description": "Sad eye expression for negative emotions"
            },
            
            # Body movement reactions
            "reaction_amazed": {
                "type": "body_movement",
                "command": "reaction_amazed",
                "triggers": ["surprise", "amazed", "astonished"],
                "emotions": ["surprise", "amazed", "astonished", "bewildered"],
                "intensity_threshold": 0.5,
                "description": "Amazed body reaction for surprise and wonder",
                "coordination": {
                    "eyes": "eyes_surprise",
                    "timing": "simultaneous"
                }
            },
            "reaction_terrified": {
                "type": "body_movement",
                "command": "reaction_terrified",
                "triggers": ["fear", "terrified", "panicked", "scared"],
                "emotions": ["fear", "terrified", "panicked", "scared", "anxious", "worried", "nervous"],
                "intensity_threshold": 0.6,
                "description": "Terrified body reaction for fear and anxiety",
                "coordination": {
                    "eyes": "eyes_sad",
                    "timing": "simultaneous"
                }
            },
            "reaction_ecstatic": {
                "type": "body_movement",
                "command": "reaction_ecstatic",
                "triggers": ["joy", "ecstatic", "delighted"],
                "emotions": ["joy", "ecstatic", "delighted"],
                "intensity_threshold": 0.7,
                "description": "Ecstatic body reaction for extreme joy",
                "coordination": {
                    "eyes": "eyes_surprise",
                    "timing": "simultaneous"
                }
            },
            "reaction_amused": {
                "type": "body_movement",
                "command": "reaction_amused",
                "triggers": ["joy", "amusement", "pleased", "happy"],
                "emotions": ["joy", "amusement", "pleased", "happy", "delighted"],
                "intensity_threshold": 0.4,
                "description": "Amused body reaction for light joy and amusement",
                "coordination": {
                    "eyes": "eyes_joy",
                    "timing": "simultaneous"
                }
            },
            "reaction_irritated": {
                "type": "body_movement",
                "command": "reaction_irritated",
                "triggers": ["anger", "irritated", "annoyed", "frustrated"],
                "emotions": ["anger", "irritated", "annoyed", "frustrated", "enraged", "furious", "livid"],
                "intensity_threshold": 0.4,
                "description": "Irritated body reaction for anger and frustration",
                "coordination": {
                    "eyes": "eyes_sad",
                    "timing": "simultaneous"
                }
            }
        }
    
    def get_body_movement_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Get the body movement scripts configuration."""
        if not hasattr(self, '_body_movement_scripts'):
            self._body_movement_scripts = self._initialize_body_movement_scripts()
        return self._body_movement_scripts
    
    def should_execute_body_movement(self, emotion: str, intensity: float) -> Optional[Dict[str, Any]]:
        """
        Determine if a body movement script should be executed based on current emotion and intensity.
        
        Args:
            emotion: Current primary emotion
            intensity: Emotional intensity (0.0 to 1.0)
            
        Returns:
            Script configuration if should execute, None otherwise
        """
        scripts = self.get_body_movement_scripts()
        
        for script_name, script_config in scripts.items():
            # Check if emotion matches
            if emotion in script_config.get("emotions", []):
                # Check if intensity meets threshold
                if intensity >= script_config.get("intensity_threshold", 0.0):
                    return {
                        "script_name": script_name,
                        "script_config": script_config,
                        "emotion": emotion,
                        "intensity": intensity
                    }
        
        return None
    
    def get_coordinated_movements(self, emotion: str, intensity: float) -> List[Dict[str, Any]]:
        """
        Get coordinated eye and body movements for the current emotional state.
        
        Args:
            emotion: Current primary emotion
            intensity: Emotional intensity (0.0 to 1.0)
            
        Returns:
            List of movement configurations to execute
        """
        movements = []
        scripts = self.get_body_movement_scripts()
        
        for script_name, script_config in scripts.items():
            if emotion in script_config.get("emotions", []):
                if intensity >= script_config.get("intensity_threshold", 0.0):
                    # Add the main movement
                    movements.append({
                        "type": script_config["type"],
                        "command": script_config["command"],
                        "script_name": script_name,
                        "description": script_config["description"]
                    })
                    
                    # Add coordinated eye movement if specified
                    coordination = script_config.get("coordination", {})
                    if coordination.get("eyes"):
                        eye_script = scripts.get(coordination["eyes"])
                        if eye_script:
                            movements.append({
                                "type": "eye_expression",
                                "command": eye_script["command"],
                                "script_name": coordination["eyes"],
                                "description": f"Coordinated {eye_script['description']}",
                                "timing": coordination.get("timing", "simultaneous")
                            })
        
        return movements
    
    def _initialize_extended_neuro_effects(self) -> Dict[str, Dict[str, float]]:
        """Initialize effects of emotional triggers on extended neurotransmitters."""
        return {
            # Positive triggers
            "praise": {
                "dopamine": 0.3, "serotonin": 0.2, "norepinephrine": 0.1,
                "gaba": 0.1, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.2, "endorphins": 0.1
            },
            "success": {
                "dopamine": 0.4, "serotonin": 0.3, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "laughter": {
                "dopamine": 0.3, "serotonin": 0.2, "norepinephrine": 0.1,
                "gaba": 0.2, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.1, "endorphins": 0.3
            },
            "music": {
                "dopamine": 0.2, "serotonin": 0.1, "norepinephrine": 0.1,
                "gaba": 0.2, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "dance": {
                "dopamine": 0.3, "serotonin": 0.2, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": 0.1, "endorphins": 0.3
            },
            "exercise": {
                "dopamine": 0.2, "serotonin": 0.3, "norepinephrine": 0.3,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": 0.1, "endorphins": 0.4
            },
            "learning": {
                "dopamine": 0.2, "serotonin": 0.1, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.3, "acetylcholine": 0.3,
                "oxytocin": 0.1, "endorphins": 0.1
            },
            "creativity": {
                "dopamine": 0.3, "serotonin": 0.2, "norepinephrine": 0.1,
                "gaba": 0.1, "glutamate": 0.3, "acetylcholine": 0.2,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "connection": {
                "dopamine": 0.2, "serotonin": 0.3, "norepinephrine": 0.1,
                "gaba": 0.1, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.4, "endorphins": 0.2
            },
            "achievement": {
                "dopamine": 0.4, "serotonin": 0.3, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.1, "endorphins": 0.3
            },
            
            # Toy and play triggers (enhanced for Chomp and favorite toys)
            "toy": {
                "dopamine": 0.4, "serotonin": 0.3, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "chomp": {
                "dopamine": 0.6, "serotonin": 0.4, "norepinephrine": 0.3,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.2, "endorphins": 0.3
            },
            "play": {
                "dopamine": 0.5, "serotonin": 0.3, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.2, "endorphins": 0.3
            },
            "favorite": {
                "dopamine": 0.5, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.3, "endorphins": 0.2
            },
            "amusement": {
                "dopamine": 0.4, "serotonin": 0.3, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": 0.1, "endorphins": 0.3
            },
            "joy": {
                "dopamine": 0.5, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": 0.2, "endorphins": 0.3
            },
            
            # Negative triggers
            "criticism": {
                "dopamine": -0.2, "serotonin": -0.3, "norepinephrine": 0.2,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": -0.1,
                "oxytocin": -0.2, "endorphins": -0.1
            },
            "failure": {
                "dopamine": -0.3, "serotonin": -0.4, "norepinephrine": 0.1,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": -0.1,
                "oxytocin": -0.1, "endorphins": -0.2
            },
            "rejection": {
                "dopamine": -0.3, "serotonin": -0.4, "norepinephrine": 0.2,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": -0.1,
                "oxytocin": -0.3, "endorphins": -0.2
            },
            "conflict": {
                "dopamine": -0.2, "serotonin": -0.3, "norepinephrine": 0.4,
                "gaba": -0.2, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": -0.2, "endorphins": -0.1
            },
            "stress": {
                "dopamine": -0.1, "serotonin": -0.2, "norepinephrine": 0.3,
                "gaba": -0.2, "glutamate": 0.2, "acetylcholine": 0.1,
                "oxytocin": -0.1, "endorphins": -0.1
            },
            "loneliness": {
                "dopamine": -0.2, "serotonin": -0.3, "norepinephrine": -0.1,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": -0.1,
                "oxytocin": -0.3, "endorphins": -0.1
            },
            "boredom": {
                "dopamine": -0.2, "serotonin": -0.1, "norepinephrine": -0.2,
                "gaba": 0.1, "glutamate": -0.1, "acetylcholine": -0.2,
                "oxytocin": -0.1, "endorphins": -0.1
            },
            "uncertainty": {
                "dopamine": -0.1, "serotonin": -0.2, "norepinephrine": 0.2,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": -0.1, "endorphins": -0.1
            },
            "overwhelm": {
                "dopamine": -0.2, "serotonin": -0.3, "norepinephrine": 0.4,
                "gaba": -0.3, "glutamate": 0.3, "acetylcholine": 0.2,
                "oxytocin": -0.1, "endorphins": -0.1
            },
            "disappointment": {
                "dopamine": -0.3, "serotonin": -0.2, "norepinephrine": 0.1,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": -0.1,
                "oxytocin": -0.1, "endorphins": -0.2
            },
            
            # Neutral/contextual triggers
            "surprise": {
                "dopamine": 0.1, "serotonin": 0.0, "norepinephrine": 0.3,
                "gaba": -0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.0, "endorphins": 0.0
            },
            "change": {
                "dopamine": 0.1, "serotonin": -0.1, "norepinephrine": 0.2,
                "gaba": -0.1, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.0, "endorphins": 0.0
            },
            "challenge": {
                "dopamine": 0.2, "serotonin": -0.1, "norepinephrine": 0.3,
                "gaba": -0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.0, "endorphins": 0.1
            },
            "discovery": {
                "dopamine": 0.2, "serotonin": 0.1, "norepinephrine": 0.2,
                "gaba": 0.0, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.0, "endorphins": 0.1
            },
            "reflection": {
                "dopamine": 0.0, "serotonin": 0.1, "norepinephrine": -0.1,
                "gaba": 0.1, "glutamate": 0.1, "acetylcholine": 0.1,
                "oxytocin": 0.0, "endorphins": 0.0
            },
            "rest": {
                "dopamine": 0.1, "serotonin": 0.2, "norepinephrine": -0.2,
                "gaba": 0.2, "glutamate": -0.1, "acetylcholine": -0.1,
                "oxytocin": 0.1, "endorphins": 0.1
            },
            
            # Self-awareness and self-recognition triggers (extended neurotransmitters)
            "me": {
                "dopamine": 0.3, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.3,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "self_recognition": {
                "dopamine": 0.3, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.3,
                "oxytocin": 0.1, "endorphins": 0.2
            },
            "mirror_test": {
                "dopamine": 0.4, "serotonin": 0.5, "norepinephrine": 0.3,
                "gaba": 0.1, "glutamate": 0.3, "acetylcholine": 0.4,
                "oxytocin": 0.2, "endorphins": 0.3
            },
            "self_awareness": {
                "dopamine": 0.2, "serotonin": 0.3, "norepinephrine": 0.1,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.2,
                "oxytocin": 0.1, "endorphins": 0.1
            },
            "identity_confirmation": {
                "dopamine": 0.3, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.1, "glutamate": 0.2, "acetylcholine": 0.3,
                "oxytocin": 0.1, "endorphins": 0.2
            },
        }
    
    def get_current_emotion(self) -> Dict[str, Any]:
        """
        Get the current emotional state.
        
        Returns:
            Dictionary with primary emotion, sub-emotion, detail, and neuro coordinates
        """
        return {
            "primary": self.current_state.primary,
            "sub_emotion": self.current_state.sub_emotion,
            "detail": self.current_state.detail,
            "neuro_coordinates": self.current_state.neuro_coordinates.to_dict(),
            "intensity": self.current_state.intensity,
            "timestamp": self.current_state.timestamp.isoformat()
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current NEUCOGAR state in a format compatible with EmoBus publishing.
        
        Returns:
            Dictionary with all neurotransmitter levels and emotional state
        """
        try:
            # Get extended neurotransmitter levels
            extended_nt = self.current_state.extended_neurotransmitters
            
            return {
                "dopamine": extended_nt.dopamine,
                "serotonin": extended_nt.serotonin,
                "norepinephrine": extended_nt.norepinephrine,
                "gaba": extended_nt.gaba,
                "glutamate": extended_nt.glutamate,
                "acetylcholine": extended_nt.acetylcholine,
                "oxytocin": extended_nt.oxytocin,
                "endorphins": extended_nt.endorphins,
                "primary": self.current_state.primary,
                "sub_emotion": self.current_state.sub_emotion,
                "intensity": self.current_state.intensity,
                "timestamp": self.current_state.timestamp.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting current state: {e}")
            # Return safe defaults
            return {
                "dopamine": 0.5,
                "serotonin": 0.5,
                "norepinephrine": 0.5,
                "gaba": 0.5,
                "glutamate": 0.5,
                "acetylcholine": 0.5,
                "oxytocin": 0.5,
                "endorphins": 0.5,
                "primary": "neutral",
                "sub_emotion": "calm",
                "intensity": 0.5,
                "timestamp": datetime.now().isoformat()
            }
    
    def update_emotion_state(self, trigger_input: str) -> Dict[str, Any]:
        """
        Update emotional state based on external trigger input.
        
        Args:
            trigger_input: External input (trigger word or perceptual stimulus)
            
        Returns:
            Updated emotional state dictionary
        """
        # First check if this is a role-playing request
        role_playing_trigger = self.detect_role_playing_request(trigger_input)
        
        if role_playing_trigger:
            # Use the role-playing trigger instead of the original input
            trigger_input = role_playing_trigger
            self.logger.info(f"Detected role-playing request: '{trigger_input}' -> using trigger: '{role_playing_trigger}'")
        
        # Find matching trigger
        trigger_effects = self._find_trigger_effects(trigger_input)
        
        if trigger_effects:
            # Apply neurotransmitter adjustments (both core and extended)
            self._adjust_neurotransmitters(trigger_effects)
            self._adjust_extended_neurotransmitters(trigger_input)
            
            # Resolve new emotional state based on proximity in cube
            new_state = self._resolve_emotional_state()
            
            # Update current state
            self.current_state = new_state
            
            # Log the transition
            self._log_emotional_transition(new_state)
            
            # 🔧 NEW: Trigger body movement reactions based on emotional state change
            self._trigger_automatic_body_reactions(new_state)
            
            self.logger.info(f"Emotional state updated: {trigger_input} -> {new_state.primary}/{new_state.sub_emotion}")
        else:
            # If no trigger effects found, still log the current state to ensure we have data
            self._log_emotional_transition(self.current_state)
            self.logger.info(f"No trigger effects found for: {trigger_input}, keeping current state")
        
        return self.get_current_emotion()
    
    def _find_trigger_effects(self, trigger_input: str) -> Optional[Dict[str, float]]:
        """Find neurotransmitter effects for a given trigger input."""
        trigger_input_lower = trigger_input.lower()
        
        # Direct match
        if trigger_input_lower in self.emotional_triggers:
            return self.emotional_triggers[trigger_input_lower]
        
        # Vision-specific pattern matching for self-recognition
        if "vision:" in trigger_input_lower and "object:" in trigger_input_lower:
            # Extract object name from vision input like "Vision: me - Object: me, Confidence: 0.8"
            try:
                # Look for "Object: [object_name]" pattern
                object_start = trigger_input_lower.find("object:")
                if object_start != -1:
                    object_part = trigger_input_lower[object_start + 7:].strip()
                    # Remove confidence part if present
                    if "," in object_part:
                        object_name = object_part.split(",")[0].strip()
                    else:
                        object_name = object_part
                    
                    # Check if this is self-recognition
                    if object_name == "me":
                        self.logger.info(f"🎯 Self-recognition detected in vision: {trigger_input}")
                        return self.emotional_triggers["me"]
                    elif object_name.lower() in self.emotional_triggers:
                        return self.emotional_triggers[object_name.lower()]
            except Exception as e:
                self.logger.warning(f"Error parsing vision input: {e}")
        
        # Partial match
        for trigger, effects in self.emotional_triggers.items():
            if trigger in trigger_input_lower or trigger_input_lower in trigger:
                return effects
        
        # Semantic matching for common patterns
        if any(word in trigger_input_lower for word in ["good", "great", "excellent", "wonderful"]):
            return self.emotional_triggers["praise"]
        elif any(word in trigger_input_lower for word in ["bad", "terrible", "awful", "horrible"]):
            return self.emotional_triggers["criticism"]
        elif any(word in trigger_input_lower for word in ["scary", "frightening", "terrifying"]):
            return self.emotional_triggers["stress"]
        elif any(word in trigger_input_lower for word in ["fun", "exciting", "amazing"]):
            return self.emotional_triggers["laughter"]
        
        return None
    
    def _trigger_automatic_body_reactions(self, emotional_state: 'EmotionalState'):
        """
        Automatically trigger body movement reactions based on emotional state changes.
        
        Args:
            emotional_state: The new emotional state
        """
        try:
            # Get coordinated movements for the current emotional state
            movements = self.get_coordinated_movements(emotional_state.primary, emotional_state.intensity)
            
            if movements:
                self.logger.info(f"🎭 Triggering {len(movements)} automatic body reactions for {emotional_state.primary}/{emotional_state.sub_emotion}")
                
                # Execute each movement
                for movement in movements:
                    self._execute_body_movement(movement)
            else:
                # Check if we should trigger default reactions for high-intensity emotions
                if emotional_state.intensity > 0.6:
                    default_movement = self._get_default_reaction_for_emotion(emotional_state.primary, emotional_state.intensity)
                    if default_movement:
                        self.logger.info(f"🎭 Triggering default reaction for high-intensity {emotional_state.primary}")
                        self._execute_body_movement(default_movement)
                        
        except Exception as e:
            self.logger.error(f"❌ Error triggering automatic body reactions: {e}")
    
    def _execute_body_movement(self, movement: Dict[str, Any]):
        """
        Execute a body movement command.
        
        Args:
            movement: Movement configuration dictionary
        """
        try:
            command = movement.get('command', '')
            movement_type = movement.get('type', '')
            description = movement.get('description', '')
            
            if movement_type == 'body_movement':
                self.logger.info(f"🤖 Executing body movement: {command} - {description}")
                # Execute through callback system
                if hasattr(self, 'body_movement_callback') and self.body_movement_callback:
                    self.body_movement_callback(command)
                    
            elif movement_type == 'eye_expression':
                self.logger.info(f"👁️ Executing eye expression: {command} - {description}")
                # Execute through callback system
                if hasattr(self, 'eye_expression_callback') and self.eye_expression_callback:
                    self.eye_expression_callback(command)
                    
        except Exception as e:
            self.logger.error(f"❌ Error executing body movement {movement}: {e}")
    
    def _get_default_reaction_for_emotion(self, emotion: str, intensity: float) -> Optional[Dict[str, Any]]:
        """
        Get default body reaction for emotions that don't have specific scripts.
        
        Args:
            emotion: Primary emotion
            intensity: Emotional intensity
            
        Returns:
            Default movement configuration or None
        """
        try:
            # Default reactions for high-intensity emotions
            if intensity > 0.7:
                if emotion in ['joy', 'happiness']:
                    return {
                        'type': 'body_movement',
                        'command': 'reaction_ecstatic',
                        'description': 'Default ecstatic reaction for high-intensity joy'
                    }
                elif emotion in ['surprise', 'amazement']:
                    return {
                        'type': 'body_movement', 
                        'command': 'reaction_amazed',
                        'description': 'Default amazed reaction for high-intensity surprise'
                    }
                elif emotion in ['fear', 'anxiety']:
                    return {
                        'type': 'body_movement',
                        'command': 'reaction_terrified', 
                        'description': 'Default terrified reaction for high-intensity fear'
                    }
                elif emotion in ['anger', 'frustration']:
                    return {
                        'type': 'body_movement',
                        'command': 'reaction_irritated',
                        'description': 'Default irritated reaction for high-intensity anger'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting default reaction for emotion: {e}")
            return None
    
    def set_body_movement_callback(self, callback):
        """
        Set callback function for body movement execution.
        
        Args:
            callback: Function to call with (command) parameter
        """
        self.body_movement_callback = callback
    
    def set_eye_expression_callback(self, callback):
        """
        Set callback function for eye expression execution.
        
        Args:
            callback: Function to call with (command) parameter
        """
        self.eye_expression_callback = callback
    
    def map_to_main_system_emotion(self, neucogar_emotion: str, neucogar_sub_emotion: str) -> Tuple[str, str]:
        """
        Map NEUCOGAR emotions to main system emotions for consistency.
        
        Args:
            neucogar_emotion: Primary emotion from NEUCOGAR (e.g., "joy")
            neucogar_sub_emotion: Sub-emotion from NEUCOGAR (e.g., "ecstatic")
            
        Returns:
            Tuple of (main_primary, main_sub) emotions
        """
        # Mapping from NEUCOGAR to main system emotions
        emotion_mapping = {
            "joy": ("happiness", "joyful"),
            "satisfaction": ("happiness", "content"),  # satisfaction -> happiness/content
            "excitement": ("happiness", "joyful"),     # excitement -> happiness/joyful
            "anger": ("anger", "frustrated"),
            "fear": ("fear", "anxious"),
            "sadness": ("sadness", "hurt"),
            "surprise": ("surprise", "startled"),
            "disgust": ("disgust", "disapproving"),
            "neutral": ("neutral", "calm")
        }
        
        # Get main system primary and sub-emotion
        main_primary, main_sub = emotion_mapping.get(neucogar_emotion, (neucogar_emotion, "general"))
        
        # For joy -> happiness/joyful, ensure sub-emotion is valid
        if neucogar_emotion == "joy" and neucogar_sub_emotion in ["ecstatic", "delighted"]:
            main_sub = neucogar_sub_emotion  # Use the valid sub-emotion directly
        elif neucogar_emotion == "joy":
            # If invalid sub-emotion, default to "ecstatic" for high intensity, "delighted" for lower
            main_sub = "ecstatic" if neucogar_sub_emotion in ["elated", "thrilled"] else "delighted"
        
        # For satisfaction -> happiness/content, ensure sub-emotion is valid
        elif neucogar_emotion == "satisfaction" and neucogar_sub_emotion in ["satisfied", "fulfilled"]:
            main_sub = neucogar_sub_emotion  # Use the valid sub-emotion directly
        elif neucogar_emotion == "satisfaction":
            # Default to "satisfied" for satisfaction emotions
            main_sub = "satisfied"
        
        return main_primary, main_sub
    
    def get_main_system_emotion(self) -> Dict[str, str]:
        """
        Get current emotional state mapped to main system format.
        
        Returns:
            Dictionary with main system emotion format
        """
        main_primary, main_sub = self.map_to_main_system_emotion(
            self.current_state.primary, 
            self.current_state.sub_emotion
        )
        
        return {
            "primary": main_primary,
            "sub_emotion": main_sub,
            "neucogar_primary": self.current_state.primary,
            "neucogar_sub_emotion": self.current_state.sub_emotion,
            "intensity": self.current_state.intensity,
            "timestamp": self.current_state.timestamp.isoformat()
        }
    
    def handle_self_recognition_event(self, confidence: float = 0.8, context: str = "vision") -> Dict[str, Any]:
        """
        Handle a self-recognition event with special emotional and memory effects.
        
        Args:
            confidence: Confidence level of self-recognition (0.0 to 1.0)
            context: Context of recognition (e.g., "vision", "mirror", "reflection")
            
        Returns:
            Dictionary with emotional state and self-awareness data
        """
        try:
            # Determine trigger based on confidence and context
            if confidence >= 0.8:
                if context == "mirror":
                    trigger = "mirror_test"
                else:
                    trigger = "self_recognition"
            else:
                trigger = "self_awareness"
            
            # Apply emotional effects
            self.update_emotion_state(trigger)
            
            # Create self-awareness memory data
            self_awareness_data = {
                "event_type": "self_recognition",
                "confidence": confidence,
                "context": context,
                "trigger_used": trigger,
                "emotional_state": self.get_current_emotion(),
                "timestamp": datetime.now().isoformat(),
                "neurotransmitter_effects": {
                    "dopamine": "increased (curiosity and reward)",
                    "serotonin": "increased (confidence and self-satisfaction)", 
                    "norepinephrine": "increased (alertness and self-awareness)",
                    "acetylcholine": "increased (attention and self-focus)"
                },
                "cognitive_implications": [
                    "Self-awareness confirmation",
                    "Identity recognition",
                    "Mirror test behavior",
                    "Meta-cognitive awareness"
                ]
            }
            
            # Log the self-recognition event
            self.logger.info(f"🎯 Self-recognition event processed: {context} (confidence: {confidence:.2f})")
            self.logger.info(f"   Trigger: {trigger}")
            self.logger.info(f"   Emotional state: {self.current_state.primary}/{self.current_state.sub_emotion}")
            
            return self_awareness_data
            
        except Exception as e:
            self.logger.error(f"Error handling self-recognition event: {e}")
            return {"error": str(e)}
    
    def _adjust_neurotransmitters(self, effects: Dict[str, float]):
        """Adjust current neurotransmitter levels based on trigger effects."""
        current = self.current_state.neuro_coordinates
        
        new_da = current.dopamine + effects.get("dopamine", 0.0)
        new_5ht = current.serotonin + effects.get("serotonin", 0.0)
        new_ne = current.noradrenaline + effects.get("noradrenaline", 0.0)
        
        # Apply some natural decay/regulation
        new_da *= 0.95  # Slight decay
        new_5ht *= 0.97  # More stable
        new_ne *= 0.90   # Faster decay
        
        self.current_state.neuro_coordinates = NeuroCoordinates(new_da, new_5ht, new_ne)
    
    def _adjust_extended_neurotransmitters(self, trigger_input: str):
        """Adjust extended neurotransmitter levels based on trigger input."""
        trigger_input_lower = trigger_input.lower()
        
        # Find matching extended effects
        extended_effects = None
        for trigger, effects in self.extended_neuro_effects.items():
            if trigger in trigger_input_lower or trigger_input_lower in trigger:
                extended_effects = effects
                break
        
        if extended_effects:
            current_extended = self.current_state.extended_neurotransmitters
            
            # Apply effects to extended neurotransmitters
            for nt_name, effect in extended_effects.items():
                if hasattr(current_extended, nt_name):
                    current_value = getattr(current_extended, nt_name)
                    new_value = current_value + effect
                    setattr(current_extended, nt_name, max(0.0, min(1.0, new_value)))
            
            # Apply homeostasis
            current_extended.apply_homeostasis()
            
            # Update NEUCOGAR coordinates from extended neurotransmitters
            self.current_state.neuro_coordinates = current_extended.get_neucogar_coordinates()
    
    def _resolve_emotional_state(self) -> EmotionalState:
        """
        Resolve current emotional state based on proximity to core emotions in the cube.
        
        Returns:
            New emotional state with primary, sub-emotion, and detail
        """
        current_coords = self.current_state.neuro_coordinates
        
        # Find closest core emotion
        closest_emotion = "neutral"
        min_distance = float('inf')
        
        for emotion, coords in self.core_emotions.items():
            distance = current_coords.distance_to(coords)
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion
        
        # Find appropriate sub-emotion based on depth
        sub_emotion = self._find_sub_emotion(closest_emotion, current_coords)
        
        # Generate detail based on intensity and context
        detail = self._generate_emotional_detail(closest_emotion, sub_emotion, current_coords)
        
        # Calculate intensity based on distance from neutral
        intensity = self._calculate_emotional_intensity(current_coords)
        
        return EmotionalState(
            primary=closest_emotion,
            sub_emotion=sub_emotion,
            detail=detail,
            neuro_coordinates=current_coords,
            extended_neurotransmitters=self.current_state.extended_neurotransmitters, # Keep extended neurotransmitters
            intensity=intensity,
            timestamp=datetime.now()
        )
    
    def _find_sub_emotion(self, primary_emotion: str, coords: NeuroCoordinates) -> str:
        """Find appropriate sub-emotion based on depth in the cube."""
        # Get all sub-emotions for this primary emotion
        emotion_subs = {k: v for k, v in self.sub_emotions.items() 
                       if v[0] == primary_emotion}
        
        if not emotion_subs:
            return "general"
        
        # Calculate depth factor based on distance from center
        center_distance = math.sqrt(coords.dopamine**2 + coords.serotonin**2 + coords.noradrenaline**2)
        depth_factor = min(1.0, center_distance / math.sqrt(3))  # Normalize to 0-1
        
        # Find sub-emotion with closest depth factor
        closest_sub = "general"
        min_depth_diff = float('inf')
        
        for sub_emotion, (_, sub_depth) in emotion_subs.items():
            depth_diff = abs(depth_factor - sub_depth)
            if depth_diff < min_depth_diff:
                min_depth_diff = depth_diff
                closest_sub = sub_emotion
        
        return closest_sub
    
    def _generate_emotional_detail(self, primary: str, sub_emotion: str, coords: NeuroCoordinates) -> str:
        """Generate detailed emotional description based on context."""
        intensity = self._calculate_emotional_intensity(coords)
        
        # Base descriptions
        detail_templates = {
            "anger": ["slightly irritated", "moderately frustrated", "quite angry", "deeply enraged"],
            "sadness": ["slightly down", "moderately sad", "quite melancholy", "deeply depressed"],
            "fear": ["slightly anxious", "moderately worried", "quite scared", "deeply terrified"],
            "joy": ["slightly happy", "moderately pleased", "quite joyful", "deeply elated"],
            "surprise": ["slightly surprised", "moderately amazed", "quite shocked", "deeply stunned"],
            "disgust": ["slightly bothered", "moderately disturbed", "quite repulsed", "deeply revolted"],
            "neutral": ["slightly calm", "moderately balanced", "quite centered", "deeply serene"]
        }
        
        templates = detail_templates.get(primary, detail_templates["neutral"])
        
        # Select template based on intensity
        if intensity < 0.25:
            detail = templates[0]
        elif intensity < 0.5:
            detail = templates[1]
        elif intensity < 0.75:
            detail = templates[2]
        else:
            detail = templates[3]
        
        # Add neurochemical context
        neuro_context = []
        if coords.dopamine > 0.5:
            neuro_context.append("motivated")
        elif coords.dopamine < -0.5:
            neuro_context.append("unmotivated")
        
        if coords.serotonin > 0.5:
            neuro_context.append("confident")
        elif coords.serotonin < -0.5:
            neuro_context.append("insecure")
        
        if coords.noradrenaline > 0.5:
            neuro_context.append("alert")
        elif coords.noradrenaline < -0.5:
            neuro_context.append("drowsy")
        
        if neuro_context:
            detail += f" and {', '.join(neuro_context)}"
        
        return detail
    
    def _calculate_emotional_intensity(self, coords: NeuroCoordinates) -> float:
        """Calculate emotional intensity based on distance from neutral center."""
        return min(1.0, math.sqrt(coords.dopamine**2 + coords.serotonin**2 + coords.noradrenaline**2) / math.sqrt(3))
    
    def _log_emotional_transition(self, state: EmotionalState):
        """Log emotional state transition to session log."""
        self.session_log.append(state)
        
        # Keep only last 1000 transitions to prevent memory bloat
        if len(self.session_log) > 1000:
            self.session_log = self.session_log[-1000:]
    
    def generate_emotion_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive emotional trajectory report for the session.
        
        Returns:
            Dictionary containing emotion frequency histogram, neurotransmitter averages,
            peak emotional states, and most common emotions
        """
        if not self.session_log:
            return {"error": "No emotional data available for this session"}
        
        # Emotion frequency histogram
        emotion_counts = {}
        sub_emotion_counts = {}
        
        for state in self.session_log:
            emotion_counts[state.primary] = emotion_counts.get(state.primary, 0) + 1
            sub_emotion_counts[state.sub_emotion] = sub_emotion_counts.get(state.sub_emotion, 0) + 1
        
        # Neurotransmitter average values
        total_da = sum(state.neuro_coordinates.dopamine for state in self.session_log)
        total_5ht = sum(state.neuro_coordinates.serotonin for state in self.session_log)
        total_ne = sum(state.neuro_coordinates.noradrenaline for state in self.session_log)
        count = len(self.session_log)
        
        avg_neuro = {
            "dopamine": total_da / count,
            "serotonin": total_5ht / count,
            "noradrenaline": total_ne / count
        }
        
        # Peak emotional states (most intense DA/NE/5-HT)
        peak_da_state = max(self.session_log, key=lambda s: s.neuro_coordinates.dopamine)
        peak_5ht_state = max(self.session_log, key=lambda s: s.neuro_coordinates.serotonin)
        peak_ne_state = max(self.session_log, key=lambda s: s.neuro_coordinates.noradrenaline)
        
        peak_states = {
            "peak_dopamine": {
                "emotion": f"{peak_da_state.primary}/{peak_da_state.sub_emotion}",
                "value": peak_da_state.neuro_coordinates.dopamine,
                "timestamp": peak_da_state.timestamp.isoformat()
            },
            "peak_serotonin": {
                "emotion": f"{peak_5ht_state.primary}/{peak_5ht_state.sub_emotion}",
                "value": peak_5ht_state.neuro_coordinates.serotonin,
                "timestamp": peak_5ht_state.timestamp.isoformat()
            },
            "peak_noradrenaline": {
                "emotion": f"{peak_ne_state.primary}/{peak_ne_state.sub_emotion}",
                "value": peak_ne_state.neuro_coordinates.noradrenaline,
                "timestamp": peak_ne_state.timestamp.isoformat()
            }
        }
        
        # Most common primary + sub-emotion
        emotion_sub_pairs = {}
        for state in self.session_log:
            pair = f"{state.primary}/{state.sub_emotion}"
            emotion_sub_pairs[pair] = emotion_sub_pairs.get(pair, 0) + 1
        
        most_common_pair = max(emotion_sub_pairs.items(), key=lambda x: x[1]) if emotion_sub_pairs else ("none/none", 0)
        
        # Session statistics
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        transitions_per_minute = len(self.session_log) / (session_duration / 60) if session_duration > 0 else 0
        
        return {
            "session_info": {
                "start_time": self.session_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": session_duration,
                "total_transitions": len(self.session_log),
                "transitions_per_minute": transitions_per_minute
            },
            "emotion_frequency_histogram": emotion_counts,
            "sub_emotion_frequency_histogram": sub_emotion_counts,
            "neurotransmitter_averages": avg_neuro,
            "peak_emotional_states": peak_states,
            "most_common_emotion_pair": {
                "emotion": most_common_pair[0],
                "frequency": most_common_pair[1]
            },
            "emotional_trajectory_summary": self._generate_trajectory_summary()
        }
    
    def _generate_trajectory_summary(self) -> str:
        """Generate a comprehensive narrative summary of the emotional trajectory."""
        if len(self.session_log) < 2:
            return "Insufficient data for trajectory analysis"
        
        # Analyze emotional flow
        transitions = []
        for i in range(1, len(self.session_log)):
            prev = self.session_log[i-1]
            curr = self.session_log[i]
            
            if prev.primary != curr.primary:
                transitions.append(f"{prev.primary} → {curr.primary}")
        
        # Find dominant patterns
        transition_counts = {}
        for transition in transitions:
            transition_counts[transition] = transition_counts.get(transition, 0) + 1
        
        most_common_transition = max(transition_counts.items(), key=lambda x: x[1]) if transition_counts else ("none", 0)
        
        # Calculate emotional stability
        unique_emotions = len(set(state.primary for state in self.session_log))
        stability_score = 1.0 - (unique_emotions / len(self.session_log)) if self.session_log else 0.0
        
        # Analyze neurotransmitter patterns
        avg_da = sum(state.neuro_coordinates.dopamine for state in self.session_log) / len(self.session_log)
        avg_5ht = sum(state.neuro_coordinates.serotonin for state in self.session_log) / len(self.session_log)
        avg_ne = sum(state.neuro_coordinates.noradrenaline for state in self.session_log) / len(self.session_log)
        
        # Detect humor and social engagement patterns
        humor_indicators = []
        social_engagement = []
        
        for state in self.session_log:
            # Check for humor indicators (high dopamine, moderate serotonin, low norepinephrine)
            if (state.neuro_coordinates.dopamine > 0.6 and 
                state.neuro_coordinates.serotonin > 0.4 and 
                state.neuro_coordinates.noradrenaline < 0.3):
                humor_indicators.append(state)
            
            # Check for social engagement (moderate dopamine, high serotonin)
            if (state.neuro_coordinates.dopamine > 0.4 and 
                state.neuro_coordinates.serotonin > 0.6):
                social_engagement.append(state)
        
        # Generate comprehensive summary
        summary_parts = []
        
        # Emotional stability analysis
        if stability_score > 0.7:
            summary_parts.append("The emotional state remained relatively stable throughout the session")
        elif stability_score > 0.4:
            summary_parts.append("The emotional state showed moderate variability")
        else:
            summary_parts.append("The emotional state was highly dynamic and variable")
        
        # Transition patterns
        if most_common_transition[1] > 1:
            summary_parts.append(f"with the most frequent transition being {most_common_transition[0]}")
        
        # Neurotransmitter analysis
        if avg_da > 0.6:
            summary_parts.append("Elevated dopamine levels suggest positive engagement and reward-seeking behavior")
        elif avg_da < 0.3:
            summary_parts.append("Lower dopamine levels indicate reduced motivation or positive reinforcement")
        
        if avg_5ht > 0.6:
            summary_parts.append("High serotonin levels reflect emotional stability and social confidence")
        elif avg_5ht < 0.3:
            summary_parts.append("Lower serotonin levels suggest potential mood instability")
        
        if avg_ne > 0.6:
            summary_parts.append("Elevated norepinephrine indicates high arousal and alertness")
        elif avg_ne < 0.3:
            summary_parts.append("Lower norepinephrine suggests calm, relaxed states")
        
        # Humor and social behavior analysis
        if humor_indicators:
            summary_parts.append(f"Humor and playful behavior were detected in {len(humor_indicators)} emotional states, characterized by elevated dopamine (reward response) and serotonin (social comfort) with reduced norepinephrine (relaxed engagement)")
        
        if social_engagement:
            summary_parts.append(f"Strong social engagement patterns were observed in {len(social_engagement)} states, indicating positive interpersonal interactions")
        
        # Intensity analysis
        avg_intensity = sum(state.intensity for state in self.session_log) / len(self.session_log)
        if avg_intensity > 0.7:
            summary_parts.append("Overall emotional intensity was high")
        elif avg_intensity > 0.4:
            summary_parts.append("Overall emotional intensity was moderate")
        else:
            summary_parts.append("Overall emotional intensity was low")
        
        # Cognitive and behavioral implications
        if len(humor_indicators) > 0 and len(social_engagement) > 0:
            summary_parts.append("The session demonstrates sophisticated social cognition, including humor generation and appropriate social responses, indicating advanced emotional intelligence and social awareness")
        
        return ". ".join(summary_parts) + "."
    
    def reset_session(self):
        """Reset the session log and start a new session."""
        self.session_log = []
        self.session_start_time = datetime.now()
        self.current_state = self._initialize_neutral_state()
        self._log_emotional_transition(self.current_state)
        self.logger.info("NEUCOGAR emotional session reset")
    
    def get_session_log(self) -> List[Dict[str, Any]]:
        """Get the session log as a list of dictionaries."""
        return [state.to_dict() for state in self.session_log]
    
    def export_session_data(self, filename: str = None) -> str:
        """
        Export session data to a JSON file.
        
        Args:
            filename: Optional filename, defaults to timestamp-based name
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"neucogar_session_{timestamp}.json"
        
        data = {
            "session_info": {
                "start_time": self.session_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "engine_version": "NEUCOGAR v1.0",
                "lovheim_cube_reference": "Lövheim, 2012"
            },
            "current_state": self.current_state.to_dict(),
            "session_log": self.get_session_log(),
            "report": self.generate_emotion_report()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Session data exported to {filename}")
        return filename
    
    def update_from_event(self, event: Dict[str, Any]) -> AffectSnapshot:
        """
        Update NEUCOGAR emotional state based on an incoming event.
        
        Args:
            event: Event context dictionary with triggers, content, etc.
            
        Returns:
            AffectSnapshot with updated emotional state
        """
        # Extract triggers from event
        triggers = self._extract_triggers_from_event(event)
        
        # Apply triggers to current state
        updated_state = self._apply_triggers_to_state(triggers)
        
        # Determine emotion and sub-emotion
        primary_emotion, sub_emotion = self._determine_emotion_and_sub_emotion(updated_state)
        
        # Update the state with new emotion/sub-emotion
        updated_state.primary = primary_emotion
        updated_state.sub_emotion = sub_emotion
        
        # Update rolling statistics
        self._update_rolling_stats(updated_state)
        
        # Log the transition
        self._log_emotional_transition(updated_state)
        
        # Create and return affect snapshot
        snapshot = AffectSnapshot(
            primary_emotion=primary_emotion,
            sub_emotion=sub_emotion,
            neuro_coordinates=updated_state.neuro_coordinates,
            extended_neurotransmitters=updated_state.extended_neurotransmitters,
            intensity=updated_state.intensity,
            triggers=triggers,
            timestamp=datetime.now()
        )
        
        # Update current state
        self.current_state = updated_state
        
        return snapshot

    def _extract_triggers_from_event(self, event: Dict[str, Any]) -> List[str]:
        """Extract emotional triggers from an event."""
        triggers = []
        
        # Extract from event type
        event_type = event.get('event_type', '')
        if event_type == 'vision':
            triggers.append('visual_stimulation')
        elif event_type == 'speech':
            triggers.append('social_interaction')
        elif event_type == 'action':
            triggers.append('physical_activity')
        elif event_type == 'memory':
            triggers.append('memory_recall')
        
        # Extract from content
        content = event.get('content', '').lower()
        if any(word in content for word in ['joke', 'funny', 'laugh', 'humor']):
            triggers.append('humor')
        if any(word in content for word in ['sad', 'unhappy', 'disappointed']):
            triggers.append('negative_emotion')
        if any(word in content for word in ['happy', 'joy', 'excited', 'great']):
            triggers.append('positive_emotion')
        if any(word in content for word in ['scared', 'afraid', 'fear']):
            triggers.append('fear')
        if any(word in content for word in ['angry', 'mad', 'frustrated']):
            triggers.append('anger')
        
        # Extract from concepts
        concepts = event.get('concepts', [])
        for concept in concepts:
            if concept.lower() in ['friend', 'family', 'love']:
                triggers.append('social_bonding')
            elif concept.lower() in ['work', 'task', 'goal']:
                triggers.append('goal_oriented')
            elif concept.lower() in ['food', 'eat', 'hungry']:
                triggers.append('basic_need')
        
        return triggers

    def _apply_triggers_to_state(self, triggers: List[str]) -> EmotionalState:
        """Apply triggers to current state and return updated state."""
        # Start with current state
        current_state = self.current_state
        
        # Create new neuro coordinates
        new_coords = NeuroCoordinates(
            current_state.neuro_coordinates.dopamine,
            current_state.neuro_coordinates.serotonin,
            current_state.neuro_coordinates.noradrenaline
        )
        
        # Create new extended neurotransmitters
        new_extended = ExtendedNeurotransmitters(
            current_state.extended_neurotransmitters.dopamine,
            current_state.extended_neurotransmitters.serotonin,
            current_state.extended_neurotransmitters.norepinephrine,
            current_state.extended_neurotransmitters.gaba,
            current_state.extended_neurotransmitters.glutamate,
            current_state.extended_neurotransmitters.acetylcholine,
            current_state.extended_neurotransmitters.oxytocin,
            current_state.extended_neurotransmitters.endorphins
        )
        
        # Apply trigger effects
        for trigger in triggers:
            if trigger in self.emotional_triggers:
                effect = self.emotional_triggers[trigger]
                new_coords.dopamine += effect.get('dopamine', 0.0)
                new_coords.serotonin += effect.get('serotonin', 0.0)
                new_coords.noradrenaline += effect.get('noradrenaline', 0.0)
            
            if trigger in self.extended_neuro_effects:
                effect = self.extended_neuro_effects[trigger]
                new_extended.dopamine += effect.get('dopamine', 0.0)
                new_extended.serotonin += effect.get('serotonin', 0.0)
                new_extended.norepinephrine += effect.get('norepinephrine', 0.0)
                new_extended.gaba += effect.get('gaba', 0.0)
                new_extended.glutamate += effect.get('glutamate', 0.0)
                new_extended.acetylcholine += effect.get('acetylcholine', 0.0)
                new_extended.oxytocin += effect.get('oxytocin', 0.0)
                new_extended.endorphins += effect.get('endorphins', 0.0)
        
        # Create updated state
        updated_state = EmotionalState(
            primary=current_state.primary,
            sub_emotion=current_state.sub_emotion,
            detail=f"Updated by triggers: {', '.join(triggers)}",
            neuro_coordinates=new_coords,
            extended_neurotransmitters=new_extended,
            intensity=current_state.intensity,
            timestamp=datetime.now()
        )
        
        return updated_state

    def _determine_emotion_and_sub_emotion(self, state: EmotionalState) -> Tuple[str, str]:
        """Determine primary emotion and sub-emotion from neuro coordinates."""
        coords = state.neuro_coordinates
        
        # Find closest core emotion
        closest_emotion = "neutral"
        min_distance = float('inf')
        
        for emotion, emotion_coords in self.core_emotions.items():
            distance = coords.distance_to(emotion_coords)
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion
        
        # Determine sub-emotion based on intensity and context
        sub_emotion = self._select_sub_emotion(closest_emotion, state.intensity, coords)
        
        return closest_emotion, sub_emotion

    def _select_sub_emotion(self, primary_emotion: str, intensity: float, coords: NeuroCoordinates) -> str:
        """Select appropriate sub-emotion based on primary emotion and intensity."""
        if primary_emotion not in self.sub_emotions:
            return "calm"
        
        available_subs = self.sub_emotions[primary_emotion]
        
        # Select based on intensity and depth
        if intensity < 0.3:
            # Low intensity - surface level emotions
            surface_subs = [sub for sub, (_, depth) in available_subs.items() if depth < 0.5]
            return surface_subs[0] if surface_subs else "calm"
        elif intensity > 0.7:
            # High intensity - deep emotions
            deep_subs = [sub for sub, (_, depth) in available_subs.items() if depth > 0.7]
            return deep_subs[0] if deep_subs else "calm"
        else:
            # Medium intensity - moderate depth
            moderate_subs = [sub for sub, (_, depth) in available_subs.items() if 0.3 <= depth <= 0.7]
            return moderate_subs[0] if moderate_subs else "calm"

    def _update_rolling_stats(self, state: EmotionalState):
        """Update rolling statistics for NEUCOGAR monitoring."""
        if not hasattr(self, 'rolling_stats'):
            self.rolling_stats = {
                'dopamine': {'min': 1.0, 'max': -1.0, 'avg': 0.0, 'count': 0},
                'serotonin': {'min': 1.0, 'max': -1.0, 'avg': 0.0, 'count': 0},
                'noradrenaline': {'min': 1.0, 'max': -1.0, 'avg': 0.0, 'count': 0}
            }
        
        coords = state.neuro_coordinates
        
        for nt in ['dopamine', 'serotonin', 'noradrenaline']:
            value = getattr(coords, nt)
            stats = self.rolling_stats[nt]
            
            stats['min'] = min(stats['min'], value)
            stats['max'] = max(stats['max'], value)
            stats['count'] += 1
            stats['avg'] = (stats['avg'] * (stats['count'] - 1) + value) / stats['count'] 
    
    def update_neurotransmitter_levels(self, new_levels: Dict[str, float]):
        """
        Update neurotransmitter levels directly (for exercise system integration).
        
        Args:
            new_levels: Dictionary of neurotransmitter levels to update
        """
        try:
            # Update extended neurotransmitters
            for nt, level in new_levels.items():
                if hasattr(self.current_state.extended_neurotransmitters, nt):
                    setattr(self.current_state.extended_neurotransmitters, nt, max(0.0, min(1.0, level)))
            
            # Update core neuro coordinates (convert from 0.0-1.0 to -1.0 to +1.0)
            if 'dopamine' in new_levels:
                self.current_state.neuro_coordinates.dopamine = (new_levels['dopamine'] - 0.5) * 2.0
            if 'serotonin' in new_levels:
                self.current_state.neuro_coordinates.serotonin = (new_levels['serotonin'] - 0.5) * 2.0
            if 'norepinephrine' in new_levels:
                self.current_state.neuro_coordinates.noradrenaline = (new_levels['norepinephrine'] - 0.5) * 2.0
            
            # Resolve new emotional state
            new_state = self._resolve_emotional_state()
            self.current_state = new_state
            
            # Log the update
            self.logger.info(f"Updated neurotransmitter levels: {new_levels}")
            
        except Exception as e:
            self.logger.error(f"Error updating neurotransmitter levels: {e}")
    
    def get_neurotransmitter_state(self) -> Dict[str, float]:
        """
        Get current neurotransmitter state for external systems.
        
        Returns:
            Dictionary of current neurotransmitter levels (0.0-1.0 range)
        """
        try:
            return {
                "dopamine": self.current_state.extended_neurotransmitters.dopamine,
                "serotonin": self.current_state.extended_neurotransmitters.serotonin,
                "norepinephrine": self.current_state.extended_neurotransmitters.norepinephrine,
                "gaba": self.current_state.extended_neurotransmitters.gaba,
                "glutamate": self.current_state.extended_neurotransmitters.glutamate,
                "acetylcholine": self.current_state.extended_neurotransmitters.acetylcholine,
                "oxytocin": self.current_state.extended_neurotransmitters.oxytocin,
                "endorphins": self.current_state.extended_neurotransmitters.endorphins
            }
        except Exception as e:
            self.logger.error(f"Error getting neurotransmitter state: {e}")
            return {
                "dopamine": 0.3, "serotonin": 0.4, "norepinephrine": 0.2,
                "gaba": 0.35, "glutamate": 0.45, "acetylcholine": 0.3,
                "oxytocin": 0.25, "endorphins": 0.2
            }
    
    def update_neurotransmitters(self, changes: Dict[str, float]):
        """
        Update neurotransmitter levels with specified changes.
        
        Args:
            changes: Dictionary of neurotransmitter changes to apply
        """
        try:
            # Update extended neurotransmitters
            for nt, change in changes.items():
                if hasattr(self.current_state.extended_neurotransmitters, nt):
                    current_value = getattr(self.current_state.extended_neurotransmitters, nt)
                    new_value = max(0.0, min(1.0, current_value + change))
                    setattr(self.current_state.extended_neurotransmitters, nt, new_value)
            
            # Update core neuro coordinates (convert from 0.0-1.0 to -1.0 to +1.0)
            if 'dopamine' in changes:
                self.current_state.neuro_coordinates.dopamine = (self.current_state.extended_neurotransmitters.dopamine - 0.5) * 2.0
            if 'serotonin' in changes:
                self.current_state.neuro_coordinates.serotonin = (self.current_state.extended_neurotransmitters.serotonin - 0.5) * 2.0
            if 'norepinephrine' in changes:
                self.current_state.neuro_coordinates.noradrenaline = (self.current_state.extended_neurotransmitters.norepinephrine - 0.5) * 2.0
            
            # Resolve new emotional state
            new_state = self._resolve_emotional_state()
            self.current_state = new_state
            
            # Log the update
            self.logger.info(f"Updated neurotransmitters: {changes}")
            
        except Exception as e:
            self.logger.error(f"Error updating neurotransmitters: {e}")
    
    def trigger_neurotransmitter_effect(self, neurotransmitter: str, effect: float, reason: str = ""):
        """
        Trigger a specific neurotransmitter effect.
        
        Args:
            neurotransmitter: Name of the neurotransmitter to affect
            effect: Effect magnitude (positive or negative)
            reason: Reason for the effect (for logging)
        """
        try:
            changes = {neurotransmitter: effect}
            self.update_neurotransmitters(changes)
            
            if reason:
                self.logger.info(f"Triggered {neurotransmitter} effect ({effect:+.3f}): {reason}")
            else:
                self.logger.info(f"Triggered {neurotransmitter} effect: {effect:+.3f}")
                
        except Exception as e:
            self.logger.error(f"Error triggering neurotransmitter effect: {e}")
    

    
    def detect_role_playing_request(self, text: str) -> Optional[str]:
        """
        Detect if text contains a role-playing emotional request.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Emotional trigger string if role-playing detected, None otherwise
        """
        text_lower = text.lower()
        
        # Role-playing patterns
        role_playing_patterns = {
            # Act patterns
            "act_amazed": ["act amazed", "act like you're amazed", "act as if amazed"],
            "act_surprised": ["act surprised", "act like you're surprised", "act as if surprised"],
            "act_amused": ["act amused", "act like you're amused", "act as if amused"],
            "act_joyful": ["act joyful", "act happy", "act like you're happy", "act as if happy"],
            "act_ecstatic": ["act ecstatic", "act like you're ecstatic", "act as if ecstatic"],
            "act_terrified": ["act terrified", "act like you're terrified", "act as if terrified"],
            "act_scared": ["act scared", "act afraid", "act like you're scared", "act as if scared"],
            "act_irritated": ["act irritated", "act annoyed", "act like you're irritated", "act as if irritated"],
            "act_angry": ["act angry", "act mad", "act like you're angry", "act as if angry"],
            "act_sad": ["act sad", "act like you're sad", "act as if sad"],
            
            # Pretend patterns
            "pretend_amazed": ["pretend to be amazed", "pretend amazed", "pretend like amazed"],
            "pretend_surprised": ["pretend to be surprised", "pretend surprised", "pretend like surprised"],
            "pretend_amused": ["pretend to be amused", "pretend amused", "pretend like amused"],
            "pretend_joyful": ["pretend to be joyful", "pretend happy", "pretend to be happy", "pretend like happy"],
            "pretend_ecstatic": ["pretend to be ecstatic", "pretend ecstatic", "pretend like ecstatic"],
            "pretend_terrified": ["pretend to be terrified", "pretend terrified", "pretend like terrified"],
            "pretend_scared": ["pretend to be scared", "pretend scared", "pretend afraid", "pretend like scared"],
            "pretend_irritated": ["pretend to be irritated", "pretend irritated", "pretend annoyed", "pretend like irritated"],
            "pretend_angry": ["pretend to be angry", "pretend angry", "pretend mad", "pretend like angry"],
            "pretend_sad": ["pretend to be sad", "pretend sad", "pretend like sad"],
            
            # Show patterns
            "show_amazed": ["show amazed", "show me amazed", "demonstrate amazed"],
            "show_surprised": ["show surprised", "show me surprised", "demonstrate surprised"],
            "show_amused": ["show amused", "show me amused", "demonstrate amused"],
            "show_joyful": ["show joyful", "show happy", "show me happy", "demonstrate happy"],
            "show_ecstatic": ["show ecstatic", "show me ecstatic", "demonstrate ecstatic"],
            "show_terrified": ["show terrified", "show me terrified", "demonstrate terrified"],
            "show_scared": ["show scared", "show afraid", "show me scared", "demonstrate scared"],
            "show_irritated": ["show irritated", "show annoyed", "show me irritated", "demonstrate irritated"],
            "show_angry": ["show angry", "show mad", "show me angry", "demonstrate angry"],
            "show_sad": ["show sad", "show me sad", "demonstrate sad"],
            
            # Can you patterns
            "act_amazed": ["can you act amazed", "could you act amazed", "would you act amazed"],
            "act_surprised": ["can you act surprised", "could you act surprised", "would you act surprised"],
            "act_amused": ["can you act amused", "could you act amused", "would you act amused"],
            "act_joyful": ["can you act happy", "could you act happy", "would you act happy"],
            "act_ecstatic": ["can you act ecstatic", "could you act ecstatic", "would you act ecstatic"],
            "act_terrified": ["can you act terrified", "could you act terrified", "would you act terrified"],
            "act_scared": ["can you act scared", "could you act scared", "would you act scared"],
            "act_irritated": ["can you act irritated", "could you act irritated", "would you act irritated"],
            "act_angry": ["can you act angry", "could you act angry", "would you act angry"],
            "act_sad": ["can you act sad", "could you act sad", "would you act sad"],
        }
        
        # Check for role-playing patterns
        for trigger, patterns in role_playing_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return trigger
        
        return None