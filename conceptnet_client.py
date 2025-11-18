import requests
import json
import time
from typing import Dict, List, Optional
import logging

class ConceptNetClient:
    """Client for interacting with ConceptNet API to enhance CARL's common sense reasoning."""
    
    def __init__(self):
        self.base_url = "http://api.conceptnet.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CARL-AI-Robot/5.9.0'
        })
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to be respectful to the API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def query_concept(self, concept: str, limit: int = 10) -> Dict:
        """
        Query ConceptNet for a concept and return the top weighted edges.
        Validates that the concept is a single word for optimal API performance.
        
        Args:
            concept: The concept to query (should be a single word)
            limit: Maximum number of edges to return (default 10)
            
        Returns:
            Dict containing ConceptNet data with edges and relationships
        """
        try:
            self._rate_limit()
            
            # Validate that concept is a single word
            import re
            words = re.findall(r'\b\w+\b', concept.lower())
            if len(words) != 1:
                logging.warning(f"ConceptNet query expects single word, got: '{concept}' (extracted: {words})")
                if not words:
                    return {
                        'has_data': False,
                        'last_lookup': time.time(),
                        'edges': [],
                        'relationships': [],
                        'error': 'No valid word found',
                        'concept_queried': concept
                    }
                # Use the first word if multiple found
                concept = words[0]
                logging.info(f"Using first word for ConceptNet query: '{concept}'")
            
            # Clean the concept for API query
            clean_concept = concept.lower().replace(' ', '_')
            
            # Query ConceptNet API
            url = f"{self.base_url}/query"
            params = {
                'start': f'/c/en/{clean_concept}',
                'limit': limit,
                'filter': '/c/en'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the edges
            edges = []
            relationships = []
            
            for edge in data.get('edges', []):
                # Extract relationship information
                rel = edge.get('rel', {})
                weight = edge.get('weight', 0)
                
                # Get the target concept
                end = edge.get('end', {})
                target = end.get('label', '') if end else ''
                
                if target and weight > 0.1:  # Only include meaningful relationships
                    edge_info = {
                        'target': target,
                        'relationship': rel.get('label', ''),
                        'weight': weight,
                        'uri': edge.get('@id', '')
                    }
                    edges.append(edge_info)
                    
                    # Add to relationships list
                    rel_type = rel.get('label', '')
                    if rel_type and rel_type not in relationships:
                        relationships.append(rel_type)
            
            # Sort edges by weight (highest first)
            edges.sort(key=lambda x: x['weight'], reverse=True)
            
            return {
                'has_data': len(edges) > 0,
                'last_lookup': time.time(),
                'edges': edges[:limit],
                'relationships': relationships,
                'total_edges_found': len(data.get('edges', [])),
                'concept_queried': concept,
                'single_word_validated': True
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"ConceptNet API request failed for '{concept}': {e}")
            return {
                'has_data': False,
                'last_lookup': time.time(),
                'edges': [],
                'relationships': [],
                'error': str(e),
                'concept_queried': concept
            }
        except Exception as e:
            logging.error(f"Unexpected error querying ConceptNet for '{concept}': {e}")
            return {
                'has_data': False,
                'last_lookup': time.time(),
                'edges': [],
                'relationships': [],
                'error': str(e),
                'concept_queried': concept
            }
    
    def get_common_sense_relationships(self, concept: str) -> List[Dict]:
        """
        Get common sense relationships for a concept.
        This focuses on the most important relationships for understanding.
        
        Args:
            concept: The concept to get relationships for
            
        Returns:
            List of relationship dictionaries
        """
        result = self.query_concept(concept, limit=15)
        
        if not result['has_data']:
            return []
        
        # Filter for the most meaningful relationships
        meaningful_relationships = []
        for edge in result['edges']:
            rel_type = edge['relationship']
            weight = edge['weight']
            
            # Focus on high-weight relationships and common sense types
            if weight > 0.5 or rel_type in [
                'IsA', 'PartOf', 'UsedFor', 'CapableOf', 'HasProperty',
                'Causes', 'Desires', 'LocatedNear', 'SimilarTo', 'RelatedTo'
            ]:
                meaningful_relationships.append({
                    'target': edge['target'],
                    'relationship': rel_type,
                    'weight': weight,
                    'confidence': min(weight * 2, 1.0)  # Convert weight to confidence
                })
        
        return meaningful_relationships[:10]  # Return top 10
    
    def validate_concept_knowledge(self, concept: str, existing_knowledge: Dict) -> Dict:
        """
        Validate and enhance existing concept knowledge with ConceptNet data.
        
        Args:
            concept: The concept to validate
            existing_knowledge: Current concept knowledge
            
        Returns:
            Enhanced knowledge with ConceptNet validation
        """
        # Get fresh ConceptNet data
        conceptnet_data = self.query_concept(concept, limit=10)
        
        # Check if we have new or conflicting information
        validation_result = {
            'concept': concept,
            'has_conceptnet_data': conceptnet_data['has_data'],
            'existing_relationships': len(existing_knowledge.get('conceptnet_data', {}).get('edges', [])),
            'new_relationships': len(conceptnet_data.get('edges', [])),
            'validation_score': 0.0,
            'enhanced_knowledge': existing_knowledge.copy()
        }
        
        if conceptnet_data['has_data']:
            # Update the concept knowledge with fresh ConceptNet data
            validation_result['enhanced_knowledge']['conceptnet_data'] = conceptnet_data
            
            # Calculate validation score based on relationship consistency
            existing_edges = existing_knowledge.get('conceptnet_data', {}).get('edges', [])
            new_edges = conceptnet_data.get('edges', [])
            
            if existing_edges and new_edges:
                # Check for consistency between existing and new knowledge
                existing_targets = {edge.get('target', '') for edge in existing_edges}
                new_targets = {edge.get('target', '') for edge in new_edges}
                
                overlap = len(existing_targets.intersection(new_targets))
                total_unique = len(existing_targets.union(new_targets))
                
                if total_unique > 0:
                    validation_result['validation_score'] = overlap / total_unique
            
            # Add common sense validation
            validation_result['common_sense_relationships'] = self.get_common_sense_relationships(concept)
        
        return validation_result
    
    def batch_query_concepts(self, concepts: List[str], delay: float = 0.2) -> Dict[str, Dict]:
        """
        Query multiple concepts with rate limiting.
        
        Args:
            concepts: List of concepts to query
            delay: Delay between queries in seconds
            
        Returns:
            Dictionary mapping concepts to their ConceptNet data
        """
        results = {}
        
        for concept in concepts:
            results[concept] = self.query_concept(concept)
            time.sleep(delay)  # Be respectful to the API
        
        return results

# Global instance for use throughout CARL
conceptnet_client = ConceptNetClient() 