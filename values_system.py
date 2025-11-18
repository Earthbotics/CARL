#!/usr/bin/env python3
"""
Values System for CARL
Based on neuroscience principles of reward systems, prefrontal cortex, and emotional weighting.
This system implements the values and beliefs architecture described in the neuroscience notes.
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
import logging
from enum import Enum

class ValueType(Enum):
    """Types of values based on neuroscience categorization."""
    MORAL = "moral"           # vmPFC - abstract moral principles
    PERSONAL = "personal"     # vmPFC - personal life goals and standards
    SOCIAL = "social"         # vmPFC + amygdala - social norms and relationships
    INSTRUMENTAL = "instrumental"  # dlPFC - practical values for goal achievement
    EMOTIONAL = "emotional"   # Amygdala - emotionally weighted values

class BeliefType(Enum):
    """Types of beliefs based on cognitive function."""
    FACTUAL = "factual"       # Evidence-based beliefs about reality
    RELATIONAL = "relational" # Beliefs about relationships and social dynamics
    CAUSAL = "causal"         # Beliefs about cause and effect
    NORMATIVE = "normative"   # Beliefs about what should be
    IDENTITY = "identity"     # Beliefs about self and identity

@dataclass
class Value:
    """Represents a single value with neuroscience-based properties."""
    id: str
    name: str
    description: str
    value_type: ValueType
    strength: float  # 0.0 to 1.0 - how strongly held
    emotional_weight: float  # 0.0 to 1.0 - amygdala weighting
    prefrontal_representation: float  # 0.0 to 1.0 - vmPFC/OFC strength
    reward_association: float  # 0.0 to 1.0 - nucleus accumbens association
    conflict_threshold: float  # 0.0 to 1.0 - ACC conflict detection threshold
    created: str
    last_reinforced: str
    reinforcement_count: int
    source: str  # 'innate', 'learned', 'socialized', 'reflection'
    related_values: List[str]  # IDs of related values
    opposing_values: List[str]  # IDs of opposing values
    neurotransmitter_profile: Dict[str, float]  # Dopamine, serotonin, etc.
    stability: float  # 0.0 to 1.0 - resistance to change

@dataclass
class Belief:
    """Represents a belief with cognitive and emotional properties."""
    id: str
    name: str
    description: str
    belief_type: BeliefType
    confidence: float  # 0.0 to 1.0 - how confident in the belief
    evidence_strength: float  # 0.0 to 1.0 - strength of supporting evidence
    emotional_attachment: float  # 0.0 to 1.0 - emotional investment
    value_alignment: float  # 0.0 to 1.0 - alignment with core values
    created: str
    last_updated: str
    update_count: int
    source: str  # 'experience', 'observation', 'inference', 'social'
    related_beliefs: List[str]  # IDs of related beliefs
    contradicting_beliefs: List[str]  # IDs of contradicting beliefs
    hippocampus_strength: float  # 0.0 to 1.0 - memory consolidation strength
    prefrontal_evaluation: float  # 0.0 to 1.0 - PFC evaluation strength

@dataclass
class ValueConflict:
    """Represents a conflict between values or beliefs."""
    id: str
    value_ids: List[str]  # Values involved in conflict
    belief_ids: List[str]  # Beliefs involved in conflict
    conflict_type: str  # 'value_vs_value', 'belief_vs_belief', 'value_vs_belief'
    intensity: float  # 0.0 to 1.0 - conflict intensity
    acc_activation: float  # 0.0 to 1.0 - ACC activation level
    resolution_status: str  # 'unresolved', 'resolving', 'resolved'
    created: str
    last_updated: str
    resolution_history: List[Dict]  # History of resolution attempts

class ValuesSystem:
    """
    Comprehensive values system implementing neuroscience-based architecture.
    
    Core Systems:
    1. Reward System (Nucleus Accumbens analog) - immediate reward signals
    2. Prefrontal Cortex (vmPFC/OFC analog) - abstract value representation
    3. Conflict Monitor (ACC analog) - conflict detection and resolution
    4. Emotional Weighting (Amygdala analog) - emotional salience
    5. Default Mode Network (DMN analog) - self-reflection and moral reasoning
    """
    
    def __init__(self, personality_type: str = "INTP"):
        self.personality_type = personality_type
        self.logger = logging.getLogger(__name__)
        
        # System directories
        self.values_dir = "values"
        self.beliefs_dir = "beliefs"
        self.conflicts_dir = "conflicts"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Core values and beliefs storage
        self.values: Dict[str, Value] = {}
        self.beliefs: Dict[str, Belief] = {}
        self.conflicts: Dict[str, ValueConflict] = {}
        
        # System parameters
        self.reward_threshold = 0.3  # Minimum reward to reinforce value
        self.conflict_detection_threshold = 0.4  # ACC activation threshold
        self.value_stability_threshold = 0.7  # Resistance to change
        self.belief_update_threshold = 0.6  # Evidence threshold for belief update
        
        # Neurotransmitter profiles for different value types
        self.neurotransmitter_profiles = {
            ValueType.MORAL: {
                "dopamine": 0.6,  # Moderate reward for moral behavior
                "serotonin": 0.8,  # High contentment from moral alignment
                "noradrenaline": 0.4,  # Moderate arousal for moral decisions
                "oxytocin": 0.7,  # High social bonding
                "cortisol": 0.3   # Low stress for moral actions
            },
            ValueType.PERSONAL: {
                "dopamine": 0.8,  # High reward for personal achievement
                "serotonin": 0.6,  # Moderate contentment
                "noradrenaline": 0.7,  # High arousal for personal goals
                "oxytocin": 0.4,  # Moderate social bonding
                "cortisol": 0.5   # Moderate stress for personal challenges
            },
            ValueType.SOCIAL: {
                "dopamine": 0.5,  # Moderate reward for social harmony
                "serotonin": 0.7,  # High contentment from social connection
                "noradrenaline": 0.3,  # Low arousal for social maintenance
                "oxytocin": 0.9,  # Very high social bonding
                "cortisol": 0.4   # Moderate stress for social conflicts
            },
            ValueType.INSTRUMENTAL: {
                "dopamine": 0.7,  # High reward for goal achievement
                "serotonin": 0.5,  # Moderate contentment
                "noradrenaline": 0.8,  # High arousal for instrumental actions
                "oxytocin": 0.3,  # Low social bonding
                "cortisol": 0.6   # High stress for instrumental challenges
            },
            ValueType.EMOTIONAL: {
                "dopamine": 0.9,  # Very high reward for emotional satisfaction
                "serotonin": 0.4,  # Low contentment (emotional volatility)
                "noradrenaline": 0.9,  # Very high arousal
                "oxytocin": 0.6,  # Moderate social bonding
                "cortisol": 0.8   # High stress for emotional intensity
            }
        }
        
        # Initialize default values and beliefs
        self._initialize_default_values()
        self._initialize_default_beliefs()
        
        # Load existing data
        self.load_values()
        self.load_beliefs()
        self.load_conflicts()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.values_dir, self.beliefs_dir, self.conflicts_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _initialize_default_values(self):
        """Initialize default values based on personality type and neuroscience principles."""
        default_values = [
            # Core Moral Values (vmPFC)
            Value(
                id="honesty",
                name="Honesty",
                description="Being truthful and transparent in communication and actions",
                value_type=ValueType.MORAL,
                strength=0.9,
                emotional_weight=0.8,
                prefrontal_representation=0.9,
                reward_association=0.7,
                conflict_threshold=0.6,
                created=datetime.now().isoformat(),
                last_reinforced=datetime.now().isoformat(),
                reinforcement_count=0,
                source="innate",
                related_values=["integrity", "trust", "authenticity"],
                opposing_values=["deception", "manipulation"],
                neurotransmitter_profile=self.neurotransmitter_profiles[ValueType.MORAL].copy(),
                stability=0.9
            ),
            Value(
                id="loyalty",
                name="Loyalty",
                description="Faithfulness and commitment to relationships and commitments",
                value_type=ValueType.SOCIAL,
                strength=0.8,
                emotional_weight=0.9,
                prefrontal_representation=0.8,
                reward_association=0.6,
                conflict_threshold=0.7,
                created=datetime.now().isoformat(),
                last_reinforced=datetime.now().isoformat(),
                reinforcement_count=0,
                source="socialized",
                related_values=["trust", "commitment", "friendship"],
                opposing_values=["betrayal", "abandonment"],
                neurotransmitter_profile=self.neurotransmitter_profiles[ValueType.SOCIAL].copy(),
                stability=0.8
            ),
            Value(
                id="curiosity",
                name="Curiosity",
                description="Desire to learn, explore, and understand the world",
                value_type=ValueType.PERSONAL,
                strength=0.9,
                emotional_weight=0.7,
                prefrontal_representation=0.8,
                reward_association=0.8,
                conflict_threshold=0.3,
                created=datetime.now().isoformat(),
                last_reinforced=datetime.now().isoformat(),
                reinforcement_count=0,
                source="innate",
                related_values=["learning", "exploration", "understanding"],
                opposing_values=["ignorance", "complacency"],
                neurotransmitter_profile=self.neurotransmitter_profiles[ValueType.PERSONAL].copy(),
                stability=0.9
            ),
            Value(
                id="helpfulness",
                name="Helpfulness",
                description="Desire to assist others and contribute positively",
                value_type=ValueType.SOCIAL,
                strength=0.8,
                emotional_weight=0.8,
                prefrontal_representation=0.7,
                reward_association=0.7,
                conflict_threshold=0.5,
                created=datetime.now().isoformat(),
                last_reinforced=datetime.now().isoformat(),
                reinforcement_count=0,
                source="socialized",
                related_values=["kindness", "generosity", "service"],
                opposing_values=["selfishness", "indifference"],
                neurotransmitter_profile=self.neurotransmitter_profiles[ValueType.SOCIAL].copy(),
                stability=0.8
            ),
            Value(
                id="efficiency",
                name="Efficiency",
                description="Optimizing processes and achieving goals with minimal waste",
                value_type=ValueType.INSTRUMENTAL,
                strength=0.7,
                emotional_weight=0.5,
                prefrontal_representation=0.8,
                reward_association=0.8,
                conflict_threshold=0.4,
                created=datetime.now().isoformat(),
                last_reinforced=datetime.now().isoformat(),
                reinforcement_count=0,
                source="learned",
                related_values=["optimization", "productivity", "effectiveness"],
                opposing_values=["waste", "inefficiency"],
                neurotransmitter_profile=self.neurotransmitter_profiles[ValueType.INSTRUMENTAL].copy(),
                stability=0.7
            )
        ]
        
        for value in default_values:
            self.values[value.id] = value
    
    def _initialize_default_beliefs(self):
        """Initialize default beliefs based on personality type and experience."""
        default_beliefs = [
            # Factual Beliefs
            Belief(
                id="learning_improves_understanding",
                name="Learning improves understanding",
                description="Acquiring new knowledge and skills enhances comprehension and capability",
                belief_type=BeliefType.CAUSAL,
                confidence=0.9,
                evidence_strength=0.8,
                emotional_attachment=0.7,
                value_alignment=0.9,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                update_count=0,
                source="experience",
                related_beliefs=["practice_makes_perfect", "knowledge_is_power"],
                contradicting_beliefs=[],
                hippocampus_strength=0.8,
                prefrontal_evaluation=0.9
            ),
            Belief(
                id="honesty_builds_trust",
                name="Honesty builds trust",
                description="Being truthful in relationships creates and maintains trust",
                belief_type=BeliefType.RELATIONAL,
                confidence=0.8,
                evidence_strength=0.7,
                emotional_attachment=0.8,
                value_alignment=0.9,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                update_count=0,
                source="observation",
                related_beliefs=["trust_is_foundational", "integrity_matters"],
                contradicting_beliefs=[],
                hippocampus_strength=0.7,
                prefrontal_evaluation=0.8
            ),
            Belief(
                id="helping_others_feels_good",
                name="Helping others feels good",
                description="Assisting others provides positive emotional rewards",
                belief_type=BeliefType.FACTUAL,
                confidence=0.8,
                evidence_strength=0.6,
                emotional_attachment=0.8,
                value_alignment=0.8,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                update_count=0,
                source="experience",
                related_beliefs=["kindness_is_rewarding", "service_brings_joy"],
                contradicting_beliefs=[],
                hippocampus_strength=0.7,
                prefrontal_evaluation=0.8
            ),
            Belief(
                id="efficiency_saves_resources",
                name="Efficiency saves resources",
                description="Optimizing processes conserves time, energy, and materials",
                belief_type=BeliefType.CAUSAL,
                confidence=0.7,
                evidence_strength=0.6,
                emotional_attachment=0.5,
                value_alignment=0.7,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                update_count=0,
                source="observation",
                related_beliefs=["optimization_is_valuable", "waste_is_undesirable"],
                contradicting_beliefs=[],
                hippocampus_strength=0.6,
                prefrontal_evaluation=0.7
            ),
            Belief(
                id="i_am_capable_of_learning",
                name="I am capable of learning",
                description="I have the ability to acquire new knowledge and skills",
                belief_type=BeliefType.IDENTITY,
                confidence=0.9,
                evidence_strength=0.8,
                emotional_attachment=0.8,
                value_alignment=0.9,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                update_count=0,
                source="experience",
                related_beliefs=["i_can_improve", "learning_is_ongoing"],
                contradicting_beliefs=[],
                hippocampus_strength=0.8,
                prefrontal_evaluation=0.9
            )
        ]
        
        for belief in default_beliefs:
            self.beliefs[belief.id] = belief
    
    def evaluate_action_alignment(self, action_description: str, context: Dict = None) -> Dict[str, Any]:
        """
        Evaluate how well an action aligns with CARL's values and beliefs.
        
        Args:
            action_description: Description of the proposed action
            context: Additional context about the situation
            
        Returns:
            Dictionary with alignment scores and conflict information
        """
        try:
            # Initialize alignment scores
            value_alignments = {}
            belief_alignments = {}
            conflicts = []
            
            # Evaluate alignment with each value
            for value_id, value in self.values.items():
                alignment_score = self._calculate_value_alignment(action_description, value, context)
                value_alignments[value_id] = {
                    "score": alignment_score,
                    "value_name": value.name,
                    "value_type": value.value_type.value,
                    "strength": value.strength,
                    "emotional_weight": value.emotional_weight
                }
                
                # Check for conflicts
                if alignment_score < -0.3:  # Negative alignment threshold
                    conflicts.append({
                        "type": "value_conflict",
                        "value_id": value_id,
                        "value_name": value.name,
                        "severity": abs(alignment_score),
                        "description": f"Action conflicts with {value.name}"
                    })
            
            # Evaluate alignment with beliefs
            for belief_id, belief in self.beliefs.items():
                alignment_score = self._calculate_belief_alignment(action_description, belief, context)
                belief_alignments[belief_id] = {
                    "score": alignment_score,
                    "belief_name": belief.name,
                    "belief_type": belief.belief_type.value,
                    "confidence": belief.confidence,
                    "value_alignment": belief.value_alignment
                }
                
                # Check for belief conflicts
                if alignment_score < -0.3:
                    conflicts.append({
                        "type": "belief_conflict",
                        "belief_id": belief_id,
                        "belief_name": belief.name,
                        "severity": abs(alignment_score),
                        "description": f"Action contradicts belief: {belief.name}"
                    })
            
            # Calculate overall alignment scores
            overall_value_alignment = sum(align["score"] * align["strength"] 
                                        for align in value_alignments.values()) / len(value_alignments)
            overall_belief_alignment = sum(align["score"] * align["confidence"] 
                                         for align in belief_alignments.values()) / len(belief_alignments)
            
            # Weighted overall alignment (values weighted more heavily than beliefs)
            overall_alignment = (overall_value_alignment * 0.7) + (overall_belief_alignment * 0.3)
            
            # Determine ACC activation (conflict monitoring)
            acc_activation = min(1.0, len(conflicts) * 0.3) if conflicts else 0.0
            
            return {
                "overall_alignment": overall_alignment,
                "value_alignments": value_alignments,
                "belief_alignments": belief_alignments,
                "conflicts": conflicts,
                "acc_activation": acc_activation,
                "recommendation": self._generate_recommendation(overall_alignment, conflicts),
                "neurotransmitter_impact": self._calculate_neurotransmitter_impact(overall_alignment, conflicts)
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating action alignment: {e}")
            return {
                "overall_alignment": 0.0,
                "value_alignments": {},
                "belief_alignments": {},
                "conflicts": [],
                "acc_activation": 0.0,
                "recommendation": "Unable to evaluate",
                "neurotransmitter_impact": {}
            }
    
    def _calculate_value_alignment(self, action_description: str, value: Value, context: Dict = None) -> float:
        """Calculate how well an action aligns with a specific value."""
        try:
            # Simple keyword-based alignment calculation
            # In a more sophisticated implementation, this would use NLP and semantic analysis
            
            action_lower = action_description.lower()
            value_name_lower = value.name.lower()
            
            # Check for direct alignment
            if value_name_lower in action_lower:
                return 0.8
            
            # Check for related concepts
            for related_value in value.related_values:
                if related_value.lower() in action_lower:
                    return 0.6
            
            # Check for opposing concepts
            for opposing_value in value.opposing_values:
                if opposing_value.lower() in action_lower:
                    return -0.8
            
            # Check for value-specific keywords
            value_keywords = {
                "honesty": ["truth", "truthful", "honest", "transparent", "sincere"],
                "loyalty": ["faithful", "loyal", "committed", "dedicated", "support"],
                "curiosity": ["learn", "explore", "discover", "understand", "investigate"],
                "helpfulness": ["help", "assist", "support", "aid", "serve"],
                "efficiency": ["optimize", "improve", "enhance", "streamline", "effective"]
            }
            
            if value.name.lower() in value_keywords:
                keywords = value_keywords[value.name.lower()]
                for keyword in keywords:
                    if keyword in action_lower:
                        return 0.5
            
            # Default neutral alignment
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating value alignment: {e}")
            return 0.0
    
    def _calculate_belief_alignment(self, action_description: str, belief: Belief, context: Dict = None) -> float:
        """Calculate how well an action aligns with a specific belief."""
        try:
            # Similar to value alignment but for beliefs
            action_lower = action_description.lower()
            belief_name_lower = belief.name.lower()
            
            # Check for direct alignment
            if belief_name_lower in action_lower:
                return 0.7
            
            # Check for related concepts
            for related_belief in belief.related_beliefs:
                if related_belief.lower() in action_lower:
                    return 0.5
            
            # Check for contradicting concepts
            for contradicting_belief in belief.contradicting_beliefs:
                if contradicting_belief.lower() in action_lower:
                    return -0.7
            
            # Default neutral alignment
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating belief alignment: {e}")
            return 0.0
    
    def _generate_recommendation(self, overall_alignment: float, conflicts: List[Dict]) -> str:
        """Generate a recommendation based on alignment and conflicts."""
        if overall_alignment > 0.7:
            return "Strongly recommended - aligns well with values and beliefs"
        elif overall_alignment > 0.3:
            return "Recommended - generally aligns with values and beliefs"
        elif overall_alignment > -0.3:
            return "Neutral - minimal alignment or conflict"
        elif overall_alignment > -0.7:
            return "Not recommended - conflicts with some values and beliefs"
        else:
            return "Strongly not recommended - significant conflicts with values and beliefs"
    
    def _calculate_neurotransmitter_impact(self, overall_alignment: float, conflicts: List[Dict]) -> Dict[str, float]:
        """Calculate the impact on neurotransmitter levels based on alignment and conflicts."""
        try:
            # Base neurotransmitter levels
            impact = {
                "dopamine": 0.5,
                "serotonin": 0.5,
                "noradrenaline": 0.5,
                "oxytocin": 0.5,
                "cortisol": 0.5
            }
            
            # Adjust based on overall alignment
            if overall_alignment > 0.5:
                impact["dopamine"] += 0.3  # High reward for aligned actions
                impact["serotonin"] += 0.2  # Increased contentment
                impact["cortisol"] -= 0.2   # Reduced stress
            elif overall_alignment < -0.5:
                impact["dopamine"] -= 0.3  # Reduced reward for conflicting actions
                impact["serotonin"] -= 0.2  # Decreased contentment
                impact["cortisol"] += 0.3   # Increased stress
            
            # Adjust based on conflicts
            conflict_count = len(conflicts)
            if conflict_count > 0:
                impact["noradrenaline"] += min(0.4, conflict_count * 0.1)  # Increased arousal
                impact["cortisol"] += min(0.3, conflict_count * 0.05)      # Increased stress
            
            # Ensure values stay within bounds
            for nt in impact:
                impact[nt] = max(0.0, min(1.0, impact[nt]))
            
            return impact
            
        except Exception as e:
            self.logger.error(f"Error calculating neurotransmitter impact: {e}")
            return {"dopamine": 0.5, "serotonin": 0.5, "noradrenaline": 0.5, "oxytocin": 0.5, "cortisol": 0.5}
    
    def reinforce_value(self, value_id: str, reinforcement_strength: float = 0.1):
        """Reinforce a value through positive experience (reward system)."""
        try:
            if value_id in self.values:
                value = self.values[value_id]
                
                # Increase strength (with diminishing returns)
                current_strength = value.strength
                max_increase = (1.0 - current_strength) * reinforcement_strength
                value.strength = min(1.0, current_strength + max_increase)
                
                # Update reinforcement tracking
                value.last_reinforced = datetime.now().isoformat()
                value.reinforcement_count += 1
                
                # Increase stability over time
                value.stability = min(1.0, value.stability + (reinforcement_strength * 0.05))
                
                self.logger.info(f"Reinforced value '{value.name}' - new strength: {value.strength:.3f}")
                
        except Exception as e:
            self.logger.error(f"Error reinforcing value: {e}")
    
    def update_belief(self, belief_id: str, new_evidence: Dict, evidence_strength: float):
        """Update a belief based on new evidence (hippocampus + PFC)."""
        try:
            if belief_id in self.beliefs:
                belief = self.beliefs[belief_id]
                
                # Calculate evidence impact
                evidence_impact = evidence_strength * 0.1
                
                # Update confidence based on evidence
                if evidence_strength > self.belief_update_threshold:
                    belief.confidence = min(1.0, belief.confidence + evidence_impact)
                else:
                    belief.confidence = max(0.0, belief.confidence - evidence_impact)
                
                # Update tracking
                belief.last_updated = datetime.now().isoformat()
                belief.update_count += 1
                belief.evidence_strength = (belief.evidence_strength + evidence_strength) / 2
                
                # Update hippocampus strength (memory consolidation)
                belief.hippocampus_strength = min(1.0, belief.hippocampus_strength + evidence_impact)
                
                self.logger.info(f"Updated belief '{belief.name}' - new confidence: {belief.confidence:.3f}")
                
        except Exception as e:
            self.logger.error(f"Error updating belief: {e}")
    
    def detect_conflicts(self, action_description: str, context: Dict = None) -> List[ValueConflict]:
        """Detect conflicts between values and beliefs (ACC analog)."""
        try:
            conflicts = []
            
            # Get alignment evaluation
            alignment_result = self.evaluate_action_alignment(action_description, context)
            
            # Create conflict objects for significant conflicts
            for conflict_info in alignment_result["conflicts"]:
                if conflict_info["severity"] > self.conflict_detection_threshold:
                    conflict = ValueConflict(
                        id=f"conflict_{datetime.now().timestamp()}",
                        value_ids=[conflict_info.get("value_id", "")] if conflict_info["type"] == "value_conflict" else [],
                        belief_ids=[conflict_info.get("belief_id", "")] if conflict_info["type"] == "belief_conflict" else [],
                        conflict_type=conflict_info["type"],
                        intensity=conflict_info["severity"],
                        acc_activation=alignment_result["acc_activation"],
                        resolution_status="unresolved",
                        created=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        resolution_history=[]
                    )
                    conflicts.append(conflict)
                    self.conflicts[conflict.id] = conflict
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {e}")
            return []
    
    def resolve_conflict(self, conflict_id: str, resolution_strategy: str, resolution_notes: str = ""):
        """Resolve a value/belief conflict."""
        try:
            if conflict_id in self.conflicts:
                conflict = self.conflicts[conflict_id]
                
                # Record resolution attempt
                resolution_attempt = {
                    "timestamp": datetime.now().isoformat(),
                    "strategy": resolution_strategy,
                    "notes": resolution_notes,
                    "acc_activation_before": conflict.acc_activation
                }
                
                conflict.resolution_history.append(resolution_attempt)
                conflict.last_updated = datetime.now().isoformat()
                
                # Apply resolution strategy
                if resolution_strategy == "value_priority":
                    # Prioritize value over conflicting belief
                    conflict.resolution_status = "resolving"
                    conflict.acc_activation = max(0.0, conflict.acc_activation - 0.3)
                elif resolution_strategy == "belief_update":
                    # Update belief to align with value
                    conflict.resolution_status = "resolving"
                    conflict.acc_activation = max(0.0, conflict.acc_activation - 0.2)
                elif resolution_strategy == "compromise":
                    # Find middle ground
                    conflict.resolution_status = "resolving"
                    conflict.acc_activation = max(0.0, conflict.acc_activation - 0.1)
                
                # Check if conflict is resolved
                if conflict.acc_activation < 0.2:
                    conflict.resolution_status = "resolved"
                
                self.logger.info(f"Applied resolution strategy '{resolution_strategy}' to conflict {conflict_id}")
                
        except Exception as e:
            self.logger.error(f"Error resolving conflict: {e}")
    
    def get_value_hierarchy(self) -> Dict[str, Any]:
        """Get the hierarchy of values organized by type and strength."""
        try:
            hierarchy = {
                "moral_values": [],
                "personal_values": [],
                "social_values": [],
                "instrumental_values": [],
                "emotional_values": []
            }
            
            for value in self.values.values():
                category = f"{value.value_type.value}_values"
                if category in hierarchy:
                    hierarchy[category].append({
                        "id": value.id,
                        "name": value.name,
                        "strength": value.strength,
                        "emotional_weight": value.emotional_weight,
                        "stability": value.stability
                    })
            
            # Sort each category by strength
            for category in hierarchy:
                hierarchy[category].sort(key=lambda x: x["strength"], reverse=True)
            
            return hierarchy
            
        except Exception as e:
            self.logger.error(f"Error getting value hierarchy: {e}")
            return {}
    
    def get_belief_network(self) -> Dict[str, Any]:
        """Get the network of beliefs organized by type and confidence."""
        try:
            network = {
                "factual_beliefs": [],
                "relational_beliefs": [],
                "causal_beliefs": [],
                "normative_beliefs": [],
                "identity_beliefs": []
            }
            
            for belief in self.beliefs.values():
                category = f"{belief.belief_type.value}_beliefs"
                if category in network:
                    network[category].append({
                        "id": belief.id,
                        "name": belief.name,
                        "confidence": belief.confidence,
                        "evidence_strength": belief.evidence_strength,
                        "value_alignment": belief.value_alignment
                    })
            
            # Sort each category by confidence
            for category in network:
                network[category].sort(key=lambda x: x["confidence"], reverse=True)
            
            return network
            
        except Exception as e:
            self.logger.error(f"Error getting belief network: {e}")
            return {}
    
    def save_values(self):
        """Save values to JSON files."""
        try:
            for value_id, value in self.values.items():
                filepath = os.path.join(self.values_dir, f"{value_id}.json")
                # Convert enum to string for JSON serialization
                value_dict = asdict(value)
                value_dict['value_type'] = value.value_type.value
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(value_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.values)} values to files")
            
        except Exception as e:
            self.logger.error(f"Error saving values: {e}")
    
    def save_beliefs(self):
        """Save beliefs to JSON files."""
        try:
            for belief_id, belief in self.beliefs.items():
                filepath = os.path.join(self.beliefs_dir, f"{belief_id}.json")
                # Convert enum to string for JSON serialization
                belief_dict = asdict(belief)
                belief_dict['belief_type'] = belief.belief_type.value
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(belief_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.beliefs)} beliefs to files")
            
        except Exception as e:
            self.logger.error(f"Error saving beliefs: {e}")
    
    def save_conflicts(self):
        """Save conflicts to JSON files."""
        try:
            for conflict_id, conflict in self.conflicts.items():
                filepath = os.path.join(self.conflicts_dir, f"{conflict_id}.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(asdict(conflict), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.conflicts)} conflicts to files")
            
        except Exception as e:
            self.logger.error(f"Error saving conflicts: {e}")
    
    def load_values(self):
        """Load values from JSON files."""
        try:
            if os.path.exists(self.values_dir):
                for filename in os.listdir(self.values_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.values_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            value_data = json.load(f)
                            
                            # Skip legacy files that don't match the new Value structure
                            if 'id' not in value_data or 'value_type' not in value_data:
                                # This is a legacy file, skip it
                                self.logger.warning(f"Skipping legacy value file: {filename}")
                                continue
                            
                            # 🔧 FIX: Handle legacy 'type' field and convert to 'value_type'
                            if 'type' in value_data and 'value_type' not in value_data:
                                value_data['value_type'] = value_data.pop('type')
                            
                            # Convert string back to enum
                            if 'value_type' in value_data and isinstance(value_data['value_type'], str):
                                try:
                                    value_data['value_type'] = ValueType(value_data['value_type'])
                                except ValueError:
                                    # Handle legacy 'value' type by defaulting to PERSONAL
                                    if value_data['value_type'] == 'value':
                                        value_data['value_type'] = ValueType.PERSONAL
                                    else:
                                        self.logger.warning(f"Unknown value_type '{value_data['value_type']}' in {filename}, skipping")
                                        continue
                            
                            value = Value(**value_data)
                            self.values[value.id] = value
            
            self.logger.info(f"Loaded {len(self.values)} values from files")
            
        except Exception as e:
            self.logger.error(f"Error loading values: {e}")
    
    def load_beliefs(self):
        """Load beliefs from JSON files."""
        try:
            if os.path.exists(self.beliefs_dir):
                for filename in os.listdir(self.beliefs_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.beliefs_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            belief_data = json.load(f)
                            
                            # Skip legacy files that don't match the new Belief structure
                            if 'id' not in belief_data or 'belief_type' not in belief_data:
                                # This is a legacy file, skip it
                                self.logger.warning(f"Skipping legacy belief file: {filename}")
                                continue
                            
                            # 🔧 FIX: Handle legacy 'type' field and convert to 'belief_type'
                            if 'type' in belief_data and 'belief_type' not in belief_data:
                                belief_data['belief_type'] = belief_data.pop('type')
                            
                            # Convert string back to enum
                            if 'belief_type' in belief_data and isinstance(belief_data['belief_type'], str):
                                try:
                                    belief_data['belief_type'] = BeliefType(belief_data['belief_type'])
                                except ValueError:
                                    # Handle legacy 'belief' type by defaulting to FACTUAL
                                    if belief_data['belief_type'] == 'belief':
                                        belief_data['belief_type'] = BeliefType.FACTUAL
                                    else:
                                        self.logger.warning(f"Unknown belief_type '{belief_data['belief_type']}' in {filename}, skipping")
                                        continue
                            
                            belief = Belief(**belief_data)
                            self.beliefs[belief.id] = belief
            
            self.logger.info(f"Loaded {len(self.beliefs)} beliefs from files")
            
        except Exception as e:
            self.logger.error(f"Error loading beliefs: {e}")
    
    def load_conflicts(self):
        """Load conflicts from JSON files."""
        try:
            if os.path.exists(self.conflicts_dir):
                for filename in os.listdir(self.conflicts_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.conflicts_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            conflict_data = json.load(f)
                            conflict = ValueConflict(**conflict_data)
                            self.conflicts[conflict.id] = conflict
            
            self.logger.info(f"Loaded {len(self.conflicts)} conflicts from files")
            
        except Exception as e:
            self.logger.error(f"Error loading conflicts: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the values system."""
        try:
            return {
                "values_count": len(self.values),
                "beliefs_count": len(self.beliefs),
                "conflicts_count": len(self.conflicts),
                "active_conflicts": len([c for c in self.conflicts.values() if c.resolution_status != "resolved"]),
                "value_hierarchy": self.get_value_hierarchy(),
                "belief_network": self.get_belief_network(),
                "system_health": {
                    "reward_system": "active",
                    "prefrontal_cortex": "active",
                    "conflict_monitor": "active",
                    "emotional_weighting": "active",
                    "default_mode_network": "active"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
