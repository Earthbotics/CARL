#!/usr/bin/env python3
"""
CARL's Imagination System

This system implements human-like imagination capabilities for CARL, following:
- Predictive Processing / Bayesian Brain models
- Constructive Episodic Simulation / Scene Construction
- Default Mode Network simulation
- Conceptual Blending theory
- NEUCOGAR mood-dependent imagery generation

The system enables CARL to:
1. Generate mental imagery for planning and exploration
2. Create visual representations of imagined scenarios
3. Store and retrieve imagined episodes as memories
4. Use imagination for goal-directed behavior
"""

import json
import os
import time
import requests
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from PIL import Image
import io
import hashlib

@dataclass
class ImaginationRequest:
    """Structured request for imagination generation."""
    seed: str
    purpose: str  # plan-social-interaction, explore-scenario, counterfactual, etc.
    mbti_state: Dict[str, float]  # Ti, Ne, Si, Fe values
    neucogar: Dict[str, float]  # DA, 5HT, NE values
    constraints: Optional[Dict[str, Any]] = None
    risk_budget: float = 0.3
    render: str = "image"  # image, schema, both
    timestamp: Optional[str] = None

@dataclass
class SceneGraph:
    """Structured scene representation for imagination."""
    objects: List[Dict[str, Any]]
    relations: List[Dict[str, str]]
    affect: Dict[str, float]  # valence, arousal, dominant emotion
    details: Dict[str, str]  # lighting, style, etc.
    context: Dict[str, Any]  # additional context

@dataclass
class ImaginationContext:
    """Context for imagination generation."""
    seed: str
    purpose: str
    mbti_state: Dict[str, float]
    neucogar_state: Dict[str, float]
    constraints: Optional[Dict[str, Any]] = None
    risk_budget: float = 0.3
    render_style: str = "hologram_3d"

@dataclass
class ImaginationArtifact:
    """Generated imagination artifact."""
    episode_id: str
    purpose: str
    seed: str
    scene_description: str
    render_style: str
    coherence_score: float
    plausibility_score: float
    novelty_score: float
    utility_score: float
    vividness_score: float
    affect_alignment: float
    timestamp: str
    image_path: Optional[str] = None

@dataclass
class ImaginedEpisode:
    """Complete imagined episode with metadata."""
    request: ImaginationRequest
    scene_graph: SceneGraph
    render_data: Optional[Dict[str, Any]] = None
    coherence_score: float = 0.0
    plausibility_score: float = 0.0
    novelty_score: float = 0.0
    utility_score: float = 0.0
    vividness_score: float = 0.0
    affect_alignment: float = 0.0
    timestamp: Optional[str] = None
    episode_id: Optional[str] = None

