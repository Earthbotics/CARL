#!/usr/bin/env python3
"""
Enhanced Concept Graph System with Gordon & Hobbs Accessibility by Association

Implements concept graph linking with edge inference from:
- AssociatedGoals and AssociatedNeeds
- Co-occurrence in events
- Gordon & Hobbs Accessibility by Association
- Temporal and semantic relationships
"""

import json
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import networkx as nx
from collections import defaultdict, Counter

@dataclass
class ConceptEdge:
    """Represents an edge between two concepts in the graph."""
    source: str
    target: str
    edge_type: str  # goal_shared, need_shared, co_occurrence, semantic, temporal
    weight: float  # 0.0 to 1.0
    evidence: List[str]  # List of evidence sources
    created_at: str
    last_updated: str
    metadata: Dict[str, Any]

@dataclass
class AccessibilityNode:
    """Represents a concept node with accessibility information."""
    concept: str
    activation_level: float  # 0.0 to 1.0
    last_activated: str
    associated_concepts: List[str]
    accessibility_score: float
    context_history: List[Dict[str, Any]]

class ConceptGraphSystem:
    """
    Enhanced concept graph system implementing Gordon & Hobbs Accessibility by Association.
    """
    
    def __init__(self, concepts_dir: str = "concepts", 
                 needs_dir: str = "needs", 
                 goals_dir: str = "goals",
                 memories_dir: str = "memories"):
        self.concepts_dir = concepts_dir
        self.needs_dir = needs_dir
        self.goals_dir = goals_dir
        self.memories_dir = memories_dir
        self.logger = logging.getLogger(__name__)
        
        # Graph structure
        self.graph = nx.Graph()
        self.edges: Dict[str, ConceptEdge] = {}
        self.accessibility_nodes: Dict[str, AccessibilityNode] = {}
        
        # Caches
        self.concept_cache: Dict[str, Dict] = {}
        self.need_cache: Dict[str, Dict] = {}
        self.goal_cache: Dict[str, Dict] = {}
        self.event_cache: List[Dict] = []
        
        # Configuration
        self.edge_decay_factor = 0.95  # How quickly edge weights decay
        self.activation_decay_rate = 0.1  # How quickly activation decays
        self.min_edge_weight = 0.1  # Minimum weight to keep an edge
        self.max_edges_per_concept = 20  # Maximum edges per concept
        
        # 🔧 ENHANCEMENT: Rate limiting for repetitive associations
        self.association_rate_limit = {}  # Track recent associations
        self.rate_limit_window = 30  # seconds
        self.max_associations_per_window = 5  # max associations per window
        
        # Load existing data
        self._load_concepts()
        self._load_needs_and_goals()
        self._load_recent_events()
        
    def _load_concepts(self):
        """Load all concept files into cache."""
        try:
            for filename in os.listdir(self.concepts_dir):
                if filename.endswith('.json'):
                    concept_name = filename.replace('.json', '')
                    concept_file = os.path.join(self.concepts_dir, filename)
                    
                    with open(concept_file, 'r') as f:
                        concept_data = json.load(f)
                    
                    self.concept_cache[concept_name] = concept_data
                    
            self.logger.info(f"Loaded {len(self.concept_cache)} concepts")
            
        except Exception as e:
            self.logger.error(f"Error loading concepts: {e}")
    
    def _load_needs_and_goals(self):
        """Load needs and goals for relationship inference."""
        try:
            # Load needs
            if os.path.exists(self.needs_dir):
                for filename in os.listdir(self.needs_dir):
                    if filename.endswith('.json'):
                        need_name = filename.replace('.json', '')
                        need_file = os.path.join(self.needs_dir, filename)
                        
                        with open(need_file, 'r') as f:
                            need_data = json.load(f)
                        
                        self.need_cache[need_name] = need_data
            
            # Load goals
            if os.path.exists(self.goals_dir):
                for filename in os.listdir(self.goals_dir):
                    if filename.endswith('.json'):
                        goal_name = filename.replace('.json', '')
                        goal_file = os.path.join(self.goals_dir, filename)
                        
                        with open(goal_file, 'r') as f:
                            goal_data = json.load(f)
                        
                        self.goal_cache[goal_name] = goal_data
            
            self.logger.info(f"Loaded {len(self.need_cache)} needs and {len(self.goal_cache)} goals")
            
        except Exception as e:
            self.logger.error(f"Error loading needs and goals: {e}")
    
    def _load_recent_events(self):
        """Load recent events for co-occurrence analysis."""
        try:
            # Load short-term memory for recent events
            stm_file = "short_term_memory.json"
            if os.path.exists(stm_file):
                with open(stm_file, 'r') as f:
                    stm_data = json.load(f)
                
                # Extract recent events (last 24 hours)
                recent_time = datetime.now() - timedelta(hours=24)
                
                # Handle different data structures
                events = []
                if isinstance(stm_data, dict):
                    events = stm_data.get('events', [])
                elif isinstance(stm_data, list):
                    events = stm_data
                
                for event in events:
                    if isinstance(event, dict) and 'timestamp' in event:
                        try:
                            event_time = datetime.fromisoformat(event.get('timestamp', ''))
                            if event_time > recent_time:
                                self.event_cache.append(event)
                        except (ValueError, TypeError):
                            # Skip events with invalid timestamps
                            continue
                
                self.logger.info(f"Loaded {len(self.event_cache)} recent events")
            
        except Exception as e:
            self.logger.error(f"Error loading recent events: {e}")
    
    def update_concept_graph(self, new_event: Optional[Dict] = None):
        """
        Update the concept graph with new relationships and accessibility.
        
        Args:
            new_event: Optional new event to process
        """
        try:
            # Add new event to cache if provided
            if new_event:
                self.event_cache.append(new_event)
            
            # Clear existing graph
            self.graph.clear()
            
            # Build edges from various sources
            self._build_goal_shared_edges()
            self._build_need_shared_edges()
            self._build_co_occurrence_edges()
            self._build_semantic_edges()
            self._build_temporal_edges()
            
            # Apply Gordon & Hobbs Accessibility by Association
            self._apply_accessibility_association()
            
            # Prune weak edges
            self._prune_weak_edges()
            
            # Update accessibility scores
            self._update_accessibility_scores()
            
            # Save graph
            self._save_graph()
            
            self.logger.info(f"Updated concept graph with {self.graph.number_of_edges()} edges")
            
        except Exception as e:
            self.logger.error(f"Error updating concept graph: {e}")
    
    def _build_goal_shared_edges(self):
        """Build edges between concepts that share goals."""
        try:
            goal_concepts = defaultdict(set)
            
            # Find concepts associated with each goal
            for goal_name, goal_data in self.goal_cache.items():
                associated_concepts = goal_data.get('associated_concepts', [])
                for concept in associated_concepts:
                    goal_concepts[goal_name].add(concept)
            
            # Create edges between concepts that share goals
            for goal_name, concepts in goal_concepts.items():
                concept_list = list(concepts)
                for i in range(len(concept_list)):
                    for j in range(i + 1, len(concept_list)):
                        source = concept_list[i]
                        target = concept_list[j]
                        
                        edge_id = f"{source}_{target}_goal"
                        if edge_id not in self.edges:
                            edge = ConceptEdge(
                                source=source,
                                target=target,
                                edge_type="goal_shared",
                                weight=0.7,  # High weight for goal sharing
                                evidence=[f"Shared goal: {goal_name}"],
                                created_at=datetime.now().isoformat(),
                                last_updated=datetime.now().isoformat(),
                                metadata={"shared_goal": goal_name}
                            )
                            self.edges[edge_id] = edge
                        else:
                            # Update existing edge
                            self.edges[edge_id].evidence.append(f"Shared goal: {goal_name}")
                            self.edges[edge_id].last_updated = datetime.now().isoformat()
                            self.edges[edge_id].weight = min(1.0, self.edges[edge_id].weight + 0.1)
            
            self.logger.info(f"Built {len([e for e in self.edges.values() if e.edge_type == 'goal_shared'])} goal-shared edges")
            
        except Exception as e:
            self.logger.error(f"Error building goal-shared edges: {e}")
    
    def _build_need_shared_edges(self):
        """Build edges between concepts that share needs."""
        try:
            need_concepts = defaultdict(set)
            
            # Find concepts associated with each need
            for need_name, need_data in self.need_cache.items():
                associated_concepts = need_data.get('associated_concepts', [])
                for concept in associated_concepts:
                    need_concepts[need_name].add(concept)
            
            # Create edges between concepts that share needs
            for need_name, concepts in need_concepts.items():
                concept_list = list(concepts)
                for i in range(len(concept_list)):
                    for j in range(i + 1, len(concept_list)):
                        source = concept_list[i]
                        target = concept_list[j]
                        
                        edge_id = f"{source}_{target}_need"
                        if edge_id not in self.edges:
                            edge = ConceptEdge(
                                source=source,
                                target=target,
                                edge_type="need_shared",
                                weight=0.6,  # Medium-high weight for need sharing
                                evidence=[f"Shared need: {need_name}"],
                                created_at=datetime.now().isoformat(),
                                last_updated=datetime.now().isoformat(),
                                metadata={"shared_need": need_name}
                            )
                            self.edges[edge_id] = edge
                        else:
                            # Update existing edge
                            self.edges[edge_id].evidence.append(f"Shared need: {need_name}")
                            self.edges[edge_id].last_updated = datetime.now().isoformat()
                            self.edges[edge_id].weight = min(1.0, self.edges[edge_id].weight + 0.1)
            
            self.logger.info(f"Built {len([e for e in self.edges.values() if e.edge_type == 'need_shared'])} need-shared edges")
            
        except Exception as e:
            self.logger.error(f"Error building need-shared edges: {e}")
    
    def _build_co_occurrence_edges(self):
        """Build edges based on co-occurrence in events."""
        try:
            concept_co_occurrences = defaultdict(Counter)
            
            # Analyze co-occurrences in recent events
            for event in self.event_cache:
                # Extract concepts from event
                event_concepts = set()
                
                # Extract from WHAT field
                what = event.get('WHAT', '')
                if what:
                    words = what.lower().split()
                    for word in words:
                        if word in self.concept_cache:
                            event_concepts.add(word)
                
                # Extract from contexts in concepts
                for concept_name, concept_data in self.concept_cache.items():
                    contexts = concept_data.get('contexts', [])
                    for context in contexts:
                        if context.get('timestamp') == event.get('timestamp'):
                            event_concepts.add(concept_name)
                
                # Record co-occurrences
                concept_list = list(event_concepts)
                for i in range(len(concept_list)):
                    for j in range(i + 1, len(concept_list)):
                        source = concept_list[i]
                        target = concept_list[j]
                        concept_co_occurrences[(source, target)][event.get('timestamp', '')] += 1
            
            # Create edges based on co-occurrence frequency
            for (source, target), occurrences in concept_co_occurrences.items():
                frequency = len(occurrences)
                weight = min(0.8, 0.2 + (frequency * 0.1))  # Base 0.2 + 0.1 per occurrence
                
                edge_id = f"{source}_{target}_cooccur"
                if edge_id not in self.edges:
                    edge = ConceptEdge(
                        source=source,
                        target=target,
                        edge_type="co_occurrence",
                        weight=weight,
                        evidence=[f"Co-occurred in {frequency} events"],
                        created_at=datetime.now().isoformat(),
                        last_updated=datetime.now().isoformat(),
                        metadata={"co_occurrence_count": frequency}
                    )
                    self.edges[edge_id] = edge
                else:
                    # Update existing edge
                    self.edges[edge_id].evidence.append(f"Co-occurred in {frequency} events")
                    self.edges[edge_id].last_updated = datetime.now().isoformat()
                    self.edges[edge_id].weight = min(1.0, self.edges[edge_id].weight + 0.05)
            
            self.logger.info(f"Built {len([e for e in self.edges.values() if e.edge_type == 'co_occurrence'])} co-occurrence edges")
            
        except Exception as e:
            self.logger.error(f"Error building co-occurrence edges: {e}")
    
    def _build_semantic_edges(self):
        """Build edges based on semantic relationships from ConceptNet."""
        try:
            for concept_name, concept_data in self.concept_cache.items():
                conceptnet_data = concept_data.get('conceptnet_data', {})
                edges = conceptnet_data.get('edges', [])
                
                for edge_data in edges:
                    target = edge_data.get('target', '')
                    relationship = edge_data.get('relationship', '')
                    weight = edge_data.get('weight', 0.0)
                    
                    # Normalize weight to 0-1 range
                    normalized_weight = min(1.0, weight / 10.0)
                    
                    if target and target in self.concept_cache and normalized_weight > 0.3:
                        edge_id = f"{concept_name}_{target}_semantic"
                        if edge_id not in self.edges:
                            edge = ConceptEdge(
                                source=concept_name,
                                target=target,
                                edge_type="semantic",
                                weight=normalized_weight,
                                evidence=[f"ConceptNet: {relationship}"],
                                created_at=datetime.now().isoformat(),
                                last_updated=datetime.now().isoformat(),
                                metadata={"conceptnet_relationship": relationship}
                            )
                            self.edges[edge_id] = edge
            
            self.logger.info(f"Built {len([e for e in self.edges.values() if e.edge_type == 'semantic'])} semantic edges")
            
        except Exception as e:
            self.logger.error(f"Error building semantic edges: {e}")
    
    def _build_temporal_edges(self):
        """Build edges based on temporal proximity in events."""
        try:
            # Group events by time windows (e.g., 1-hour windows)
            time_windows = defaultdict(list)
            window_size = timedelta(hours=1)
            
            for event in self.event_cache:
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                window_start = timestamp.replace(minute=0, second=0, microsecond=0)
                time_windows[window_start].append(event)
            
            # Create edges between concepts in same time windows
            for window_start, events in time_windows.items():
                window_concepts = set()
                
                for event in events:
                    # Extract concepts from event
                    what = event.get('WHAT', '')
                    if what:
                        words = what.lower().split()
                        for word in words:
                            if word in self.concept_cache:
                                window_concepts.add(word)
                
                # Create edges between concepts in same time window
                concept_list = list(window_concepts)
                for i in range(len(concept_list)):
                    for j in range(i + 1, len(concept_list)):
                        source = concept_list[i]
                        target = concept_list[j]
                        
                        edge_id = f"{source}_{target}_temporal"
                        if edge_id not in self.edges:
                            edge = ConceptEdge(
                                source=source,
                                target=target,
                                edge_type="temporal",
                                weight=0.4,  # Medium weight for temporal proximity
                                evidence=[f"Temporal proximity: {window_start}"],
                                created_at=datetime.now().isoformat(),
                                last_updated=datetime.now().isoformat(),
                                metadata={"time_window": window_start.isoformat()}
                            )
                            self.edges[edge_id] = edge
            
            self.logger.info(f"Built {len([e for e in self.edges.values() if e.edge_type == 'temporal'])} temporal edges")
            
        except Exception as e:
            self.logger.error(f"Error building temporal edges: {e}")
    
    def _apply_accessibility_association(self):
        """
        Apply Gordon & Hobbs Accessibility by Association.
        
        When a concept is active (mentioned/detected), boost accessibility
        for associated concepts based on edge weights.
        """
        try:
            # Initialize accessibility nodes
            for concept_name in self.concept_cache.keys():
                if concept_name not in self.accessibility_nodes:
                    self.accessibility_nodes[concept_name] = AccessibilityNode(
                        concept=concept_name,
                        activation_level=0.0,
                        last_activated="",
                        associated_concepts=[],
                        accessibility_score=0.0,
                        context_history=[]
                    )
            
            # Apply accessibility based on recent events
            recent_time = datetime.now() - timedelta(hours=2)
            
            for event in self.event_cache:
                event_time = datetime.fromisoformat(event.get('timestamp', ''))
                if event_time > recent_time:
                    # Extract active concepts from event
                    active_concepts = self._extract_active_concepts(event)
                    
                    # Boost accessibility for associated concepts
                    for active_concept in active_concepts:
                        if active_concept in self.accessibility_nodes:
                            # Activate the concept
                            self.accessibility_nodes[active_concept].activation_level = 1.0
                            self.accessibility_nodes[active_concept].last_activated = event.get('timestamp', '')
                            
                            # Find associated concepts through edges
                            associated_concepts = []
                            for edge in self.edges.values():
                                if edge.source == active_concept:
                                    associated_concepts.append((edge.target, edge.weight))
                                elif edge.target == active_concept:
                                    associated_concepts.append((edge.source, edge.weight))
                            
                            # Update accessibility scores
                            for associated_concept, weight in associated_concepts:
                                if associated_concept in self.accessibility_nodes:
                                    # Boost accessibility based on edge weight
                                    boost = weight * 0.5  # Scale factor
                                    current_score = self.accessibility_nodes[associated_concept].accessibility_score
                                    self.accessibility_nodes[associated_concept].accessibility_score = min(1.0, current_score + boost)
                                    
                                    # Add to associated concepts list
                                    if associated_concept not in self.accessibility_nodes[active_concept].associated_concepts:
                                        self.accessibility_nodes[active_concept].associated_concepts.append(associated_concept)
            
            # Apply decay to activation levels
            for node in self.accessibility_nodes.values():
                if node.activation_level > 0:
                    # Decay activation over time
                    time_since_activation = datetime.now() - datetime.fromisoformat(node.last_activated)
                    decay_factor = max(0.0, 1.0 - (time_since_activation.total_seconds() / 3600) * self.activation_decay_rate)
                    node.activation_level *= decay_factor
            
            self.logger.info(f"Applied accessibility association to {len(self.accessibility_nodes)} concepts")
            
        except Exception as e:
            self.logger.error(f"Error applying accessibility association: {e}")
    
    def _extract_active_concepts(self, event: Dict) -> List[str]:
        """Extract active concepts from an event."""
        active_concepts = []
        
        # Extract from WHAT field
        what = event.get('WHAT', '')
        if what:
            words = what.lower().split()
            for word in words:
                if word in self.concept_cache:
                    active_concepts.append(word)
        
        # Extract from contexts
        for concept_name, concept_data in self.concept_cache.items():
            contexts = concept_data.get('contexts', [])
            for context in contexts:
                if context.get('timestamp') == event.get('timestamp'):
                    active_concepts.append(concept_name)
                    break
        
        return list(set(active_concepts))  # Remove duplicates
    
    def _prune_weak_edges(self):
        """Remove edges with weights below threshold."""
        try:
            edges_to_remove = []
            
            for edge_id, edge in self.edges.items():
                if edge.weight < self.min_edge_weight:
                    edges_to_remove.append(edge_id)
            
            for edge_id in edges_to_remove:
                del self.edges[edge_id]
            
            self.logger.info(f"Pruned {len(edges_to_remove)} weak edges")
            
        except Exception as e:
            self.logger.error(f"Error pruning weak edges: {e}")
    
    def _update_accessibility_scores(self):
        """Update accessibility scores based on current state."""
        try:
            for node in self.accessibility_nodes.values():
                # Base accessibility on activation level
                base_score = node.activation_level
                
                # Boost from associated concepts
                association_boost = len(node.associated_concepts) * 0.1
                
                # Final accessibility score
                node.accessibility_score = min(1.0, base_score + association_boost)
            
        except Exception as e:
            self.logger.error(f"Error updating accessibility scores: {e}")
    
    def _save_graph(self):
        """Save the concept graph to file."""
        try:
            # Convert to NetworkX format
            for edge in self.edges.values():
                # Convert lists to strings for GraphML compatibility
                evidence_str = "; ".join(edge.evidence) if edge.evidence else ""
                metadata_str = json.dumps(edge.metadata) if edge.metadata else "{}"
                
                self.graph.add_edge(
                    edge.source, 
                    edge.target, 
                    weight=edge.weight,
                    edge_type=edge.edge_type,
                    evidence=evidence_str,
                    metadata=metadata_str
                )
            
            # Save as GraphML
            nx.write_graphml(self.graph, "concept_graph.graphml")
            
            # Save accessibility data
            accessibility_data = {
                "nodes": {name: asdict(node) for name, node in self.accessibility_nodes.items()},
                "edges": {edge_id: asdict(edge) for edge_id, edge in self.edges.items()},
                "last_updated": datetime.now().isoformat()
            }
            
            with open("concept_graph_accessibility.json", 'w') as f:
                json.dump(accessibility_data, f, indent=2)
            
            self.logger.info("Saved concept graph and accessibility data")
            
        except Exception as e:
            self.logger.error(f"Error saving graph: {e}")
    
    def get_accessible_concepts(self, query_concepts: List[str], limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get concepts accessible through association with query concepts.
        
        Args:
            query_concepts: List of query concepts
            limit: Maximum number of results
            
        Returns:
            List of (concept, accessibility_score) tuples
        """
        try:
            accessibility_scores = {}
            
            for query_concept in query_concepts:
                if query_concept in self.accessibility_nodes:
                    # Get associated concepts
                    associated_concepts = self.accessibility_nodes[query_concept].associated_concepts
                    
                    for associated_concept in associated_concepts:
                        if associated_concept in self.accessibility_nodes:
                            score = self.accessibility_nodes[associated_concept].accessibility_score
                            accessibility_scores[associated_concept] = max(
                                accessibility_scores.get(associated_concept, 0),
                                score
                            )
            
            # Sort by accessibility score
            sorted_concepts = sorted(
                accessibility_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_concepts[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting accessible concepts: {e}")
            return []
    
    def activate_concept(self, concept: str, activation_strength: float = 1.0):
        """
        Activate a concept, making it available for association-based reasoning.
        
        Args:
            concept: The concept to activate
            activation_strength: Strength of activation (0.0 to 1.0)
        """
        try:
            if concept in self.accessibility_nodes:
                self.accessibility_nodes[concept].activation_level = activation_strength
                self.accessibility_nodes[concept].last_activated = datetime.now().isoformat()
                
                # Update associated concepts
                associated_concepts = []
                for edge in self.edges.values():
                    if edge.source == concept:
                        associated_concepts.append(edge.target)
                    elif edge.target == concept:
                        associated_concepts.append(edge.source)
                
                self.accessibility_nodes[concept].associated_concepts = associated_concepts
                
                self.logger.info(f"Activated concept: {concept} (strength: {activation_strength})")
            
        except Exception as e:
            self.logger.error(f"Error activating concept: {e}")
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the concept graph."""
        try:
            return {
                "total_nodes": len(self.concept_cache),
                "total_edges": len(self.edges),
                "edge_types": Counter([edge.edge_type for edge in self.edges.values()]),
                "active_concepts": len([node for node in self.accessibility_nodes.values() if node.activation_level > 0]),
                "avg_accessibility_score": sum([node.accessibility_score for node in self.accessibility_nodes.values()]) / len(self.accessibility_nodes) if self.accessibility_nodes else 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting graph summary: {e}")
            return {}

    def get_edges_for_concept(self, concept: str) -> List[ConceptEdge]:
        """Get all edges connected to a specific concept."""
        edges = []
        for edge_id, edge in self.edges.items():
            if edge.source == concept or edge.target == concept:
                edges.append(edge)
        return edges

    def query_related(self, node: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Query related concepts using Accessibility by Association.
        
        Args:
            node: Source concept
            k: Number of results to return
            
        Returns:
            List of (concept, score) tuples sorted by accessibility score
        """
        try:
            if node not in self.concept_cache:
                self.logger.warning(f"Concept '{node}' not found in graph")
                return []
            
            # Get all edges connected to this concept
            connected_edges = self.get_edges_for_concept(node)
            
            # Calculate accessibility scores for connected concepts
            accessibility_scores = {}
            
            for edge in connected_edges:
                # Determine the connected concept
                connected_concept = edge.target if edge.source == node else edge.source
                
                # Calculate base accessibility score from edge weight
                base_score = edge.weight
                
                # Apply Accessibility by Association boosts
                boosted_score = self._apply_accessibility_boosts(connected_concept, edge, base_score)
                
                # Store the highest score for each concept
                if connected_concept in accessibility_scores:
                    accessibility_scores[connected_concept] = max(
                        accessibility_scores[connected_concept], 
                        boosted_score
                    )
                else:
                    accessibility_scores[connected_concept] = boosted_score
            
            # Sort by accessibility score (descending)
            sorted_concepts = sorted(
                accessibility_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return top k results
            return sorted_concepts[:k]
            
        except Exception as e:
            self.logger.error(f"Error querying related concepts for '{node}': {e}")
            return []

    def _apply_accessibility_boosts(self, concept: str, edge: ConceptEdge, base_score: float) -> float:
        """
        Apply Accessibility by Association boosts to a concept's accessibility score.
        
        Args:
            concept: The concept being evaluated
            edge: The edge connecting to this concept
            base_score: Base accessibility score
            
        Returns:
            Boosted accessibility score
        """
        boosted_score = base_score
        
        # Boost 1: Recent activation
        if concept in self.accessibility_nodes:
            node = self.accessibility_nodes[concept]
            if node.activation_level > 0:
                # Recent activation provides a boost
                activation_boost = node.activation_level * 0.3
                boosted_score += activation_boost
        
        # Boost 2: Edge type specific boosts
        edge_type_boosts = {
            "goal_shared": 0.2,      # High boost for shared goals
            "need_shared": 0.15,     # Medium-high boost for shared needs
            "co_occurrence": 0.1,    # Medium boost for co-occurrence
            "semantic": 0.05,        # Low boost for semantic similarity
            "temporal": 0.08         # Medium-low boost for temporal proximity
        }
        
        edge_boost = edge_type_boosts.get(edge.edge_type, 0.0)
        boosted_score += edge_boost
        
        # Boost 3: Evidence strength
        evidence_count = len(edge.evidence)
        evidence_boost = min(evidence_count * 0.05, 0.2)  # Max 0.2 boost
        boosted_score += evidence_boost
        
        # Boost 4: Recency of edge update
        try:
            last_updated = datetime.fromisoformat(edge.last_updated)
            time_diff = (datetime.now() - last_updated).total_seconds()
            if time_diff < 3600:  # Within last hour
                recency_boost = 0.1
            elif time_diff < 86400:  # Within last day
                recency_boost = 0.05
            else:
                recency_boost = 0.0
            boosted_score += recency_boost
        except:
            pass  # Ignore timestamp parsing errors
        
        # Clamp to valid range
        return min(1.0, max(0.0, boosted_score))

    def update_from_event(self, event: Dict[str, Any]) -> None:
        """
        Update concept graph from an event.
        
        Args:
            event: Event dictionary with concepts, goals, needs, etc.
        """
        try:
            # Extract concepts from event
            concepts = event.get('concepts', [])
            goals = event.get('goals', [])
            needs = event.get('needs', [])
            
            if not concepts:
                return
            
            # Add concepts to graph if they don't exist
            for concept in concepts:
                if concept not in self.concept_cache:
                    self.concept_cache[concept] = {
                        'name': concept,
                        'type': 'concept',
                        'created_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
            
            # Create co-occurrence edges between concepts in this event
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    self._create_or_strengthen_edge(concept1, concept2, "co_occurrence", 0.1)
            
            # Create goal-shared edges
            for goal in goals:
                for concept1 in concepts:
                    for concept2 in concepts:
                        if concept1 != concept2:
                            self._create_or_strengthen_edge(concept1, concept2, "goal_shared", 0.2)
            
            # Create need-shared edges
            for need in needs:
                for concept1 in concepts:
                    for concept2 in concepts:
                        if concept1 != concept2:
                            self._create_or_strengthen_edge(concept1, concept2, "need_shared", 0.15)
            
            # Update accessibility nodes
            self._update_accessibility_nodes()
            
            self.logger.info(f"Updated concept graph from event with {len(concepts)} concepts")
            
        except Exception as e:
            self.logger.error(f"Error updating concept graph from event: {e}")

    def _create_or_strengthen_edge(self, source: str, target: str, edge_type: str, weight_increment: float):
        """Create a new edge or strengthen an existing one."""
        edge_id = f"{source}_{target}_{edge_type}"
        
        if edge_id in self.edges:
            # Strengthen existing edge
            edge = self.edges[edge_id]
            edge.weight = min(1.0, edge.weight + weight_increment)
            edge.last_updated = datetime.now().isoformat()
            edge.evidence.append(f"Event update: {datetime.now().isoformat()}")
        else:
            # Create new edge
            edge = ConceptEdge(
                source=source,
                target=target,
                edge_type=edge_type,
                weight=0.3 + weight_increment,  # Base weight + increment
                evidence=[f"Event update: {datetime.now().isoformat()}"],
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                metadata={"source": "event_update"}
            )
            self.edges[edge_id] = edge

    def add_association(self, source: str, target: str, edge_type: str, weight: float):
        """
        Add an association between two concepts.
        
        Args:
            source: Source concept
            target: Target concept
            edge_type: Type of association (e.g., 'related_to_goal', 'related_to_need', etc.)
            weight: Association strength (0.0 to 1.0)
        """
        try:
            # 🔧 ENHANCEMENT: Rate limiting for repetitive associations
            current_time = time.time()
            association_key = f"{source}→{target}→{edge_type}"
            
            # Clean old entries
            self.association_rate_limit = {
                k: v for k, v in self.association_rate_limit.items() 
                if current_time - v < self.rate_limit_window
            }
            
            # Check if we're exceeding rate limit
            if association_key in self.association_rate_limit:
                # Count how many times this association was added recently
                recent_count = sum(1 for k, v in self.association_rate_limit.items() 
                                 if k == association_key and current_time - v < self.rate_limit_window)
                if recent_count >= self.max_associations_per_window:
                    # Rate limited - skip this association
                    return
            
            # Record this association
            self.association_rate_limit[association_key] = current_time
            # Ensure concepts exist in cache
            if source not in self.concept_cache:
                self.concept_cache[source] = {
                    'name': source,
                    'type': 'concept',
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            
            if target not in self.concept_cache:
                self.concept_cache[target] = {
                    'name': target,
                    'type': 'concept',
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            
            # Create or strengthen the edge
            self._create_or_strengthen_edge(source, target, edge_type, weight)
            
            # Update accessibility nodes
            self._update_accessibility_nodes()
            
            self.logger.info(f"Added association: {source} -> {target} ({edge_type}, weight={weight})")
            
        except Exception as e:
            self.logger.error(f"Error adding association: {e}")

    def _update_accessibility_nodes(self):
        """Update accessibility nodes based on current graph state."""
        try:
            for concept in self.concept_cache:
                if concept not in self.accessibility_nodes:
                    # Create new accessibility node
                    self.accessibility_nodes[concept] = AccessibilityNode(
                        concept=concept,
                        activation_level=0.0,
                        last_activated=datetime.now().isoformat(),
                        associated_concepts=[],
                        accessibility_score=0.5,  # Default score
                        context_history=[]
                    )
                
                # Update associated concepts
                associated_concepts = []
                for edge in self.edges.values():
                    if edge.source == concept:
                        associated_concepts.append(edge.target)
                    elif edge.target == concept:
                        associated_concepts.append(edge.source)
                
                self.accessibility_nodes[concept].associated_concepts = associated_concepts
                
                # Update accessibility score based on connected edges
                if associated_concepts:
                    avg_edge_weight = sum(
                        edge.weight for edge in self.edges.values()
                        if edge.source == concept or edge.target == concept
                    ) / len(associated_concepts)
                    self.accessibility_nodes[concept].accessibility_score = min(1.0, avg_edge_weight)
                
        except Exception as e:
            self.logger.error(f"Error updating accessibility nodes: {e}")

# Global instance
concept_graph_system = ConceptGraphSystem()
