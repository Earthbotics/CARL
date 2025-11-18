"""
Concept Graph System with Accessibility by Association

Implements incremental co-occurrence linking and accessibility scoring based on
Gordon & Hobbs "Accessibility by Association" principles.
"""

import time
import math
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class ConceptEdge:
    """Represents an edge between concepts in the graph."""
    source: str
    target: str
    weight: float
    edge_type: str  # "co_occurrence", "shared_goal", "shared_need", "temporal"
    last_seen: float
    decay_rate: float = 0.1


@dataclass
class AccessibilityNode:
    """Represents a concept node with accessibility information."""
    concept: str
    base_score: float
    boosted_score: float
    boost_factors: List[str]
    last_activation: float


class ConceptGraphSystem:
    """Manages concept graph with accessibility by association."""
    
    def __init__(self):
        self.edges: Dict[Tuple[str, str], ConceptEdge] = {}
        self.nodes: Set[str] = set()
        self.recent_events: List[Dict[str, Any]] = []
        self.max_events = 50  # Keep last 50 events for temporal analysis
        
        # Accessibility parameters
        self.temporal_decay_half_life = 300.0  # 5 minutes
        self.co_occurrence_boost = 0.3
        self.shared_goal_boost = 0.4
        self.shared_need_boost = 0.4
        self.temporal_proximity_boost = 0.2
        
        # Event tracking
        self.event_concepts: Dict[str, Set[str]] = {}  # event_id -> concepts
        self.concept_goals: Dict[str, Set[str]] = defaultdict(set)
        self.concept_needs: Dict[str, Set[str]] = defaultdict(set)
    
    def update_from_event(self, event_ctx: Dict[str, Any]) -> None:
        """
        Update graph from an event context.
        
        Args:
            event_ctx: Event context with concepts, goals, needs, etc.
        """
        event_id = event_ctx.get("event_id", f"evt_{time.time()}")
        concepts = event_ctx.get("concepts", [])
        goals = event_ctx.get("goals", [])
        needs = event_ctx.get("needs", [])
        timestamp = time.time()
        
        # Add concepts to nodes
        for concept in concepts:
            self.nodes.add(concept)
        
        # Store event for temporal analysis
        self.recent_events.append({
            "event_id": event_id,
            "concepts": concepts,
            "goals": goals,
            "needs": needs,
            "timestamp": timestamp
        })
        
        # Trim old events
        if len(self.recent_events) > self.max_events:
            self.recent_events.pop(0)
        
        # Store event concepts
        self.event_concepts[event_id] = set(concepts)
        
        # Update concept-goal and concept-need mappings
        for concept in concepts:
            self.concept_goals[concept].update(goals)
            self.concept_needs[concept].update(needs)
        
        # Create co-occurrence edges
        self._create_co_occurrence_edges(concepts, timestamp)
        
        # Create shared goal/need edges
        self._create_shared_association_edges(concepts, goals, needs, timestamp)
        
        # Apply temporal decay to existing edges
        self._apply_temporal_decay(timestamp)
    
    def query_related(self, node: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Query related concepts using accessibility by association.
        
        Args:
            node: Source concept
            k: Number of results to return
            
        Returns:
            List of (concept, score) tuples sorted by score
        """
        if node not in self.nodes:
            return []
        
        # Calculate accessibility scores
        accessibility_scores = {}
        current_time = time.time()
        
        for concept in self.nodes:
            if concept == node:
                continue
            
            base_score = self._calculate_base_score(node, concept)
            boosted_score = self._calculate_boosted_score(node, concept, current_time)
            
            accessibility_scores[concept] = boosted_score
        
        # Sort by score and return top k
        sorted_concepts = sorted(
            accessibility_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_concepts[:k]
    
    def get_edges_for_concept(self, concept: str) -> List[ConceptEdge]:
        """Get all edges connected to a concept."""
        edges = []
        for edge in self.edges.values():
            if edge.source == concept or edge.target == concept:
                edges.append(edge)
        return edges
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        total_edges = len(self.edges)
        total_nodes = len(self.nodes)
        
        # Count edge types
        edge_types = Counter(edge.edge_type for edge in self.edges.values())
        
        # Calculate average weights
        weights = [edge.weight for edge in self.edges.values()]
        avg_weight = sum(weights) / len(weights) if weights else 0.0
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "edge_types": dict(edge_types),
            "average_weight": avg_weight,
            "recent_events": len(self.recent_events)
        }
    
    def _create_co_occurrence_edges(self, concepts: List[str], timestamp: float) -> None:
        """Create co-occurrence edges between concepts in the same event."""
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                edge_key = (concept1, concept2)
                reverse_key = (concept2, concept1)
                
                # Use the canonical edge key (alphabetical order)
                if concept1 > concept2:
                    edge_key, reverse_key = reverse_key, edge_key
                
                if edge_key in self.edges:
                    # Strengthen existing edge
                    edge = self.edges[edge_key]
                    edge.weight = min(1.0, edge.weight + 0.1)
                    edge.last_seen = timestamp
                else:
                    # Create new edge
                    self.edges[edge_key] = ConceptEdge(
                        source=edge_key[0],
                        target=edge_key[1],
                        weight=0.3,
                        edge_type="co_occurrence",
                        last_seen=timestamp
                    )
    
    def _create_shared_association_edges(self, concepts: List[str], goals: List[str], needs: List[str], timestamp: float) -> None:
        """Create edges based on shared goals and needs."""
        # Create shared goal edges
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                shared_goals = self.concept_goals[concept1] & self.concept_goals[concept2]
                if shared_goals:
                    self._create_or_strengthen_edge(
                        concept1, concept2, "shared_goal", timestamp, len(shared_goals) * 0.1
                    )
                
                shared_needs = self.concept_needs[concept1] & self.concept_needs[concept2]
                if shared_needs:
                    self._create_or_strengthen_edge(
                        concept1, concept2, "shared_need", timestamp, len(shared_needs) * 0.1
                    )
    
    def _create_or_strengthen_edge(self, concept1: str, concept2: str, edge_type: str, timestamp: float, weight_boost: float) -> None:
        """Create or strengthen an edge between two concepts."""
        edge_key = (concept1, concept2) if concept1 < concept2 else (concept2, concept1)
        
        if edge_key in self.edges:
            edge = self.edges[edge_key]
            edge.weight = min(1.0, edge.weight + weight_boost)
            edge.last_seen = timestamp
        else:
            self.edges[edge_key] = ConceptEdge(
                source=edge_key[0],
                target=edge_key[1],
                weight=0.2 + weight_boost,
                edge_type=edge_type,
                last_seen=timestamp
            )
    
    def _apply_temporal_decay(self, current_time: float) -> None:
        """Apply temporal decay to edge weights."""
        edges_to_remove = []
        
        for edge_key, edge in self.edges.items():
            time_diff = current_time - edge.last_seen
            if time_diff > 0:
                # Apply exponential decay
                decay_factor = math.exp(-time_diff / self.temporal_decay_half_life)
                edge.weight *= decay_factor
                
                # Remove very weak edges
                if edge.weight < 0.05:
                    edges_to_remove.append(edge_key)
        
        # Remove weak edges
        for edge_key in edges_to_remove:
            del self.edges[edge_key]
    
    def _calculate_base_score(self, source: str, target: str) -> float:
        """Calculate base accessibility score between concepts."""
        edge_key = (source, target) if source < target else (target, source)
        
        if edge_key in self.edges:
            edge = self.edges[edge_key]
            return edge.weight
        else:
            return 0.0
    
    def _calculate_boosted_score(self, source: str, target: str, current_time: float) -> float:
        """Calculate boosted accessibility score using Gordon & Hobbs principles."""
        base_score = self._calculate_base_score(source, target)
        boosted_score = base_score
        boost_factors = []
        
        # Boost 1: Recent co-occurrence
        recent_co_occurrence = self._check_recent_co_occurrence(source, target, current_time)
        if recent_co_occurrence:
            boosted_score += self.co_occurrence_boost
            boost_factors.append("recent_co_occurrence")
        
        # Boost 2: Shared goals
        shared_goals = self.concept_goals[source] & self.concept_goals[target]
        if shared_goals:
            boosted_score += self.shared_goal_boost * len(shared_goals)
            boost_factors.append(f"shared_goals({len(shared_goals)})")
        
        # Boost 3: Shared needs
        shared_needs = self.concept_needs[source] & self.concept_needs[target]
        if shared_needs:
            boosted_score += self.shared_need_boost * len(shared_needs)
            boost_factors.append(f"shared_needs({len(shared_needs)})")
        
        # Boost 4: Temporal proximity in recent events
        temporal_boost = self._calculate_temporal_proximity(source, target, current_time)
        if temporal_boost > 0:
            boosted_score += temporal_boost
            boost_factors.append("temporal_proximity")
        
        return min(1.0, boosted_score)
    
    def _check_recent_co_occurrence(self, source: str, target: str, current_time: float) -> bool:
        """Check if concepts co-occurred in recent events."""
        time_window = 300.0  # 5 minutes
        
        for event in self.recent_events:
            if current_time - event["timestamp"] <= time_window:
                event_concepts = set(event["concepts"])
                if source in event_concepts and target in event_concepts:
                    return True
        
        return False
    
    def _calculate_temporal_proximity(self, source: str, target: str, current_time: float) -> float:
        """Calculate temporal proximity boost between concepts."""
        source_events = []
        target_events = []
        
        # Find recent events containing each concept
        for event in self.recent_events:
            if current_time - event["timestamp"] <= 600.0:  # 10 minutes
                if source in event["concepts"]:
                    source_events.append(event["timestamp"])
                if target in event["concepts"]:
                    target_events.append(event["timestamp"])
        
        # Calculate minimum time difference
        min_time_diff = float('inf')
        for source_time in source_events:
            for target_time in target_events:
                time_diff = abs(source_time - target_time)
                min_time_diff = min(min_time_diff, time_diff)
        
        if min_time_diff == float('inf'):
            return 0.0
        
        # Convert to boost (closer events = higher boost)
        proximity_boost = self.temporal_proximity_boost * math.exp(-min_time_diff / 60.0)
        return proximity_boost


# Global instance
concept_graph = ConceptGraphSystem()


def update_from_event(event_ctx: Dict[str, Any]) -> None:
    """Convenience function to update graph from event."""
    concept_graph.update_from_event(event_ctx)


def query_related(node: str, k: int = 5) -> List[Tuple[str, float]]:
    """Convenience function to query related concepts."""
    return concept_graph.query_related(node, k)


def get_edges_for_concept(concept: str) -> List[ConceptEdge]:
    """Convenience function to get edges for concept."""
    return concept_graph.get_edges_for_concept(concept)


def get_graph_stats() -> Dict[str, Any]:
    """Convenience function to get graph statistics."""
    return concept_graph.get_graph_stats()