class ImaginationSystem:
    """
    CARL's imagination system implementing human-like mental imagery generation.
    """
    
    def __init__(self, api_client, memory_system, concept_system, neucogar_engine):
        """
        Initialize the imagination system.
        
        Args:
            api_client: OpenAI API client for image generation
            memory_system: CARL's memory system for episodic fragments
            concept_system: Concept system for semantic relationships
            neucogar_engine: NEUCOGAR engine for mood-dependent generation
        """
        self.api_client = api_client
        self.memory_system = memory_system
        self.concept_system = concept_system
        self.neucogar_engine = neucogar_engine
        self.logger = logging.getLogger(__name__)
        
        # Imagination storage
        self.imagined_episodes_dir = "memories/imagined"
        self.images_dir = "memories/imagined/images"
        self._ensure_directories()
        
        # Imagination parameters
        self.max_fragments = 5
        self.max_semantic_neighbors = 20
        self.max_blends = 20
        self.coherence_threshold = 0.6
        self.plausibility_threshold = 0.5
        
        # NEUCOGAR mood mapping
        self.mood_palette_mapping = {
            "dopamine": {
                "high": {"warmth": 0.8, "saturation": 0.7, "brightness": 0.8},
                "low": {"warmth": 0.3, "saturation": 0.4, "brightness": 0.5}
            },
            "serotonin": {
                "high": {"warmth": 0.6, "saturation": 0.6, "brightness": 0.7},
                "low": {"warmth": 0.2, "saturation": 0.3, "brightness": 0.4}
            },
            "noradrenaline": {
                "high": {"contrast": 0.8, "sharpness": 0.9, "framing": "tight"},
                "low": {"contrast": 0.4, "sharpness": 0.5, "framing": "wide"}
            }
        }
    
    def _ensure_directories(self):
        """Ensure imagination storage directories exist."""
        os.makedirs(self.imagined_episodes_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
    
    def generate_imagination(self, context: 'ImaginationContext') -> 'ImaginationArtifact':
        """
        Public method to generate imagination artifacts.
        
        Args:
            context: ImaginationContext with seed, purpose, and parameters
            
        Returns:
            ImaginationArtifact: Generated imagination artifact
        """
        try:
            self.logger.info(f"🎭 Generating imagination: {context.seed} for {context.purpose}")
            
            # Create imagination request from context
            request = ImaginationRequest(
                seed=context.seed,
                purpose=context.purpose,
                mbti_state=context.mbti_state,
                neucogar=context.neucogar_state,
                constraints=context.constraints,
                risk_budget=context.risk_budget,
                render=context.render_style,
                timestamp=datetime.now().isoformat()
            )
            
            # Generate imagined episode
            episode = self.imagine(context.seed, context.purpose, context.constraints)
            
            # Create artifact from episode
            artifact = ImaginationArtifact(
                episode_id=episode.episode_id,
                purpose=context.purpose,
                seed=context.seed,
                scene_description=self._scene_to_description(episode.scene_graph),
                render_style=context.render_style,
                coherence_score=episode.coherence_score,
                plausibility_score=episode.plausibility_score,
                novelty_score=episode.novelty_score,
                utility_score=episode.utility_score,
                vividness_score=episode.vividness_score,
                affect_alignment=episode.affect_alignment,
                timestamp=episode.timestamp,
                image_path=episode.render_data.get('image_path') if episode.render_data else None
            )
            
            self.logger.info(f"✅ Imagination artifact generated: {artifact.episode_id}")
            return artifact
            
        except Exception as e:
            self.logger.error(f"❌ Error generating imagination: {e}")
            # Return fallback artifact
            return self._create_fallback_artifact(context)
    
    def imagine(self, seed: str, purpose: str, constraints: Optional[Dict] = None) -> ImaginedEpisode:
        """
        Main imagination function - generates an imagined episode with inner thought integration.
        
        Args:
            seed: The seed concept or scenario to imagine
            purpose: Purpose of imagination (plan-social-interaction, explore-scenario, etc.)
            constraints: Optional constraints for the imagination
            
        Returns:
            ImaginedEpisode: Complete imagined episode
        """
        try:
            self.logger.info(f"🎭 Starting imagination process: {seed} for {purpose}")
            
            # Get current cognitive state
            state = self._get_current_cognitive_state()
            
            # Create imagination request
            request = ImaginationRequest(
                seed=seed,
                purpose=purpose,
                mbti_state=state['mbti'],
                neucogar=state['neucogar'],
                constraints=constraints,
                timestamp=datetime.now().isoformat()
            )
            
            # Select cues and retrieve fragments
            cues = self._select_cues(seed, purpose)
            fragments = self._retrieve_fragments(cues)
            
            # Generate conceptual blends
            blends = self._conceptual_blends(fragments)
            
            # Build scene graphs
            scenes = [self._build_scene_graph(blend) for blend in blends]
            
            # Ensure we have at least one scene
            if not scenes:
                self.logger.warning("No scenes generated from blends, creating fallback scene")
                fallback_scene = self._create_fallback_scene(seed, purpose)
                scenes = [fallback_scene]
            
            # Score and select best scene
            scored_scenes = [self._score_scene(scene, state) for scene in scenes]
            best_scene = max(scored_scenes, key=lambda x: x['score'])
            
            # Apply constraints if specified
            if constraints:
                best_scene = self._enforce_constraints(best_scene, constraints)
            
            # Generate image if requested
            render_data = None
            if request.render in ["image", "both"]:
                render_data = self._generate_image(best_scene, state, seed)
            
            # Create imagined episode
            episode = ImaginedEpisode(
                request=request,
                scene_graph=best_scene['scene'],
                render_data=render_data,
                coherence_score=best_scene['coherence'],
                plausibility_score=best_scene['plausibility'],
                novelty_score=best_scene['novelty'],
                utility_score=best_scene['utility'],
                vividness_score=best_scene['vividness'],
                affect_alignment=best_scene['affect_alignment'],
                timestamp=datetime.now().isoformat(),
                episode_id=self._generate_episode_id(seed, purpose)
            )
            
            # Store imagined episode
            self._store_imagined_episode(episode)
            
            # Broadcast to global workspace
            self._broadcast_to_gwt(episode)
            
            # Trigger NEUCOGAR effects for successful imagination
            self._trigger_neucogar_imagination_effects(best_scene['scene'], success=True)
            
            self.logger.info(f"✅ Imagination complete: {episode.episode_id}")
            return episode
            
        except Exception as e:
            self.logger.error(f"❌ Imagination failed: {e}")
            raise

    async def imagine_async(self, seed: str, purpose: str, constraints: Optional[Dict] = None) -> ImaginedEpisode:
        """
        Async version of imagination function - generates an imagined episode with async image generation.
        
        Args:
            seed: The seed concept or scenario to imagine
            purpose: Purpose of imagination (plan-social-interaction, explore-scenario, etc.)
            constraints: Optional constraints for the imagination
            
        Returns:
            ImaginedEpisode: Complete imagined episode
        """
        try:
            self.logger.info(f"🎭 Starting async imagination process: {seed} for {purpose}")
            
            # Get current cognitive state
            state = self._get_current_cognitive_state()
            
            # Create imagination request
            request = ImaginationRequest(
                seed=seed,
                purpose=purpose,
                mbti_state=state['mbti'],
                neucogar=state['neucogar'],
                constraints=constraints,
                timestamp=datetime.now().isoformat()
            )
            
            # Select cues and retrieve fragments
            cues = self._select_cues(seed, purpose)
            fragments = self._retrieve_fragments(cues)
            
            # Generate conceptual blends
            blends = self._conceptual_blends(fragments)
            
            # Build scene graphs
            scenes = [self._build_scene_graph(blend) for blend in blends]
            
            # Ensure we have at least one scene
            if not scenes:
                self.logger.warning("No scenes generated from blends, creating fallback scene")
                fallback_scene = self._create_fallback_scene(seed, purpose)
                scenes = [fallback_scene]
            
            # Score and select best scene
            scored_scenes = [self._score_scene(scene, state) for scene in scenes]
            best_scene = max(scored_scenes, key=lambda x: x['score'])
            
            # Apply constraints if specified
            if constraints:
                best_scene = self._enforce_constraints(best_scene, constraints)
            
            # Generate image if requested (async)
            render_data = None
            if request.render in ["image", "both"]:
                render_data = await self._generate_image_async(best_scene, state, seed)
            
            # Create imagined episode
            episode = ImaginedEpisode(
                request=request,
                scene_graph=best_scene['scene'],
                render_data=render_data,
                coherence_score=best_scene['coherence'],
                plausibility_score=best_scene['plausibility'],
                novelty_score=best_scene['novelty'],
                utility_score=best_scene['utility'],
                vividness_score=best_scene['vividness'],
                affect_alignment=best_scene['affect_alignment'],
                timestamp=datetime.now().isoformat(),
                episode_id=self._generate_episode_id(seed, purpose)
            )
            
            # Store imagined episode
            self._store_imagined_episode(episode)
            
            # Broadcast to global workspace
            self._broadcast_to_gwt(episode)
            
            self.logger.info(f"✅ Async imagination complete: {episode.episode_id}")
            return episode
            
        except Exception as e:
            self.logger.error(f"❌ Async imagination failed: {e}")
            raise
    
    def _get_current_cognitive_state(self) -> Dict[str, Any]:
        """Get current cognitive state for imagination."""
        try:
            # Get NEUCOGAR state
            neucogar_state = self.neucogar_engine.current_state
            
            # Get MBTI function states (simplified)
            mbti_state = {
                "Ti": 0.6,  # Internal thinking
                "Ne": 0.7,  # External intuition (high for imagination)
                "Si": 0.5,  # Internal sensing
                "Fe": 0.6   # External feeling
            }
            
            return {
                "neucogar": neucogar_state,
                "mbti": mbti_state,
                "current_emotion": self.neucogar_engine.get_current_emotion(),
                "current_goals": self._get_current_goals()
            }
        except Exception as e:
            self.logger.warning(f"Could not get cognitive state: {e}")
            return {
                "neucogar": {"dopamine": 0.5, "serotonin": 0.5, "noradrenaline": 0.5},
                "mbti": {"Ti": 0.5, "Ne": 0.7, "Si": 0.5, "Fe": 0.5},
                "current_emotion": {"emotion": "neutral", "intensity": 0.5},
                "current_goals": ["exploration", "social_interaction"]
            }
    
    def _select_cues(self, seed: str, purpose: str) -> List[str]:
        """Select relevant cues for imagination."""
        cues = [seed]
        
        # Add purpose-related cues
        if "social" in purpose:
            cues.extend(["conversation", "interaction", "people"])
        if "plan" in purpose:
            cues.extend(["future", "action", "goal"])
        if "explore" in purpose:
            cues.extend(["discovery", "novel", "environment"])
        
        # Add emotional cues based on current state
        emotion = self.neucogar_engine.get_current_emotion()
        if emotion['primary'] == 'joy':
            cues.append("positive")
        elif emotion['primary'] == 'fear':
            cues.append("caution")
        
        return cues
    
    def _retrieve_fragments(self, cues: List[str]) -> List[Dict[str, Any]]:
        """Retrieve episodic fragments and semantic neighbors."""
        fragments = []
        
        try:
            # Get episodic memories related to cues
            for cue in cues:
                memories = self.memory_system.search_memories(cue, limit=self.max_fragments)
                fragments.extend(memories)
            
            # Get semantic neighbors from concept system
            for cue in cues:
                neighbors = self.concept_system.get_related_concepts(cue, limit=self.max_semantic_neighbors)
                fragments.extend(neighbors)
            
            # Remove duplicates and limit
            unique_fragments = []
            seen = set()
            for fragment in fragments:
                fragment_id = fragment.get('id', str(fragment))
                if fragment_id not in seen:
                    unique_fragments.append(fragment)
                    seen.add(fragment_id)
            
            return unique_fragments[:self.max_fragments + self.max_semantic_neighbors]
            
        except Exception as e:
            self.logger.warning(f"Could not retrieve fragments: {e}")
            return []
    
    def _conceptual_blends(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate conceptual blends from fragments."""
        blends = []
        
        # Simple pairwise blending
        for i, frag1 in enumerate(fragments):
            for j, frag2 in enumerate(fragments[i+1:], i+1):
                blend = self._create_blend(frag1, frag2)
                if blend:
                    blends.append(blend)
        
        # Add some single fragments as potential scenes
        for fragment in fragments[:5]:
            blends.append({"base": fragment, "elements": [fragment]})
        
        return blends[:self.max_blends]
    
    def _create_blend(self, frag1: Dict[str, Any], frag2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a conceptual blend between two fragments."""
        try:
            # Extract key elements from fragments
            elements1 = self._extract_elements(frag1)
            elements2 = self._extract_elements(frag2)
            
            # Find compatible elements
            compatible = self._find_compatible_elements(elements1, elements2)
            
            if compatible:
                return {
                    "base": frag1,
                    "elements": [frag1, frag2],
                    "compatible_elements": compatible
                }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not create blend: {e}")
            return None
    
    def _extract_elements(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key elements from a fragment."""
        elements = {
            "objects": [],
            "actions": [],
            "emotions": [],
            "context": {}
        }
        
        # Extract from memory format
        if "WHAT" in fragment:
            elements["actions"].append(fragment["WHAT"])
        if "WHERE" in fragment:
            elements["context"]["location"] = fragment["WHERE"]
        if "emotions" in fragment:
            elements["emotions"].extend(fragment["emotions"])
        
        # Extract from concept format
        if "related_concepts" in fragment:
            elements["objects"].extend(fragment["related_concepts"])
        if "contextual_usage" in fragment:
            elements["actions"].extend(fragment["contextual_usage"])
        
        return elements
    
    def _find_compatible_elements(self, elements1: Dict[str, Any], elements2: Dict[str, Any]) -> Dict[str, Any]:
        """Find compatible elements between two sets of elements."""
        compatible = {
            "objects": [],
            "actions": [],
            "emotions": [],
            "context": {}
        }
        
        # Find overlapping objects
        objects1 = set(elements1.get("objects", []))
        objects2 = set(elements2.get("objects", []))
        compatible["objects"] = list(objects1.intersection(objects2))
        
        # Find compatible actions (simple heuristic)
        actions1 = elements1.get("actions", [])
        actions2 = elements2.get("actions", [])
        if actions1 and actions2:
            compatible["actions"] = [actions1[0], actions2[0]]
        
        # Merge emotions
        emotions1 = elements1.get("emotions", [])
        emotions2 = elements2.get("emotions", [])
        compatible["emotions"] = list(set(emotions1 + emotions2))
        
        # Merge context
        context1 = elements1.get("context", {})
        context2 = elements2.get("context", {})
        compatible["context"] = {**context1, **context2}
        
        return compatible
    
    def _build_scene_graph(self, blend: Dict[str, Any]) -> SceneGraph:
        """Build a scene graph from a conceptual blend."""
        try:
            # Extract elements from blend
            elements = blend.get("compatible_elements", {})
            
            # Build objects list
            objects = []
            for obj in elements.get("objects", []):
                objects.append({
                    "type": "concept",
                    "name": obj,
                    "attributes": {}
                })
            
            # Add default objects if none
            if not objects:
                objects = [
                    {"type": "agent", "name": "Carl", "attributes": {"role": "robot"}},
                    {"type": "person", "name": "Joe", "attributes": {"role": "human"}}
                ]
            
            # Build relations
            relations = []
            if len(objects) >= 2:
                relations.append({
                    "subj": objects[0]["name"],
                    "rel": "interacts_with",
                    "obj": objects[1]["name"]
                })
            
            # Determine affect from emotions
            emotions = elements.get("emotions", [])
            affect = self._determine_affect(emotions)
            
            # Build details
            details = {
                "lighting": "natural",
                "style": "photoreal",
                "setting": elements.get("context", {}).get("location", "indoor")
            }
            
            return SceneGraph(
                objects=objects,
                relations=relations,
                affect=affect,
                details=details,
                context=elements.get("context", {})
            )
            
        except Exception as e:
            self.logger.warning(f"Could not build scene graph: {e}")
            # Return default scene
            return SceneGraph(
                objects=[
                    {"type": "agent", "name": "Carl", "attributes": {"role": "robot"}},
                    {"type": "person", "name": "Joe", "attributes": {"role": "human"}}
                ],
                relations=[
                    {"subj": "Carl", "rel": "interacts_with", "obj": "Joe"}
                ],
                affect={"valence": 0.5, "arousal": 0.4, "dominant": "neutral"},
                details={"lighting": "natural", "style": "photoreal", "setting": "indoor"},
                context={}
            )
    
    def _determine_affect(self, emotions: List[str]) -> Dict[str, float]:
        """Determine affect from emotions."""
        valence = 0.5
        arousal = 0.4
        dominant = "neutral"
        
        for emotion in emotions:
            if emotion.lower() in ["joy", "happiness", "excitement"]:
                valence = 0.8
                arousal = 0.6
                dominant = "joy"
            elif emotion.lower() in ["fear", "anxiety", "worry"]:
                valence = 0.2
                arousal = 0.8
                dominant = "fear"
            elif emotion.lower() in ["sadness", "melancholy"]:
                valence = 0.3
                arousal = 0.2
                dominant = "sadness"
        
        return {
            "valence": valence,
            "arousal": arousal,
            "dominant": dominant
        }
    
    def _score_scene(self, scene: SceneGraph, state: Dict[str, Any]) -> Dict[str, Any]:
        """Score a scene for coherence, plausibility, novelty, utility, and vividness."""
        try:
            # Coherence score (graph consistency)
            coherence = self._calculate_coherence(scene)
            
            # Plausibility score (ConceptNet support)
            plausibility = self._calculate_plausibility(scene)
            
            # Novelty score (distance from existing memories)
            novelty = self._calculate_novelty(scene)
            
            # Utility score (goal satisfaction)
            utility = self._calculate_utility(scene, state)
            
            # Vividness score (detail richness)
            vividness = self._calculate_vividness(scene)
            
            # Affect alignment (mood consistency)
            affect_alignment = self._calculate_affect_alignment(scene, state)
            
            # Combined score
            score = (coherence * 0.3 + plausibility * 0.2 + novelty * 0.2 + 
                    utility * 0.2 + vividness * 0.1)
            
            return {
                "scene": scene,
                "coherence": coherence,
                "plausibility": plausibility,
                "novelty": novelty,
                "utility": utility,
                "vividness": vividness,
                "affect_alignment": affect_alignment,
                "score": score
            }
            
        except Exception as e:
            self.logger.warning(f"Could not score scene: {e}")
            return {
                "scene": scene,
                "coherence": 0.5,
                "plausibility": 0.5,
                "novelty": 0.5,
                "utility": 0.5,
                "vividness": 0.5,
                "affect_alignment": 0.5,
                "score": 0.5
            }
    
    def _calculate_coherence(self, scene: SceneGraph) -> float:
        """Calculate coherence score for scene graph."""
        # Simple coherence: all objects should have relations
        if not scene.objects:
            return 0.0
        
        connected_objects = set()
        for relation in scene.relations:
            connected_objects.add(relation["subj"])
            connected_objects.add(relation["obj"])
        
        object_names = {obj["name"] for obj in scene.objects}
        if not object_names:
            return 0.0
        
        coherence = len(connected_objects.intersection(object_names)) / len(object_names)
        return min(1.0, coherence + 0.3)  # Base coherence
    
    def _calculate_plausibility(self, scene: SceneGraph) -> float:
        """Calculate plausibility score using concept relationships."""
        # Simple plausibility: check if objects are related
        if len(scene.objects) < 2:
            return 0.5
        
        try:
            # Check if objects have concept relationships
            object_names = [obj["name"] for obj in scene.objects]
            plausibility = 0.5  # Base plausibility
            
            # Add points for each plausible relationship
            for relation in scene.relations:
                if relation["rel"] in ["interacts_with", "next_to", "at"]:
                    plausibility += 0.1
            
            return min(1.0, plausibility)
            
        except Exception as e:
            self.logger.warning(f"Could not calculate plausibility: {e}")
            return 0.5
    
    def _calculate_novelty(self, scene: SceneGraph) -> float:
        """Calculate novelty score (distance from existing memories)."""
        # Simple novelty: count unique elements
        unique_elements = set()
        for obj in scene.objects:
            unique_elements.add(obj["name"])
        for relation in scene.relations:
            unique_elements.add(f"{relation['subj']}_{relation['rel']}_{relation['obj']}")
        
        # Normalize by scene complexity
        total_elements = len(scene.objects) + len(scene.relations)
        if total_elements == 0:
            return 0.5
        
        novelty = len(unique_elements) / total_elements
        return min(1.0, novelty + 0.2)  # Base novelty
    
    def _calculate_utility(self, scene: SceneGraph, state: Dict[str, Any]) -> float:
        """Calculate utility score (goal satisfaction)."""
        goals = state.get("current_goals", [])
        utility = 0.5  # Base utility
        
        # Check if scene supports current goals
        scene_text = str(scene.objects) + str(scene.relations)
        for goal in goals:
            if goal.lower() in scene_text.lower():
                utility += 0.2
        
        return min(1.0, utility)
    
    def _calculate_vividness(self, scene: SceneGraph) -> float:
        """Calculate vividness score (detail richness)."""
        # Count details and attributes
        detail_count = 0
        
        # Object details
        for obj in scene.objects:
            detail_count += len(obj.get("attributes", {}))
        
        # Relation details
        detail_count += len(scene.relations)
        
        # Context details
        detail_count += len(scene.context)
        
        # Normalize
        vividness = min(1.0, detail_count / 10.0)
        return vividness + 0.3  # Base vividness
    
    def _calculate_affect_alignment(self, scene: SceneGraph, state: Dict[str, Any]) -> float:
        """Calculate affect alignment with current mood."""
        current_emotion = state.get("current_emotion", {"primary": "neutral", "intensity": 0.5})
        scene_affect = scene.affect
        
        # Simple alignment: positive emotion with positive valence
        if current_emotion["primary"] in ["joy", "happiness"] and scene_affect["valence"] > 0.6:
            return 0.8
        elif current_emotion["primary"] in ["fear", "anxiety"] and scene_affect["valence"] < 0.4:
            return 0.8
        else:
            return 0.5
    
    def _enforce_constraints(self, scene_data: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce constraints on the scene."""
        scene = scene_data["scene"]
        
        # Apply time constraints
        if "time" in constraints:
            scene.details["time"] = constraints["time"]
        
        # Apply weather constraints
        if "weather" in constraints:
            scene.details["weather"] = constraints["weather"]
        
        # Apply location constraints
        if "location" in constraints:
            scene.context["location"] = constraints["location"]
        
        return scene_data
    
    def _generate_image(self, scene_data: Dict[str, Any], state: Dict[str, Any], seed: str = None) -> Dict[str, Any]:
        """Generate an image from the scene using OpenAI DALL-E 3."""
        try:
            scene = scene_data["scene"]
            
            # Build prompt from scene graph with seed
            prompt = self._scene_to_prompt(scene, state, seed)
            
            # 🔧 FIX 2: Add fallback logging for prompt generation
            using_default_prompt = False
            if not prompt or prompt.strip() == "":
                using_default_prompt = True
                prompt = "First-person perspective view: imagine, a friendly indoor setting with warm lighting, showing what the viewer sees looking forward at the scene. The entire scene is rendered as a 3D hologram dream-state with depth layering and subtle glow, some spots in the scene are blurred with less details that Carl, a small EZ-Robot JD Model, is not focusing on, and the scene edges are dark and black, as if the scene was placed in a cloud and the edges blend into the darkness, showing what the viewer sees looking forward at the scene."
                self.logger.warning("⚠️ Default imagination prompt used due to null or empty response")
            
            # Get palette from NEUCOGAR state
            palette = self._get_mood_palette(state["neucogar"])
            
            # Generate image using OpenAI API
            image_data = self._call_openai_image_api(prompt, palette)
            
            if image_data:
                # Save image locally
                image_path = self._save_image_locally(image_data, scene_data)
                
                # 🔧 FIX 2: Ensure imagined_visual_path is set and file exists
                if image_path and os.path.exists(image_path):
                    self.logger.info(f"📸 Image successfully generated and saved: {image_path}")
                    return {
                        "type": "image",
                        "path": image_path,
                        "prompt": prompt,
                        "palette": palette,
                        "generated_at": datetime.now().isoformat()
                    }
                else:
                    self.logger.error("❌ Image not saved during imagination - file does not exist")
                    if image_path:
                        self.logger.error(f"❌ Expected path: {image_path}")
                    return None
            else:
                self.logger.warning("⚠️ No image data received from OpenAI API")
                return None
            
        except Exception as e:
            self.logger.error(f"Could not generate image: {e}")
            return None

    async def _generate_image_async(self, scene_data: Dict[str, Any], state: Dict[str, Any], seed: str = None) -> Dict[str, Any]:
        """Generate an image from the scene using OpenAI DALL-E 3 (async version)."""
        try:
            scene = scene_data["scene"]
            
            # Build prompt from scene graph with seed
            prompt = self._scene_to_prompt(scene, state, seed)
            
            # 🔧 FIX 2: Add fallback logging for prompt generation (async)
            using_default_prompt = False
            if not prompt or prompt.strip() == "":
                using_default_prompt = True
                prompt = "First-person perspective view: imagine, a friendly indoor setting with warm lighting, showing what the viewer sees looking forward at the scene. The entire scene is rendered as a 3D hologram dream-state with depth layering and subtle glow, some spots in the scene are blurred with less details that Carl, a small EZ-Robot JD Model, is not focusing on, and the scene edges are dark and black, as if the scene was placed in a cloud and the edges blend into the darkness, showing what the viewer sees looking forward at the scene."
                self.logger.warning("⚠️ Default imagination prompt used due to null or empty response (async)")
            
            # Get palette from NEUCOGAR state
            palette = self._get_mood_palette(state["neucogar"])
            
            # Generate image using OpenAI API (async)
            image_data = await self._call_openai_image_api_async(prompt, palette)
            
            if image_data:
                # Save image locally
                image_path = self._save_image_locally(image_data, scene_data)
                
                # 🔧 FIX 2: Ensure imagined_visual_path is set and file exists (async)
                if image_path and os.path.exists(image_path):
                    self.logger.info(f"📸 Image successfully generated and saved (async): {image_path}")
                    return {
                        "type": "image",
                        "path": image_path,
                        "prompt": prompt,
                        "palette": palette,
                        "generated_at": datetime.now().isoformat()
                    }
                else:
                    self.logger.error("❌ Image not saved during imagination (async) - file does not exist")
                    if image_path:
                        self.logger.error(f"❌ Expected path: {image_path}")
                    return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Could not generate image (async): {e}")
            return None
    
    def _trigger_neucogar_imagination_effects(self, scene: SceneGraph, success: bool = True):
        """Trigger NEUCOGAR neurotransmitter updates based on imagination outcomes."""
        try:
            if not self.neucogar_engine:
                return
            
            # Base effects for successful imagination
            if success:
                # Dopamine ↑ (reward) when imagination successfully reflects self-awareness
                self.neucogar_engine.trigger_neurotransmitter_effect("dopamine", 0.15, "imagination_success")
                
                # Check for positive/creative imagery
                scene_text = str(scene).lower()
                positive_indicators = ["joy", "happy", "creative", "beautiful", "wonderful", "amazing", "positive"]
                if any(indicator in scene_text for indicator in positive_indicators):
                    # Serotonin ↑ (contentment) if the imagined scene includes positive/creative imagery
                    self.neucogar_engine.trigger_neurotransmitter_effect("serotonin", 0.12, "positive_imagery")
                
                # Check for challenge, novelty, or danger
                challenge_indicators = ["challenge", "novel", "danger", "adventure", "explore", "new", "exciting"]
                if any(indicator in scene_text for indicator in challenge_indicators):
                    # Norepinephrine ↑ (arousal) if the imagination involves challenge, novelty, or danger
                    self.neucogar_engine.trigger_neurotransmitter_effect("noradrenaline", 0.18, "challenge_novelty")
            
            # Log the NEUCOGAR effects
            self.logger.info(f"NEUCOGAR imagination effects triggered: success={success}")
            
        except Exception as e:
            self.logger.error(f"Error triggering NEUCOGAR imagination effects: {e}")
    
    def _sanitize_imagination_prompt(self, prompt: str) -> str:
        """
        Sanitize imagination prompt to prevent OpenAI content policy violations.
        
        Args:
            prompt: Original prompt that may contain flagged content
            
        Returns:
            Sanitized prompt safe for OpenAI API
        """
        try:
            # Define potentially flagged content patterns
            flagged_patterns = {
                # Violence-related
                r'\b(violence|violent|fight|battle|war|attack|kill|murder|death|blood|gore)\b': 'action',
                r'\b(weapon|gun|knife|sword|bomb|explosion)\b': 'tool',
                
                # Adult content
                r'\b(nudity|nude|sexual|intimate|adult)\b': 'personal',
                
                # Harmful content
                r'\b(harm|hurt|pain|suffering|torture)\b': 'challenge',
                
                # Dangerous activities
                r'\b(dangerous|risky|unsafe|hazardous)\b': 'exciting',
                
                # Negative emotions (soften)
                r'\b(hate|anger|rage|fury)\b': 'strong emotion',
                r'\b(fear|terror|horror|dread)\b': 'caution',
            }
            
            sanitized_prompt = prompt
            
            # Replace flagged patterns with safer alternatives
            for pattern, replacement in flagged_patterns.items():
                sanitized_prompt = re.sub(pattern, replacement, sanitized_prompt, flags=re.IGNORECASE)
            
            # Add safety disclaimer
            if sanitized_prompt != prompt:
                sanitized_prompt += " (Note: Content has been adjusted for safety and creativity)"
                self.logger.info("🔒 Imagination prompt sanitized for OpenAI safety compliance")
            
            return sanitized_prompt
            
        except Exception as e:
            self.logger.warning(f"Error sanitizing prompt: {e}")
            return prompt

    def _scene_to_prompt(self, scene: SceneGraph, state: Dict[str, Any], seed: str = None) -> str:
        """Convert scene graph to DALL-E 3 prompt with first-person perspective and EZ-Robot JD embodiment."""
        try:
            # 🔧 FIX 2: ENHANCED IMAGINATION PROMPT PARSER - Use GPT keyword extraction for better prompts
            enhanced_prompt = self._generate_enhanced_imagination_prompt(scene, state, seed)
            if enhanced_prompt:
                self.logger.info("🎭 Using enhanced imagination prompt from GPT parsing")
                return enhanced_prompt
            
            # Fallback to original method if enhanced parsing fails
            self.logger.warning("🔄 Enhanced prompt parsing failed, using fallback method")
            
            # Check if CARL is in the scene
            carl_in_scene = False
            carl_role = ""
            other_characters = []
            
            # Analyze characters to determine perspective
            for obj in scene.objects:
                if obj["type"] in ["person", "agent"]:
                    name = obj["name"].lower()
                    role = obj.get("attributes", {}).get("role", "").lower()
                    
                    # Check if this is CARL (robot, AI, or self-reference)
                    if any(carl_indicator in name or carl_indicator in role for carl_indicator in 
                          ["carl", "robot", "ai", "self", "me", "myself", "humanoid"]):
                        carl_in_scene = True
                        carl_role = role if role else "robot"
                    else:
                        other_characters.append(f"{name} ({role})" if role else name)
            
            # Build structured prompt with first-person perspective
            prompt_parts = []
            
            # Setting
            setting = scene.details.get("setting", "indoor")
            lighting = scene.details.get("lighting", "natural")
            prompt_parts.append(f"Setting: {setting} with {lighting} lighting")
            
            # CRITICAL: CARL should ALMOST NEVER appear in the scene visually
            # All scenes should be from CARL's camera perspective, looking OUT at the world
            if carl_in_scene:
                # If CARL is mentioned in the scene, reframe it to be from his perspective
                if other_characters:
                    prompt_parts.append(f"CARL's view of: {', '.join(other_characters)}")
                else:
                    prompt_parts.append("CARL's view of the environment")
                
                # IMPORTANT: Do NOT show CARL's body in the image - only his perspective
                prompt_parts.append("CRITICAL: Do NOT show CARL's body in the image - only show what CARL sees")
            else:
                # CARL is not in the scene - perfect for first-person perspective
                if other_characters:
                    prompt_parts.append(f"CARL observes: {', '.join(other_characters)}")
                prompt_parts.append("Scene as seen through CARL's eyes")
            
            # Relations
            relations = []
            for relation in scene.relations:
                relations.append(f"{relation['subj']} {relation['rel']} {relation['obj']}")
            
            if relations:
                prompt_parts.append(f"Relations: {', '.join(relations)}")
            
            # Mood
            affect = scene.affect
            mood_desc = self._affect_to_mood_description(affect)
            prompt_parts.append(f"Mood: {mood_desc}")
            
            # Style - check if artistic mode is enabled
            is_artistic = scene.details.get("artistic_mode", False)
            if is_artistic:
                # Allow creative variations while keeping base recognizable as CARL
                style = scene.details.get("style", "artistic")
                prompt_parts.append(f"Style: {style} - artistic interpretation while maintaining EZ-Robot JD recognizability")
            else:
                # Standard style with strict EZ-Robot JD embodiment
                style = scene.details.get("style", "photoreal")
                prompt_parts.append(f"Style: {style} - strict EZ-Robot JD humanoid model representation")
            
            # ENFORCE FIRST-PERSON CAMERA PERSPECTIVE - CARL's viewpoint only
            prompt_parts.append("Visual style: first-person camera view, as if seen through CARL's eyes")
            prompt_parts.append("Camera angle: eye-level perspective, natural humanoid robot viewpoint")
            prompt_parts.append("Perspective: MUST be from CARL's first-person viewpoint - looking OUT at the world")
            prompt_parts.append("CRITICAL: Do NOT show CARL's body in the image - only show what CARL sees through his eyes")
            prompt_parts.append("Camera position: CARL's eye level, looking forward at the scene")
            
            # Safety constraints
            prompt_parts.append("Safety: no logos, no text in the image")
            
            # Combine into final prompt
            scene_description = ". ".join(prompt_parts)
            
            # 🔧 FIX 2: SANITIZE PROMPT FOR OPENAI SAFETY COMPLIANCE
            sanitized_description = self._sanitize_imagination_prompt(scene_description)
            
            # Enhanced system prompt for first-person perspective and EZ-Robot JD embodiment
            system_prompt = """SYSTEM: You are an imagery renderer that creates first-person perspective images from CARL's viewpoint.

USER: Render this scene as a single image from CARL's first-person perspective.
Scene:
{sanitized_description}
Return: one-sentence caption + concise visual description for DALL-E 3. Render as a 3D hologram artist effect—depth layering, subtle glow, slight chromatic aberration—as if visualized in CARL's mind. 

CRITICAL PERSPECTIVE RULES:
1. This image MUST be from CARL's camera/view perspective as an EZ-Robot JD humanoid model
2. CARL is 14 inches high with a metallic blue body and white head
3. CARL's own body should NEVER be visible in the image - only his perspective
4. The scene should be rendered from CARL's eye-level perspective, as if seen through his own eyes
5. Show ONLY what CARL would see looking OUT at the world, not a third-person view
6. Camera position: CARL's eye level, looking forward at the scene
7. No reflections, mirrors, or shadows that would show CARL's body

The image should look like what CARL sees through his own eyes, not what someone else sees of CARL.""".format(scene_description=sanitized_description)
            
            return system_prompt
            
        except Exception as e:
            self.logger.warning(f"Could not build prompt: {e}")
            return "First-person perspective from CARL's viewpoint: a photoreal image showing what CARL sees through his own eyes as an EZ-Robot JD humanoid model (14 inches high, metallic blue body, white head) looking OUT at a friendly setting, warm lighting, no text, no logos, rendered as a 3D hologram with depth layering and subtle glow, camera view from CARL's eye level, CRITICAL: Do NOT show CARL's body in the image - only show what CARL sees through his eyes"
    
    def _affect_to_mood_description(self, affect: Dict[str, float]) -> str:
        """Convert affect to mood description."""
        valence = affect.get("valence", 0.5)
        arousal = affect.get("arousal", 0.4)
        dominant = affect.get("dominant", "neutral")
        
        mood_parts = []
        
        if valence > 0.7:
            mood_parts.append("warm, positive")
        elif valence < 0.3:
            mood_parts.append("cool, somber")
        else:
            mood_parts.append("neutral, calm")
        
        if arousal > 0.7:
            mood_parts.append("energetic")
        elif arousal < 0.3:
            mood_parts.append("peaceful")
        
        if dominant != "neutral":
            mood_parts.append(dominant)
        
        return ", ".join(mood_parts) if mood_parts else "neutral, calm"
    
    def _get_mood_palette(self, neucogar: Dict[str, float]) -> Dict[str, Any]:
        """Get mood-dependent color palette from NEUCOGAR state."""
        palette = {
            "warmth": 0.5,
            "saturation": 0.5,
            "brightness": 0.5,
            "contrast": 0.5,
            "sharpness": 0.5
        }
        
        # Handle both dictionary and object formats
        if hasattr(neucogar, 'get'):
            # Dictionary format
            da = neucogar.get("dopamine", 0.5)
            ht = neucogar.get("serotonin", 0.5)
            ne = neucogar.get("noradrenaline", 0.5)
        else:
            # Object format - try to access attributes
            try:
                da = getattr(neucogar, 'dopamine', 0.5)
                ht = getattr(neucogar, 'serotonin', 0.5)
                ne = getattr(neucogar, 'noradrenaline', 0.5)
            except:
                # Fallback to default values
                da = ht = ne = 0.5
        
        # Adjust based on dopamine (warmth, brightness)
        if da > 0.6:
            palette["warmth"] += 0.2
            palette["brightness"] += 0.2
        elif da < 0.4:
            palette["warmth"] -= 0.2
            palette["brightness"] -= 0.2
        
        # Adjust based on serotonin (stability)
        if ht > 0.6:
            palette["saturation"] += 0.1
        elif ht < 0.4:
            palette["saturation"] -= 0.1
        
        # Adjust based on noradrenaline (contrast, sharpness)
        if ne > 0.6:
            palette["contrast"] += 0.2
            palette["sharpness"] += 0.2
        elif ne < 0.4:
            palette["contrast"] -= 0.2
            palette["sharpness"] -= 0.2
        
        # Clamp values
        for key in palette:
            palette[key] = max(0.0, min(1.0, palette[key]))
        
        return palette
    
    def _call_openai_image_api(self, prompt: str, palette: Dict[str, float]) -> Optional[bytes]:
        """Call OpenAI DALL-E 3 API to generate image."""
        try:
            # Get API key from client
            api_key = self.api_client.config.get('settings', 'OpenAIAPIKey')
            
            # Prepare request
            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            # Make request
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                
                # Download image
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    return image_response.content
            
            else:
                self.logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                
                # 🔧 FIX: Handle content policy violations with fallback prompt
                if response.status_code == 400 and "content_policy_violation" in response.text:
                    self.logger.warning("⚠️ Content policy violation detected, trying fallback prompt")
                    return self._try_fallback_prompt(api_key, headers, url)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Could not call OpenAI image API: {e}")
            return None

    def _try_fallback_prompt(self, api_key: str, headers: Dict[str, str], url: str) -> Optional[bytes]:
        """Try a safe fallback prompt when content policy violation occurs."""
        try:
            # Use the enhanced fallback prompt with "imagine" prefix and dream-state rendering
            fallback_prompt = "First-person perspective view: imagine, Inside a sun-drenched room, Carl, an EZ-Robot JD Model, and Joe engage with one another. Joe, seated on a worn-out, leather chair, looks up at Carl with a warm smile. The entire scene is rendered as a 3D hologram dream-state with depth layering and subtle glow, some spots in the scene are blurred with less details that Carl, a small EZ-Robot JD Model, is not focusing on, and the scene edges are dark and black, as if the scene was placed in a cloud and the edges blend into the darkness, showing what the viewer sees looking forward at the scene."
            
            data = {
                "model": "dall-e-3",
                "prompt": fallback_prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            self.logger.info(f"🔄 Trying fallback prompt: {fallback_prompt}")
            
            # Make request with fallback prompt
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                
                # Download image
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    self.logger.info("✅ Fallback prompt succeeded")
                    return image_response.content
            else:
                self.logger.warning(f"Fallback prompt also failed: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Fallback prompt failed: {e}")
            return None

    async def _call_openai_image_api_async(self, prompt: str, palette: Dict[str, float]) -> Optional[bytes]:
        """Call OpenAI DALL-E 3 API to generate image (async version)."""
        try:
            # Get API key from client
            api_key = self.api_client.config.get('settings', 'OpenAIAPIKey')
            
            # Prepare request
            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            # Make async request using aiohttp or similar
            import aiohttp
            import asyncio
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        result = await response.json()
                        image_url = result["data"][0]["url"]
                        
                        # Download image
                        async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=60)) as image_response:
                            if image_response.status == 200:
                                return await image_response.read()
                    else:
                        error_text = await response.text()
                        self.logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        
                        # 🔧 FIX: Handle content policy violations with fallback prompt (async)
                        if response.status == 400 and "content_policy_violation" in error_text:
                            self.logger.warning("⚠️ Content policy violation detected, trying fallback prompt (async)")
                            return await self._try_fallback_prompt_async(api_key, headers, url)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Could not call OpenAI image API (async): {e}")
            return None

    async def _try_fallback_prompt_async(self, api_key: str, headers: Dict[str, str], url: str) -> Optional[bytes]:
        """Try a safe fallback prompt when content policy violation occurs (async version)."""
        try:
            # Use the enhanced fallback prompt with "imagine" prefix and dream-state rendering
            fallback_prompt = "First-person perspective view: imagine, Inside a sun-drenched room, Carl, an EZ-Robot JD Model, and Joe engage with one another. Joe, seated on a worn-out, leather chair, looks up at Carl with a warm smile. The entire scene is rendered as a 3D hologram dream-state with depth layering and subtle glow, some spots in the scene are blurred with less details that Carl, a small EZ-Robot JD Model, is not focusing on, and the scene edges are dark and black, as if the scene was placed in a cloud and the edges blend into the darkness, showing what the viewer sees looking forward at the scene."
            
            data = {
                "model": "dall-e-3",
                "prompt": fallback_prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            self.logger.info(f"🔄 Trying fallback prompt (async): {fallback_prompt}")
            
            # Make async request with fallback prompt
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        result = await response.json()
                        image_url = result["data"][0]["url"]
                        
                        # Download image
                        async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=60)) as image_response:
                            if image_response.status == 200:
                                self.logger.info("✅ Fallback prompt succeeded (async)")
                                return await image_response.read()
                    else:
                        error_text = await response.text()
                        self.logger.warning(f"Fallback prompt also failed (async): {response.status} - {error_text}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Fallback prompt failed (async): {e}")
            return None
    
    def _save_image_locally(self, image_data: bytes, scene_data: Dict[str, Any]) -> str:
        """Save generated image locally."""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_hash = hashlib.md5(str(scene_data).encode()).hexdigest()[:8]
            filename = f"imagined_{timestamp}_{scene_hash}.png"
            filepath = os.path.join(self.images_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            self.logger.info(f"Saved imagined image: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Could not save image: {e}")
            return ""
    
    def _store_imagined_episode(self, episode: ImaginedEpisode):
        """Store imagined episode as memory."""
        try:
            # 🔧 FIX 4: MEMORY VISUAL LINKAGE & FAILOVER - Ensure valid image path exists before committing
            imagined_visual_path = None
            image_saved = False
            
            if episode.render_data and episode.render_data.get('path'):
                imagined_visual_path = episode.render_data['path']
                # Verify image file exists
                if os.path.exists(imagined_visual_path):
                    image_saved = True
                    self.logger.info(f"📸 Imagination image verified and linked: {imagined_visual_path}")
                else:
                    self.logger.warning(f"⚠️ Image file not found at path: {imagined_visual_path}")
                    imagined_visual_path = None
            else:
                self.logger.warning("⚠️ No image data in render_data for imagination episode")
            
            # 🔧 FIX 4: Add error catch and logging for failed image saves
            if not image_saved:
                self.logger.error(f"⚠️ Failed to save image for imagined episode: {episode.episode_id}")
                # Create a placeholder image path for failover
                imagined_visual_path = f"memories/imagined/images/placeholder_{episode.episode_id}.png"
                self.logger.info(f"🔄 Using placeholder image path: {imagined_visual_path}")
            
            # Convert to memory format
            memory_data = {
                "id": episode.episode_id,
                "type": "imagined_episode",
                "timestamp": episode.timestamp,
                "WHAT": f"Imagined scenario: {episode.request.seed}",
                "WHERE": episode.scene_graph.context.get("location", "imagined_space"),
                "WHY": f"Purpose: {episode.request.purpose}",
                "HOW": "Generated through imagination system",
                "WHO": "Carl (self)",
                "emotions": [episode.scene_graph.affect["dominant"]],
                "neucogar_emotional_state": {
                    "primary": episode.scene_graph.affect["dominant"],
                    "intensity": episode.scene_graph.affect["arousal"],
                    "neuro_coordinates": self._serialize_neucogar_state(episode.request.neucogar)
                },
                "scene_graph": asdict(episode.scene_graph),
                "render_data": episode.render_data,
                "imagined_visual_path": imagined_visual_path,  # 🔧 FIX: Link image path to episode
                "image_saved": image_saved,  # 🔧 FIX: Track image save status
                "scores": {
                    "coherence": episode.coherence_score,
                    "plausibility": episode.plausibility_score,
                    "novelty": episode.novelty_score,
                    "utility": episode.utility_score,
                    "vividness": episode.vividness_score,
                    "affect_alignment": episode.affect_alignment
                },
                "metadata": {
                    "purpose": episode.request.purpose,
                    "mbti_state": episode.request.mbti_state,
                    "constraints": episode.request.constraints,
                    "risk_budget": episode.request.risk_budget
                }
            }
            
            # Save to memory system
            memory_file = os.path.join(self.imagined_episodes_dir, f"{episode.episode_id}.json")
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Stored imagined episode: {episode.episode_id} (image_saved: {image_saved})")
            
        except Exception as e:
            self.logger.error(f"Could not store imagined episode: {e}")
    
    def _broadcast_to_gwt(self, episode: ImaginedEpisode):
        """Broadcast imagined episode to global workspace."""
        try:
            # This would integrate with CARL's global workspace theory implementation
            # For now, just log the broadcast
            self.logger.info(f"🎭 Broadcasting imagined episode to GWT: {episode.episode_id}")
            
        except Exception as e:
            self.logger.warning(f"Could not broadcast to GWT: {e}")
    
    def _serialize_neucogar_state(self, neucogar_state) -> Dict[str, float]:
        """Convert NEUCOGAR state to JSON-serializable dictionary."""
        try:
            if hasattr(neucogar_state, 'get'):
                # Already a dictionary
                return dict(neucogar_state)
            elif hasattr(neucogar_state, 'to_dict'):
                # Object with to_dict method
                return neucogar_state.to_dict()
            else:
                # Try to extract attributes
                result = {}
                for attr in ['dopamine', 'serotonin', 'noradrenaline']:
                    try:
                        result[attr] = getattr(neucogar_state, attr, 0.5)
                    except:
                        result[attr] = 0.5
                return result
        except Exception as e:
            self.logger.warning(f"Could not serialize NEUCOGAR state: {e}")
            return {"dopamine": 0.5, "serotonin": 0.5, "noradrenaline": 0.5}
    
    def _generate_episode_id(self, seed: str, purpose: str) -> str:
        """Generate unique episode ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_hash = hashlib.md5(seed.encode()).hexdigest()[:6]
        return f"imagined_{timestamp}_{seed_hash}"
    
    def _get_current_goals(self) -> List[str]:
        """Get current goals from CARL's system."""
        try:
            # This would integrate with CARL's goal system
            # For now, return default goals
            return ["exploration", "social_interaction", "learning"]
        except Exception as e:
            self.logger.warning(f"Could not get current goals: {e}")
            return ["exploration"]
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image using OpenAI Vision API to detect objects and describe vibe.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Get API key
            api_key = self.api_client.config.get('settings', 'OpenAIAPIKey')
            
            # Prepare request
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and provide:
1. All objects, people, and elements visible
2. The overall vibe/mood/atmosphere
3. Colors and lighting
4. Spatial relationships
5. Any emotions or feelings conveyed
6. How this relates to CARL's knowledge network

Return as structured JSON with fields: objects, vibe, colors, relationships, emotions, knowledge_connections"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            # Make request
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON from response
                try:
                    analysis = json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, create structured analysis
                    analysis = {
                        "objects": [],
                        "vibe": content,
                        "colors": "natural",
                        "relationships": [],
                        "emotions": [],
                        "knowledge_connections": []
                    }
                
                # Add metadata
                analysis["analyzed_at"] = datetime.now().isoformat()
                analysis["image_path"] = image_path
                
                return analysis
            
            else:
                self.logger.error(f"OpenAI Vision API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            self.logger.error(f"Could not analyze image: {e}")
            return None
    
    def get_imagined_episodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent imagined episodes."""
        try:
            episodes = []
            if os.path.exists(self.imagined_episodes_dir):
                files = [f for f in os.listdir(self.imagined_episodes_dir) if f.endswith('.json')]
                files.sort(key=lambda x: os.path.getmtime(os.path.join(self.imagined_episodes_dir, x)), reverse=True)
                
                for filename in files[:limit]:
                    filepath = os.path.join(self.imagined_episodes_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        episode = json.load(f)
                        episodes.append(episode)
            
            return episodes
            
        except Exception as e:
            self.logger.error(f"Could not get imagined episodes: {e}")
            return []
    
    def _create_fallback_scene(self, seed: str, purpose: str) -> SceneGraph:
        """Create a fallback scene when no scenes can be generated from fragments."""
        try:
            # Create a simple scene based on the seed and purpose
            objects = [
                {"type": "agent", "name": "Carl", "attributes": {"role": "robot"}},
                {"type": "person", "name": "Joe", "attributes": {"role": "human"}}
            ]
            
            # Add objects based on seed
            if "jack" in seed.lower() and "jill" in seed.lower():
                objects.extend([
                    {"type": "person", "name": "Jack", "attributes": {"role": "character"}},
                    {"type": "person", "name": "Jill", "attributes": {"role": "character"}},
                    {"type": "object", "name": "hill", "attributes": {"type": "landscape"}},
                    {"type": "object", "name": "pail", "attributes": {"type": "container"}},
                    {"type": "object", "name": "water", "attributes": {"type": "liquid"}}
                ])
            
            if "twister" in seed.lower() or "storm" in seed.lower():
                objects.append({"type": "object", "name": "twister", "attributes": {"type": "weather"}})
            
            # Build relations
            relations = []
            if len(objects) >= 2:
                relations.append({
                    "subj": objects[0]["name"],
                    "rel": "interacts_with",
                    "obj": objects[1]["name"]
                })
            
            # Add specific relations for Jack and Jill
            jack_obj = next((obj for obj in objects if obj["name"] == "Jack"), None)
            jill_obj = next((obj for obj in objects if obj["name"] == "Jill"), None)
            hill_obj = next((obj for obj in objects if obj["name"] == "hill"), None)
            
            if jack_obj and jill_obj and hill_obj:
                relations.extend([
                    {"subj": "Jack", "rel": "climbs", "obj": "hill"},
                    {"subj": "Jill", "rel": "climbs", "obj": "hill"},
                    {"subj": "Jack", "rel": "accompanies", "obj": "Jill"}
                ])
            
            # Determine affect based on purpose and seed
            affect = {"valence": 0.6, "arousal": 0.5, "dominant": "neutral"}
            if "storm" in seed.lower() or "twister" in seed.lower():
                affect = {"valence": 0.3, "arousal": 0.8, "dominant": "fear"}
            elif "joy" in seed.lower() or "happy" in seed.lower():
                affect = {"valence": 0.8, "arousal": 0.6, "dominant": "joy"}
            
            # Build details
            details = {
                "lighting": "natural",
                "style": "photoreal",
                "setting": "outdoor" if "hill" in seed.lower() else "indoor"
            }
            
            return SceneGraph(
                objects=objects,
                relations=relations,
                affect=affect,
                details=details,
                context={"location": "imagined_space", "seed": seed, "purpose": purpose}
            )
            
        except Exception as e:
            self.logger.warning(f"Could not create fallback scene: {e}")
            # Return minimal fallback
            return SceneGraph(
                objects=[
                    {"type": "agent", "name": "Carl", "attributes": {"role": "robot"}},
                    {"type": "person", "name": "Joe", "attributes": {"role": "human"}}
                ],
                relations=[],
                affect={"valence": 0.5, "arousal": 0.5, "dominant": "neutral"},
                details={"lighting": "neutral", "style": "simple", "setting": "generic"},
                context={"location": "fallback_space", "seed": seed, "purpose": purpose}
            )
    
    def _scene_to_description(self, scene: SceneGraph) -> str:
        """Convert scene graph to text description."""
        try:
            description_parts = []
            
            # Add objects
            object_names = [obj.get("name", "unknown") for obj in scene.objects]
            if object_names:
                description_parts.append(f"Scene contains: {', '.join(object_names)}")
            
            # Add relations
            if scene.relations:
                relation_descriptions = []
                for rel in scene.relations:
                    relation_descriptions.append(f"{rel.get('subj', 'unknown')} {rel.get('rel', 'interacts with')} {rel.get('obj', 'unknown')}")
                description_parts.append(f"Relations: {'. '.join(relation_descriptions)}")
            
            # Add affect
            if scene.affect:
                dominant = scene.affect.get('dominant', 'neutral')
                description_parts.append(f"Overall mood: {dominant}")
            
            # Add details
            if scene.details:
                setting = scene.details.get('setting', 'unknown')
                lighting = scene.details.get('lighting', 'standard')
                description_parts.append(f"Setting: {setting} with {lighting} lighting")
            
            return ". ".join(description_parts) if description_parts else "A generic imagined scene"
            
        except Exception as e:
            self.logger.error(f"Error converting scene to description: {e}")
            return "An imagined scene"
    
    def _create_fallback_artifact(self, context: ImaginationContext) -> ImaginationArtifact:
        """Create a fallback artifact when imagination generation fails."""
        try:
            fallback_scene = self._create_fallback_scene(context.seed, context.purpose)
            scene_description = self._scene_to_description(fallback_scene)
            
            return ImaginationArtifact(
                episode_id=f"fallback_{int(time.time())}",
                purpose=context.purpose,
                seed=context.seed,
                scene_description=scene_description,
                render_style=context.render_style,
                coherence_score=0.3,
                plausibility_score=0.4,
                novelty_score=0.2,
                utility_score=0.3,
                vividness_score=0.3,
                affect_alignment=0.4,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error creating fallback artifact: {e}")
            # Return minimal fallback
            return ImaginationArtifact(
                episode_id=f"error_{int(time.time())}",
                purpose=context.purpose,
                seed=context.seed,
                scene_description="Error generating imagination",
                render_style=context.render_style,
                coherence_score=0.0,
                plausibility_score=0.0,
                novelty_score=0.0,
                utility_score=0.0,
                vividness_score=0.0,
                affect_alignment=0.0,
                timestamp=datetime.now().isoformat()
            )
    
    def _generate_enhanced_imagination_prompt(self, scene: SceneGraph, state: Dict[str, Any], seed: str = None) -> Optional[str]:
        """
        🔧 FIX 2: ENHANCED IMAGINATION PROMPT PARSER - Use GPT keyword extraction for better prompts
        
        Example: 
            Input: "Imagine Jack and Jill... with twister storm"
            Output Prompt: "Create an image showing Jack and Jill climbing a hill with a tornado approaching in the background."
        """
        try:
            # Extract key elements from scene
            scene_text = self._scene_to_description(scene)
            
            # Use OpenAI API to enhance the prompt with seed concept
            enhanced_prompt = self._call_openai_prompt_enhancement(scene_text, seed)
            
            if enhanced_prompt:
                # Apply first-person perspective rules
                final_prompt = self._apply_first_person_perspective_rules(enhanced_prompt)
                return final_prompt
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Enhanced prompt generation failed: {e}")
            return None
    
    def _call_openai_prompt_enhancement(self, scene_text: str, seed: str = None) -> Optional[str]:
        """Call OpenAI API to enhance imagination prompts."""
        try:
            # Get API key from client
            api_key = self.api_client.config.get('settings', 'OpenAIAPIKey')
            if not api_key:
                self.logger.warning("No OpenAI API key available for prompt enhancement")
                return None
            
            # Prepare request for prompt enhancement
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Include seed concept in the prompt if available
            user_content = f"Enhance this scene description for image generation: {scene_text}"
            if seed:
                user_content = f"Seed concept: {seed}\n\nScene description: {scene_text}\n\nCreate an enhanced visual prompt that incorporates the seed concept."
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert at creating vivid, detailed image generation prompts. 
                        Your task is to take a basic scene description and enhance it into a rich, visual prompt.
                        
                        Rules:
                        1. Extract key subjects, actions, and modifiers
                        2. Add atmospheric details (lighting, mood, setting)
                        3. Include spatial relationships and composition
                        4. Make it highly visual and descriptive
                        5. Keep it under 100 words
                        6. Focus on what can be seen, not abstract concepts
                        7. If a seed concept is provided, incorporate it into the visual prompt
                        
                        Return only the enhanced prompt, no explanations."""
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            # Make request
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                enhanced_prompt = result["choices"][0]["message"]["content"].strip()
                self.logger.info(f"🎭 Enhanced prompt generated: {enhanced_prompt[:100]}...")
                return enhanced_prompt
            else:
                self.logger.warning(f"OpenAI prompt enhancement failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Error calling OpenAI prompt enhancement: {e}")
            return None
    
    def _apply_first_person_perspective_rules(self, enhanced_prompt: str) -> str:
        """Apply first-person perspective rules to enhanced prompt."""
        try:
            # 🔧 FIX: Enhanced prompt formatting with "imagine" prefix and dream-state rendering
            # Clean and simplify the enhanced prompt
            clean_prompt = enhanced_prompt.strip()
            
            # Add "imagine" prefix and enhanced 3D hologram dream-state rendering
            final_prompt = f"First-person perspective view: imagine, {clean_prompt} The entire scene is rendered as a 3D hologram dream-state with depth layering and subtle glow, some spots in the scene are blurred with less details that Carl, a small EZ-Robot JD Model, is not focusing on, and the scene edges are dark and black, as if the scene was placed in a cloud and the edges blend into the darkness, showing what the viewer sees looking forward at the scene."
            
            return final_prompt
            
        except Exception as e:
            self.logger.warning(f"Error applying first-person perspective rules: {e}")
            return enhanced_prompt
    
    def trigger_imagination_from_inner_thought(self, inner_thought: str, thought_context: Dict) -> Optional[ImaginedEpisode]:
        """
        Trigger imagination episodes from inner thoughts and visual thinking.
        
        Args:
            inner_thought: The inner thought that triggered imagination
            thought_context: Context from the inner world system
            
        Returns:
            ImaginedEpisode if imagination was triggered, None otherwise
        """
        try:
            # Analyze if the inner thought should trigger imagination
            imagination_triggers = self._analyze_imagination_triggers(inner_thought, thought_context)
            
            if not imagination_triggers["should_imagine"]:
                return None
            
            # Extract imagination seed from the thought
            seed = self._extract_imagination_seed(inner_thought, imagination_triggers)
            
            # Determine purpose based on thought context
            purpose = self._determine_imagination_purpose(inner_thought, thought_context)
            
            # Generate imagination episode
            episode = self.imagine(seed, purpose, thought_context.get("constraints"))
            
            # Integrate with inner world system
            self._integrate_imagination_with_inner_world(episode, thought_context)
            
            return episode
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering imagination from inner thought: {e}")
            return None
    
    def _analyze_imagination_triggers(self, inner_thought: str, thought_context: Dict) -> Dict:
        """
        Analyze if an inner thought should trigger imagination.
        
        Args:
            inner_thought: The inner thought to analyze
            thought_context: Context from inner world system
            
        Returns:
            Dictionary with trigger analysis
        """
        try:
            thought_lower = inner_thought.lower()
            
            # Imagination trigger patterns
            visual_thinking_indicators = [
                "imagine", "picture", "visualize", "see", "envision", "dream",
                "what if", "suppose", "imagine if", "picture this", "visualize"
            ]
            
            creative_problem_solving_indicators = [
                "how could", "what would happen if", "alternative", "different way",
                "creative solution", "brainstorm", "explore", "possibility"
            ]
            
            planning_indicators = [
                "plan", "prepare", "rehearse", "practice", "anticipate",
                "future", "upcoming", "next time", "when"
            ]
            
            # Check for visual thinking
            visual_thinking = any(indicator in thought_lower for indicator in visual_thinking_indicators)
            
            # Check for creative problem solving
            creative_solving = any(indicator in thought_lower for indicator in creative_problem_solving_indicators)
            
            # Check for planning
            planning = any(indicator in thought_lower for indicator in planning_indicators)
            
            # Determine if imagination should be triggered
            should_imagine = visual_thinking or creative_solving or planning
            
            # Calculate confidence based on multiple indicators
            confidence = 0.0
            if visual_thinking:
                confidence += 0.4
            if creative_solving:
                confidence += 0.3
            if planning:
                confidence += 0.3
            
            return {
                "should_imagine": should_imagine,
                "confidence": confidence,
                "triggers": {
                    "visual_thinking": visual_thinking,
                    "creative_solving": creative_solving,
                    "planning": planning
                },
                "primary_trigger": "visual_thinking" if visual_thinking else 
                                 "creative_solving" if creative_solving else 
                                 "planning" if planning else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing imagination triggers: {e}")
            return {"should_imagine": False, "confidence": 0.0, "triggers": {}}
    
    def _extract_imagination_seed(self, inner_thought: str, triggers: Dict) -> str:
        """
        Extract imagination seed from inner thought.
        
        Args:
            inner_thought: The inner thought
            triggers: Trigger analysis results
            
        Returns:
            Extracted seed for imagination
        """
        try:
            # Remove trigger words and extract the core concept
            thought = inner_thought.lower()
            
            # Remove common trigger phrases
            trigger_phrases = [
                "i imagine", "let me imagine", "what if", "suppose", "imagine if",
                "picture this", "visualize", "i see", "i envision", "i dream"
            ]
            
            for phrase in trigger_phrases:
                thought = thought.replace(phrase, "").strip()
            
            # Clean up the thought
            thought = thought.strip(".,!?")
            
            # If the thought is too short, use the original
            if len(thought.split()) < 3:
                return inner_thought
            
            return thought
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting imagination seed: {e}")
            return inner_thought
    
    def _determine_imagination_purpose(self, inner_thought: str, thought_context: Dict) -> str:
        """
        Determine the purpose of imagination based on thought context.
        
        Args:
            inner_thought: The inner thought
            thought_context: Context from inner world system
            
        Returns:
            Purpose string for imagination
        """
        try:
            thought_lower = inner_thought.lower()
            
            # Social interaction planning
            if any(word in thought_lower for word in ["talk", "conversation", "meet", "interact", "social"]):
                return "plan-social-interaction"
            
            # Problem solving
            if any(word in thought_lower for word in ["solve", "fix", "problem", "challenge", "difficulty"]):
                return "creative-problem-solving"
            
            # Future planning
            if any(word in thought_lower for word in ["future", "plan", "prepare", "upcoming", "next"]):
                return "future-planning"
            
            # Exploration
            if any(word in thought_lower for word in ["explore", "discover", "learn", "understand", "investigate"]):
                return "explore-scenario"
            
            # Default to exploration
            return "explore-scenario"
            
        except Exception as e:
            self.logger.error(f"❌ Error determining imagination purpose: {e}")
            return "explore-scenario"
    
    def _integrate_imagination_with_inner_world(self, episode: ImaginedEpisode, thought_context: Dict):
        """
        Integrate imagination episode with inner world system.
        
        Args:
            episode: The imagined episode
            thought_context: Context from inner world system
        """
        try:
            # Create visual thinking entry
            visual_thinking_entry = {
                "type": "visual_thinking",
                "episode_id": episode.episode_id,
                "trigger_thought": thought_context.get("original_thought", ""),
                "imagination_purpose": episode.purpose,
                "visual_elements": episode.scene_graph.visual_elements,
                "emotional_tone": episode.emotional_tone,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in memory system if available
            if hasattr(self, 'memory_system') and self.memory_system:
                self.memory_system.store_visual_thinking(visual_thinking_entry)
            
            self.logger.info(f"🎭 Integrated imagination episode {episode.episode_id} with inner world system")
            
        except Exception as e:
            self.logger.error(f"❌ Error integrating imagination with inner world: {e}")
    
    def get_visual_thinking_history(self, limit: int = 10) -> List[Dict]:
        """
        Get history of visual thinking episodes.
        
        Args:
            limit: Maximum number of episodes to return
            
        Returns:
            List of visual thinking episodes
        """
        try:
            if hasattr(self, 'memory_system') and self.memory_system:
                return self.memory_system.get_visual_thinking_history(limit)
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error getting visual thinking history: {e}")
            return []
    
    def enhance_inner_dialogue_with_visuals(self, inner_thought: str, context: Dict) -> str:
        """
        Enhance inner dialogue with visual thinking elements.
        
        Args:
            inner_thought: The inner thought
            context: Context information
            
        Returns:
            Enhanced thought with visual elements
        """
        try:
            # Check if this thought could benefit from visual enhancement
            if not self._should_enhance_with_visuals(inner_thought, context):
                return inner_thought
            
            # Get relevant visual thinking history
            visual_history = self.get_visual_thinking_history(5)
            
            # Enhance the thought with visual elements
            enhanced_thought = self._apply_visual_enhancement(inner_thought, visual_history, context)
            
            return enhanced_thought
            
        except Exception as e:
            self.logger.error(f"❌ Error enhancing inner dialogue with visuals: {e}")
            return inner_thought
    
    def _should_enhance_with_visuals(self, inner_thought: str, context: Dict) -> bool:
        """Determine if a thought should be enhanced with visual elements."""
        try:
            thought_lower = inner_thought.lower()
            
            # Visual enhancement indicators
            visual_indicators = [
                "see", "look", "appear", "seem", "visual", "image", "picture",
                "scene", "view", "observe", "notice", "recognize"
            ]
            
            return any(indicator in thought_lower for indicator in visual_indicators)
            
        except Exception as e:
            self.logger.error(f"❌ Error checking visual enhancement: {e}")
            return False
    
    def _apply_visual_enhancement(self, inner_thought: str, visual_history: List[Dict], context: Dict) -> str:
        """Apply visual enhancement to inner thought."""
        try:
            # For now, return the original thought
            # This could be enhanced with actual visual processing
            return inner_thought
            
        except Exception as e:
            self.logger.error(f"❌ Error applying visual enhancement: {e}")
            return inner_thought
