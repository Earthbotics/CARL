#!/usr/bin/env python3
"""
Concept Linking System for CARL

This system links related concepts to enable better understanding and cross-referencing.
For example, linking "chomp" (basic word) with "chomp_and_count_dino" (specific toy).
"""

import json
import os
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

class ConceptLinkingSystem:
    """
    System for linking related concepts to improve CARL's understanding.
    """
    
    def __init__(self, concepts_dir: str = "concepts"):
        """
        Initialize the concept linking system.
        
        Args:
            concepts_dir: Directory containing concept files
        """
        self.concepts_dir = concepts_dir
        self.links_file = "concept_links.json"
        self.logger = logging.getLogger(__name__)
        
        # Load existing links
        self.concept_links = self._load_concept_links()
        
        # Define known concept relationships
        self.known_relationships = {
            "chomp": ["chomp_and_count_dino"],
            "dino": ["chomp_and_count_dino"],
            "dinosaur": ["chomp_and_count_dino"],
            "toy": ["chomp_and_count_dino"],
            "vtech": ["chomp_and_count_dino"],
            "educational": ["chomp_and_count_dino"],
            "counting": ["chomp_and_count_dino"],
            "food": ["chomp_and_count_dino"]
        }
    
    def _load_concept_links(self) -> Dict:
        """Load existing concept links from file."""
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load concept links: {e}")
        
        return {}
    
    def _save_concept_links(self):
        """Save concept links to file."""
        try:
            with open(self.links_file, 'w', encoding='utf-8') as f:
                json.dump(self.concept_links, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save concept links: {e}")
    
    def link_concepts(self, source_concept: str, target_concept: str, relationship_type: str = "related"):
        """
        Link two concepts together.
        
        Args:
            source_concept: The source concept name
            target_concept: The target concept name
            relationship_type: Type of relationship (related, synonym, specific, etc.)
        """
        if source_concept not in self.concept_links:
            self.concept_links[source_concept] = []
        
        # Check if link already exists
        existing_link = next((link for link in self.concept_links[source_concept] 
                            if link['concept'] == target_concept), None)
        
        if not existing_link:
            link_data = {
                'concept': target_concept,
                'relationship': relationship_type,
                'created': datetime.now().isoformat(),
                'strength': 1.0
            }
            self.concept_links[source_concept].append(link_data)
            self.logger.info(f"Linked '{source_concept}' to '{target_concept}' ({relationship_type})")
        else:
            # Update existing link
            existing_link['strength'] = min(1.0, existing_link['strength'] + 0.1)
            existing_link['last_updated'] = datetime.now().isoformat()
            self.logger.info(f"Strengthened link between '{source_concept}' and '{target_concept}'")
        
        self._save_concept_links()
    
    def get_related_concepts(self, concept_name: str) -> List[Dict]:
        """
        Get all concepts related to a given concept.
        
        Args:
            concept_name: Name of the concept to find related concepts for
            
        Returns:
            List of related concept dictionaries
        """
        return self.concept_links.get(concept_name, [])
    
    def find_concept_by_keyword(self, keyword: str) -> List[str]:
        """
        Find concepts that might match a keyword.
        
        Args:
            keyword: The keyword to search for
            
        Returns:
            List of concept names that might match
        """
        matches = []
        
        # Check direct matches
        if keyword in self.concept_links:
            matches.extend([link['concept'] for link in self.concept_links[keyword]])
        
        # Check known relationships
        if keyword in self.known_relationships:
            matches.extend(self.known_relationships[keyword])
        
        # Check all concepts for keyword matches
        for concept_name, links in self.concept_links.items():
            for link in links:
                if keyword.lower() in link['concept'].lower():
                    matches.append(link['concept'])
        
        return list(set(matches))  # Remove duplicates
    
    def update_concept_references(self, concept_name: str):
        """
        Update a concept file to include references to related concepts.
        
        Args:
            concept_name: Name of the concept to update
        """
        concept_file = os.path.join(self.concepts_dir, f"{concept_name}.json")
        
        if not os.path.exists(concept_file):
            self.logger.warning(f"Concept file not found: {concept_file}")
            return
        
        try:
            # Load the concept file
            with open(concept_file, 'r', encoding='utf-8') as f:
                concept_data = json.load(f)
            
            # Get related concepts
            related_concepts = self.get_related_concepts(concept_name)
            
            # Update the concept data
            if 'linked_concepts' not in concept_data:
                concept_data['linked_concepts'] = []
            
            # Add new links
            for link in related_concepts:
                if link['concept'] not in concept_data['linked_concepts']:
                    concept_data['linked_concepts'].append(link['concept'])
            
            # Save the updated concept file
            with open(concept_file, 'w', encoding='utf-8') as f:
                json.dump(concept_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Updated concept '{concept_name}' with {len(related_concepts)} links")
            
        except Exception as e:
            self.logger.error(f"Error updating concept '{concept_name}': {e}")
    
    def create_initial_links(self):
        """Create initial concept links based on known relationships."""
        self.logger.info("Creating initial concept links...")
        
        for source, targets in self.known_relationships.items():
            for target in targets:
                self.link_concepts(source, target, "specific")
                self.link_concepts(target, source, "general")
        
        self.logger.info("Initial concept links created")
    
    def suggest_concept_links(self, concept_name: str) -> List[str]:
        """
        Suggest potential concept links based on content analysis.
        
        Args:
            concept_name: Name of the concept to analyze
            
        Returns:
            List of suggested concept names to link
        """
        concept_file = os.path.join(self.concepts_dir, f"{concept_name}.json")
        
        if not os.path.exists(concept_file):
            return []
        
        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                concept_data = json.load(f)
            
            suggestions = []
            
            # Check keywords for potential matches
            keywords = concept_data.get('keywords', [])
            for keyword in keywords:
                if keyword in self.known_relationships:
                    suggestions.extend(self.known_relationships[keyword])
            
            # Check related concepts for potential matches
            related_concepts = concept_data.get('related_concepts', [])
            for related in related_concepts:
                if related in self.known_relationships:
                    suggestions.extend(self.known_relationships[related])
            
            return list(set(suggestions))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error suggesting links for '{concept_name}': {e}")
            return []

def main():
    """Main function to set up concept linking."""
    linking_system = ConceptLinkingSystem()
    
    # Create initial links
    linking_system.create_initial_links()
    
    # Update existing concepts with links
    linking_system.update_concept_references("chomp_self_learned")
    linking_system.update_concept_references("chomp_and_count_dino")
    
    print("✅ Concept linking system initialized")
    print("✅ Initial links created between chomp and chomp_and_count_dino")

if __name__ == "__main__":
    main()
