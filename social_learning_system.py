#!/usr/bin/env python3
"""
Social Learning System for CARL
Implements social learning with cultural value integration, social norm adaptation,
and inner dialogue influenced by social interactions.

Based on:
- Social Learning Theory (Bandura)
- Cultural Learning Theory
- Social Cognitive Theory
- Theory of Mind
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from enum import Enum

class SocialLearningType(Enum):
    """Types of social learning processes."""
    OBSERVATIONAL = "observational"  # Learning by watching others
    IMITATIVE = "imitative"         # Copying behaviors
    NORMATIVE = "normative"         # Learning social norms
    CULTURAL = "cultural"           # Learning cultural values
    COLLABORATIVE = "collaborative"  # Learning through interaction

class SocialContext(Enum):
    """Social contexts for learning."""
    FAMILY = "family"
    FRIENDS = "friends"
    WORK = "work"
    COMMUNITY = "community"
    CULTURAL = "cultural"
    ONLINE = "online"

@dataclass
class SocialInteraction:
    """Represents a social interaction for learning."""
    interaction_id: str
    timestamp: str
    participants: List[str]
    context: SocialContext
    interaction_type: str
    content: str
    emotional_tone: Dict[str, float]
    cultural_values_observed: List[str]
    social_norms_observed: List[str]
    learning_opportunities: List[str]
    influence_level: float  # 0.0 to 1.0
    trust_level: float      # 0.0 to 1.0

@dataclass
class CulturalValue:
    """Represents a cultural value learned through social interaction."""
    value_id: str
    name: str
    description: str
    source_interaction: str
    cultural_context: str
    strength: float  # 0.0 to 1.0
    learned_from: List[str]  # People who demonstrated this value
    examples: List[str]     # Examples of this value in action
    conflicts_with: List[str]  # Values that conflict with this one
    timestamp: str

@dataclass
class SocialNorm:
    """Represents a social norm learned through observation."""
    norm_id: str
    name: str
    description: str
    context: SocialContext
    source_interaction: str
    strength: float  # 0.0 to 1.0
    learned_from: List[str]
    examples: List[str]
    violations_observed: List[str]
    adherence_level: float  # How well CARL follows this norm
    timestamp: str

@dataclass
class SocialLearningEpisode:
    """Represents a complete social learning episode."""
    episode_id: str
    timestamp: str
    learning_type: SocialLearningType
    social_context: SocialContext
    participants: List[str]
    content: str
    values_learned: List[CulturalValue]
    norms_learned: List[SocialNorm]
    behaviors_observed: List[str]
    emotional_impact: Dict[str, float]
    influence_on_inner_dialogue: str
    cultural_adaptations: List[str]
    confidence: float

class SocialLearningSystem:
    """
    Social learning system implementing cultural value integration and social norm adaptation.
    
    Core Functions:
    1. Social Interaction Analysis - Analyze social interactions for learning opportunities
    2. Cultural Value Integration - Learn and integrate cultural values from social interactions
    3. Social Norm Adaptation - Learn and adapt to social norms
    4. Inner Dialogue Influence - Influence inner dialogue based on social learning
    5. Collaborative Learning - Learn through collaborative interactions
    """
    
    def __init__(self, values_system, memory_system, inner_world_system):
        """
        Initialize the social learning system.
        
        Args:
            values_system: CARL's values system for cultural value integration
            memory_system: CARL's memory system for storing social learning
            inner_world_system: CARL's inner world system for dialogue influence
        """
        self.values_system = values_system
        self.memory_system = memory_system
        self.inner_world_system = inner_world_system
        self.logger = logging.getLogger(__name__)
        
        # System directories
        self.social_learning_dir = "social_learning"
        self.cultural_values_dir = "social_learning/cultural_values"
        self.social_norms_dir = "social_learning/social_norms"
        self.interactions_dir = "social_learning/interactions"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Social learning storage
        self.social_interactions: Dict[str, SocialInteraction] = {}
        self.cultural_values: Dict[str, CulturalValue] = {}
        self.social_norms: Dict[str, SocialNorm] = {}
        self.learning_episodes: Dict[str, SocialLearningEpisode] = {}
        
        # Learning parameters
        self.learning_threshold = 0.3  # Minimum influence to trigger learning
        self.trust_threshold = 0.5     # Minimum trust to learn from someone
        self.cultural_adaptation_rate = 0.1  # Rate of cultural adaptation
        self.norm_adherence_rate = 0.2      # Rate of norm adherence improvement
        
        # Social learning statistics
        self.stats = {
            "total_interactions": 0,
            "values_learned": 0,
            "norms_learned": 0,
            "cultural_adaptations": 0,
            "collaborative_learning_episodes": 0
        }
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.social_learning_dir,
            self.cultural_values_dir,
            self.social_norms_dir,
            self.interactions_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"📁 Created directory: {directory}")
    
    def process_social_interaction(self, interaction_data: Dict[str, Any]) -> SocialLearningEpisode:
        """
        Process a social interaction for learning opportunities.
        
        Args:
            interaction_data: Dictionary containing interaction information
            
        Returns:
            SocialLearningEpisode: Complete learning episode
        """
        try:
            self.logger.info(f"🤝 Processing social interaction: {interaction_data.get('type', 'unknown')}")
            
            # Create social interaction object
            interaction = self._create_social_interaction(interaction_data)
            
            # Analyze for learning opportunities
            learning_opportunities = self._analyze_learning_opportunities(interaction)
            
            # Extract cultural values
            cultural_values = self._extract_cultural_values(interaction, learning_opportunities)
            
            # Extract social norms
            social_norms = self._extract_social_norms(interaction, learning_opportunities)
            
            # Determine learning type
            learning_type = self._determine_learning_type(interaction, learning_opportunities)
            
            # Create learning episode
            episode = SocialLearningEpisode(
                episode_id=f"sl_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                learning_type=learning_type,
                social_context=interaction.context,
                participants=interaction.participants,
                content=interaction.content,
                values_learned=cultural_values,
                norms_learned=social_norms,
                behaviors_observed=learning_opportunities.get("behaviors", []),
                emotional_impact=interaction.emotional_tone,
                influence_on_inner_dialogue=self._generate_inner_dialogue_influence(interaction, cultural_values, social_norms),
                cultural_adaptations=self._generate_cultural_adaptations(cultural_values, social_norms),
                confidence=self._calculate_learning_confidence(interaction, cultural_values, social_norms)
            )
            
            # Store learning episode
            self.learning_episodes[episode.episode_id] = episode
            self._store_learning_episode(episode)
            
            # Update statistics
            self.stats["total_interactions"] += 1
            self.stats["values_learned"] += len(cultural_values)
            self.stats["norms_learned"] += len(social_norms)
            self.stats["cultural_adaptations"] += len(episode.cultural_adaptations)
            
            # Integrate with values system
            self._integrate_with_values_system(cultural_values)
            
            # Influence inner world system
            self._influence_inner_world_system(episode)
            
            self.logger.info(f"✅ Social learning episode {episode.episode_id} processed successfully")
            return episode
            
        except Exception as e:
            self.logger.error(f"❌ Error processing social interaction: {e}")
            return self._create_fallback_episode(interaction_data)
    
    def _create_social_interaction(self, interaction_data: Dict[str, Any]) -> SocialInteraction:
        """Create a SocialInteraction object from interaction data."""
        try:
            return SocialInteraction(
                interaction_id=f"si_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                participants=interaction_data.get("participants", []),
                context=SocialContext(interaction_data.get("context", "community")),
                interaction_type=interaction_data.get("type", "conversation"),
                content=interaction_data.get("content", ""),
                emotional_tone=interaction_data.get("emotional_tone", {}),
                cultural_values_observed=interaction_data.get("cultural_values", []),
                social_norms_observed=interaction_data.get("social_norms", []),
                learning_opportunities=interaction_data.get("learning_opportunities", []),
                influence_level=interaction_data.get("influence_level", 0.5),
                trust_level=interaction_data.get("trust_level", 0.5)
            )
        except Exception as e:
            self.logger.error(f"❌ Error creating social interaction: {e}")
            return SocialInteraction(
                interaction_id=f"si_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                participants=[],
                context=SocialContext.COMMUNITY,
                interaction_type="unknown",
                content="",
                emotional_tone={},
                cultural_values_observed=[],
                social_norms_observed=[],
                learning_opportunities=[],
                influence_level=0.0,
                trust_level=0.0
            )
    
    def _analyze_learning_opportunities(self, interaction: SocialInteraction) -> Dict[str, Any]:
        """Analyze social interaction for learning opportunities."""
        try:
            opportunities = {
                "cultural_values": [],
                "social_norms": [],
                "behaviors": [],
                "emotional_patterns": [],
                "communication_styles": []
            }
            
            # Analyze content for cultural values
            content_lower = interaction.content.lower()
            
            # Cultural value indicators
            value_indicators = {
                "respect": ["respect", "honor", "dignity", "courtesy"],
                "honesty": ["honest", "truth", "transparent", "sincere"],
                "kindness": ["kind", "compassionate", "caring", "gentle"],
                "fairness": ["fair", "just", "equal", "impartial"],
                "loyalty": ["loyal", "faithful", "devoted", "committed"],
                "responsibility": ["responsible", "accountable", "duty", "obligation"]
            }
            
            for value, indicators in value_indicators.items():
                if any(indicator in content_lower for indicator in indicators):
                    opportunities["cultural_values"].append(value)
            
            # Social norm indicators
            norm_indicators = {
                "politeness": ["please", "thank you", "excuse me", "sorry"],
                "turn_taking": ["your turn", "my turn", "wait", "interrupt"],
                "listening": ["listen", "hear", "understand", "pay attention"],
                "sharing": ["share", "together", "collaborate", "help"],
                "boundaries": ["personal space", "privacy", "respect", "boundaries"]
            }
            
            for norm, indicators in norm_indicators.items():
                if any(indicator in content_lower for indicator in indicators):
                    opportunities["social_norms"].append(norm)
            
            # Behavioral observations
            behavior_indicators = [
                "gesture", "expression", "tone", "posture", "eye contact",
                "smile", "nod", "wave", "hug", "handshake"
            ]
            
            for indicator in behavior_indicators:
                if indicator in content_lower:
                    opportunities["behaviors"].append(indicator)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing learning opportunities: {e}")
            return {"cultural_values": [], "social_norms": [], "behaviors": []}
    
    def _extract_cultural_values(self, interaction: SocialInteraction, opportunities: Dict[str, Any]) -> List[CulturalValue]:
        """Extract cultural values from social interaction."""
        try:
            cultural_values = []
            
            for value_name in opportunities.get("cultural_values", []):
                # Check if this value conflicts with existing values
                conflicts = self._find_value_conflicts(value_name)
                
                # Create cultural value
                cultural_value = CulturalValue(
                    value_id=f"cv_{int(time.time())}_{value_name}",
                    name=value_name,
                    description=f"Cultural value of {value_name} observed in social interaction",
                    source_interaction=interaction.interaction_id,
                    cultural_context=interaction.context.value,
                    strength=interaction.influence_level,
                    learned_from=interaction.participants,
                    examples=[interaction.content[:100] + "..."],
                    conflicts_with=conflicts,
                    timestamp=datetime.now().isoformat()
                )
                
                cultural_values.append(cultural_value)
                self.cultural_values[cultural_value.value_id] = cultural_value
            
            return cultural_values
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting cultural values: {e}")
            return []
    
    def _extract_social_norms(self, interaction: SocialInteraction, opportunities: Dict[str, Any]) -> List[SocialNorm]:
        """Extract social norms from social interaction."""
        try:
            social_norms = []
            
            for norm_name in opportunities.get("social_norms", []):
                # Create social norm
                social_norm = SocialNorm(
                    norm_id=f"sn_{int(time.time())}_{norm_name}",
                    name=norm_name,
                    description=f"Social norm of {norm_name} observed in interaction",
                    context=interaction.context,
                    source_interaction=interaction.interaction_id,
                    strength=interaction.influence_level,
                    learned_from=interaction.participants,
                    examples=[interaction.content[:100] + "..."],
                    violations_observed=[],
                    adherence_level=0.5,  # Initial adherence level
                    timestamp=datetime.now().isoformat()
                )
                
                social_norms.append(social_norm)
                self.social_norms[social_norm.norm_id] = social_norm
            
            return social_norms
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting social norms: {e}")
            return []
    
    def _determine_learning_type(self, interaction: SocialInteraction, opportunities: Dict[str, Any]) -> SocialLearningType:
        """Determine the type of social learning occurring."""
        try:
            # Check for collaborative indicators
            if any(word in interaction.content.lower() for word in ["together", "collaborate", "team", "group"]):
                return SocialLearningType.COLLABORATIVE
            
            # Check for imitative indicators
            if any(word in interaction.content.lower() for word in ["copy", "imitate", "follow", "example"]):
                return SocialLearningType.IMITATIVE
            
            # Check for normative indicators
            if any(word in interaction.content.lower() for word in ["should", "must", "expected", "normal"]):
                return SocialLearningType.NORMATIVE
            
            # Check for cultural indicators
            if any(word in interaction.content.lower() for word in ["culture", "tradition", "custom", "heritage"]):
                return SocialLearningType.CULTURAL
            
            # Default to observational
            return SocialLearningType.OBSERVATIONAL
            
        except Exception as e:
            self.logger.error(f"❌ Error determining learning type: {e}")
            return SocialLearningType.OBSERVATIONAL
    
    def _generate_inner_dialogue_influence(self, interaction: SocialInteraction, cultural_values: List[CulturalValue], social_norms: List[SocialNorm]) -> str:
        """Generate influence on inner dialogue based on social learning."""
        try:
            influences = []
            
            # Add cultural value influences
            for value in cultural_values:
                influences.append(f"I learned about {value.name} from {', '.join(interaction.participants)}")
            
            # Add social norm influences
            for norm in social_norms:
                influences.append(f"I observed the social norm of {norm.name} in this interaction")
            
            # Add emotional influences
            if interaction.emotional_tone:
                dominant_emotion = max(interaction.emotional_tone.keys(), key=lambda x: interaction.emotional_tone[x])
                influences.append(f"This interaction made me feel {dominant_emotion}")
            
            return ". ".join(influences) if influences else "No specific influences on inner dialogue"
            
        except Exception as e:
            self.logger.error(f"❌ Error generating inner dialogue influence: {e}")
            return "Error generating influence"
    
    def _generate_cultural_adaptations(self, cultural_values: List[CulturalValue], social_norms: List[SocialNorm]) -> List[str]:
        """Generate cultural adaptations based on learned values and norms."""
        try:
            adaptations = []
            
            # Generate adaptations for cultural values
            for value in cultural_values:
                adaptations.append(f"Adapt behavior to reflect {value.name} in future interactions")
            
            # Generate adaptations for social norms
            for norm in social_norms:
                adaptations.append(f"Follow {norm.name} norm in {norm.context.value} contexts")
            
            return adaptations
            
        except Exception as e:
            self.logger.error(f"❌ Error generating cultural adaptations: {e}")
            return []
    
    def _calculate_learning_confidence(self, interaction: SocialInteraction, cultural_values: List[CulturalValue], social_norms: List[SocialNorm]) -> float:
        """Calculate confidence in the learning episode."""
        try:
            base_confidence = 0.5
            
            # Adjust based on trust level
            base_confidence += interaction.trust_level * 0.3
            
            # Adjust based on influence level
            base_confidence += interaction.influence_level * 0.2
            
            # Adjust based on number of learning opportunities
            learning_count = len(cultural_values) + len(social_norms)
            base_confidence += min(learning_count * 0.1, 0.2)
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating learning confidence: {e}")
            return 0.5
    
    def _find_value_conflicts(self, value_name: str) -> List[str]:
        """Find values that might conflict with the given value."""
        try:
            # Simple conflict detection based on value names
            conflicts = []
            
            if value_name == "honesty":
                conflicts.extend(["politeness", "harmony"])  # Sometimes honesty conflicts with politeness
            elif value_name == "loyalty":
                conflicts.extend(["fairness", "impartiality"])  # Loyalty can conflict with fairness
            elif value_name == "individuality":
                conflicts.extend(["conformity", "tradition"])  # Individuality can conflict with conformity
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"❌ Error finding value conflicts: {e}")
            return []
    
    def _integrate_with_values_system(self, cultural_values: List[CulturalValue]):
        """Integrate learned cultural values with CARL's values system."""
        try:
            for cultural_value in cultural_values:
                # Create a value in the values system
                if hasattr(self.values_system, 'add_value'):
                    self.values_system.add_value(
                        name=cultural_value.name,
                        description=cultural_value.description,
                        value_type="social",  # Mark as socially learned
                        strength=cultural_value.strength,
                        source="social_learning"
                    )
            
            self.logger.info(f"✅ Integrated {len(cultural_values)} cultural values with values system")
            
        except Exception as e:
            self.logger.error(f"❌ Error integrating with values system: {e}")
    
    def _influence_inner_world_system(self, episode: SocialLearningEpisode):
        """Influence CARL's inner world system based on social learning."""
        try:
            if hasattr(self.inner_world_system, 'add_social_context'):
                # Add social context to inner world system
                social_context = {
                    "episode_id": episode.episode_id,
                    "participants": episode.participants,
                    "cultural_values": [v.name for v in episode.values_learned],
                    "social_norms": [n.name for n in episode.norms_learned],
                    "influence": episode.influence_on_inner_dialogue
                }
                
                self.inner_world_system.add_social_context(social_context)
            
            self.logger.info(f"✅ Influenced inner world system with social learning episode {episode.episode_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error influencing inner world system: {e}")
    
    def _store_learning_episode(self, episode: SocialLearningEpisode):
        """Store learning episode to disk."""
        try:
            episode_file = os.path.join(self.social_learning_dir, f"{episode.episode_id}.json")
            
            with open(episode_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(episode), f, indent=2)
            
            self.logger.info(f"💾 Stored learning episode: {episode_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error storing learning episode: {e}")
    
    def _create_fallback_episode(self, interaction_data: Dict[str, Any]) -> SocialLearningEpisode:
        """Create a fallback learning episode when processing fails."""
        try:
            return SocialLearningEpisode(
                episode_id=f"sl_fallback_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                learning_type=SocialLearningType.OBSERVATIONAL,
                social_context=SocialContext.COMMUNITY,
                participants=interaction_data.get("participants", []),
                content=interaction_data.get("content", ""),
                values_learned=[],
                norms_learned=[],
                behaviors_observed=[],
                emotional_impact={},
                influence_on_inner_dialogue="No specific influences detected",
                cultural_adaptations=[],
                confidence=0.1
            )
        except Exception as e:
            self.logger.error(f"❌ Error creating fallback episode: {e}")
            return SocialLearningEpisode(
                episode_id=f"sl_error_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                learning_type=SocialLearningType.OBSERVATIONAL,
                social_context=SocialContext.COMMUNITY,
                participants=[],
                content="",
                values_learned=[],
                norms_learned=[],
                behaviors_observed=[],
                emotional_impact={},
                influence_on_inner_dialogue="Error in processing",
                cultural_adaptations=[],
                confidence=0.0
            )
    
    def get_social_learning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent social learning episodes."""
        try:
            episodes = []
            if os.path.exists(self.social_learning_dir):
                files = [f for f in os.listdir(self.social_learning_dir) if f.endswith('.json')]
                files.sort(key=lambda x: os.path.getmtime(os.path.join(self.social_learning_dir, x)), reverse=True)
                
                for filename in files[:limit]:
                    filepath = os.path.join(self.social_learning_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        episode = json.load(f)
                        episodes.append(episode)
            
            return episodes
            
        except Exception as e:
            self.logger.error(f"❌ Error getting social learning history: {e}")
            return []
    
    def get_cultural_values_learned(self) -> List[Dict[str, Any]]:
        """Get all cultural values learned through social interactions."""
        try:
            return [asdict(value) for value in self.cultural_values.values()]
        except Exception as e:
            self.logger.error(f"❌ Error getting cultural values: {e}")
            return []
    
    def get_social_norms_learned(self) -> List[Dict[str, Any]]:
        """Get all social norms learned through social interactions."""
        try:
            return [asdict(norm) for norm in self.social_norms.values()]
        except Exception as e:
            self.logger.error(f"❌ Error getting social norms: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get social learning system statistics."""
        return {
            **self.stats,
            "cultural_values_count": len(self.cultural_values),
            "social_norms_count": len(self.social_norms),
            "learning_episodes_count": len(self.learning_episodes)
        }
