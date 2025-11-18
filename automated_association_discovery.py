#!/usr/bin/env python3
"""
Automated Association Discovery System for CARL

This system automatically discovers and creates associations between CARL's files
based on keyword matching, semantic similarity, and ConceptNet integration.

Key Features:
- Keyword-based association discovery
- Semantic similarity analysis
- ConceptNet integration for enhanced linking
- Automatic cross-referencing when new keywords are created
- Real-time association updates
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import logging
from difflib import SequenceMatcher

class AutomatedAssociationDiscovery:
    """
    Automated system for discovering associations between CARL's files.
    """
    
    def __init__(self):
        """Initialize the automated association discovery system."""
        self.logger = logging.getLogger(__name__)
        
        # Define base directories
        self.directories = {
            'goals': 'goals',
            'needs': 'needs', 
            'skills': 'skills',
            'senses': 'senses',
            'concepts': 'concepts',
            'people': 'people'
        }
        
        # Keyword patterns for different categories
        self.keyword_patterns = {
            'exercise': {
                'keywords': ['exercise', 'fitness', 'workout', 'physical', 'movement', 'sport', 'training', 'strength'],
                'related_terms': ['health', 'wellness', 'activity', 'energy', 'endurance']
            },
            'people': {
                'keywords': ['social', 'interaction', 'communication', 'greeting', 'conversation', 'relationship'],
                'related_terms': ['friend', 'family', 'community', 'connection', 'bond']
            },
            'pleasure': {
                'keywords': ['fun', 'enjoyment', 'entertainment', 'happiness', 'joy', 'pleasure', 'amusement'],
                'related_terms': ['play', 'game', 'music', 'dance', 'laugh']
            },
            'production': {
                'keywords': ['work', 'task', 'goal', 'achievement', 'creation', 'thinking', 'problem'],
                'related_terms': ['project', 'result', 'outcome', 'success', 'accomplishment']
            },
            'exploration': {
                'keywords': ['discover', 'learn', 'investigate', 'explore', 'curiosity', 'question'],
                'related_terms': ['new', 'unknown', 'mystery', 'adventure', 'finding']
            },
            'love': {
                'keywords': ['affection', 'care', 'friendship', 'relationship', 'bond', 'love'],
                'related_terms': ['warmth', 'kindness', 'compassion', 'empathy', 'connection']
            },
            'play': {
                'keywords': ['fun', 'game', 'entertainment', 'activity', 'amusement', 'play'],
                'related_terms': ['toy', 'dance', 'music', 'laugh', 'enjoy']
            },
            'safety': {
                'keywords': ['protection', 'security', 'safe', 'careful', 'caution', 'safety'],
                'related_terms': ['shield', 'guard', 'defend', 'secure', 'protect']
            },
            'security': {
                'keywords': ['stability', 'protection', 'safety', 'reliable', 'secure', 'security'],
                'related_terms': ['stable', 'steady', 'dependable', 'trustworthy', 'consistent']
            }
        }
        
        # Semantic similarity thresholds
        self.similarity_threshold = 0.7
        self.keyword_match_threshold = 0.8
        
        # Load ConceptNet client if available
        self.conceptnet_client = None
        try:
            from conceptnet_client import conceptnet_client
            self.conceptnet_client = conceptnet_client
            self.logger.info("ConceptNet client loaded successfully")
        except ImportError:
            self.logger.warning("ConceptNet client not available")
    
    def discover_associations_for_file(self, filepath: str) -> Dict:
        """
        Discover associations for a specific file based on its content.
        
        Args:
            filepath: Path to the file to analyze
            
        Returns:
            Dictionary of discovered associations
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract keywords and text content
            keywords = self._extract_keywords(data)
            text_content = self._extract_text_content(data)
            
            # Discover associations
            associations = {
                'linked_goals': [],
                'linked_needs': [],
                'linked_skills': [],
                'linked_senses': [],
                'associated_concepts': []
            }
            
            # Keyword-based associations
            keyword_associations = self._discover_keyword_associations(keywords, text_content)
            for key, value in keyword_associations.items():
                associations[key].extend(value)
            
            # Semantic similarity associations
            semantic_associations = self._discover_semantic_associations(keywords, text_content)
            for key, value in semantic_associations.items():
                associations[key].extend(value)
            
            # ConceptNet associations
            if self.conceptnet_client:
                conceptnet_associations = self._discover_conceptnet_associations(keywords)
                for key, value in conceptnet_associations.items():
                    associations[key].extend(value)
            
            # Remove duplicates
            for key in associations:
                associations[key] = list(set(associations[key]))
            
            return associations
            
        except Exception as e:
            self.logger.error(f"Error discovering associations for {filepath}: {e}")
            return {}
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract keywords from file data."""
        keywords = []
        
        # Extract from various fields
        keyword_fields = ['keywords', 'activation_keywords', 'Concepts', 'Motivators']
        for field in keyword_fields:
            if field in data and isinstance(data[field], list):
                keywords.extend(data[field])
        
        # Extract from name field
        if 'name' in data:
            keywords.append(data['name'])
        if 'Name' in data:
            keywords.append(data['Name'])
        
        # Extract from word field (concepts)
        if 'word' in data:
            keywords.append(data['word'])
        
        # Clean and normalize keywords
        cleaned_keywords = []
        for keyword in keywords:
            if isinstance(keyword, str):
                # Clean the keyword
                cleaned = re.sub(r'[^\w\s]', '', keyword.lower()).strip()
                if cleaned and len(cleaned) > 2:
                    cleaned_keywords.append(cleaned)
        
        return list(set(cleaned_keywords))
    
    def _extract_text_content(self, data: Dict) -> str:
        """Extract text content from file data for semantic analysis."""
        text_parts = []
        
        # Extract from various text fields
        text_fields = ['contextual_usage', 'semantic_relationships', 'prerequisites', 'future_steps']
        for field in text_fields:
            if field in data:
                if isinstance(data[field], list):
                    text_parts.extend(data[field])
                elif isinstance(data[field], str):
                    text_parts.append(data[field])
        
        # Extract from skill class
        if 'skill_class' in data and isinstance(data['skill_class'], dict):
            for value in data['skill_class'].values():
                if isinstance(value, str):
                    text_parts.append(value)
        
        return ' '.join(text_parts).lower()
    
    def _discover_keyword_associations(self, keywords: List[str], text_content: str) -> Dict:
        """Discover associations based on keyword matching."""
        associations = {
            'linked_goals': [],
            'linked_needs': [],
            'linked_skills': [],
            'linked_senses': [],
            'associated_concepts': []
        }
        
        # Check each keyword against patterns
        for keyword in keywords:
            for category, pattern in self.keyword_patterns.items():
                # Check direct keyword matches
                if keyword in pattern['keywords']:
                    self._add_association_by_category(category, associations)
                
                # Check related terms
                if keyword in pattern['related_terms']:
                    self._add_association_by_category(category, associations)
                
                # Check partial matches
                for pattern_keyword in pattern['keywords']:
                    similarity = SequenceMatcher(None, keyword, pattern_keyword).ratio()
                    if similarity >= self.keyword_match_threshold:
                        self._add_association_by_category(category, associations)
        
        # Check text content for keyword matches
        for category, pattern in self.keyword_patterns.items():
            for keyword in pattern['keywords']:
                if keyword in text_content:
                    self._add_association_by_category(category, associations)
        
        return associations
    
    def _add_association_by_category(self, category: str, associations: Dict):
        """Add associations based on category."""
        if category in ['exercise', 'people', 'pleasure', 'production']:
            associations['linked_goals'].append(category)
        elif category in ['exploration', 'love', 'play', 'safety', 'security']:
            associations['linked_needs'].append(category)
    
    def _discover_semantic_associations(self, keywords: List[str], text_content: str) -> Dict:
        """Discover associations based on semantic similarity."""
        associations = {
            'linked_goals': [],
            'linked_needs': [],
            'linked_skills': [],
            'linked_senses': [],
            'associated_concepts': []
        }
        
        # Analyze all files for semantic similarity
        for file_type, directory in self.directories.items():
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.endswith('.json'):
                        filepath = os.path.join(directory, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                other_data = json.load(f)
                            
                            # Calculate similarity
                            similarity = self._calculate_semantic_similarity(keywords, text_content, other_data)
                            
                            if similarity >= self.similarity_threshold:
                                # Add to appropriate association list
                                if file_type == 'goals':
                                    goal_name = filename.replace('.json', '')
                                    if goal_name not in associations['linked_goals']:
                                        associations['linked_goals'].append(goal_name)
                                elif file_type == 'needs':
                                    need_name = filename.replace('.json', '')
                                    if need_name not in associations['linked_needs']:
                                        associations['linked_needs'].append(need_name)
                                elif file_type == 'skills':
                                    skill_name = filename.replace('.json', '')
                                    if skill_name not in associations['linked_skills']:
                                        associations['linked_skills'].append(skill_name)
                                elif file_type == 'senses':
                                    sense_name = filename.replace('.json', '')
                                    if sense_name not in associations['linked_senses']:
                                        associations['linked_senses'].append(sense_name)
                                elif file_type == 'concepts':
                                    concept_name = filename.replace('.json', '')
                                    if concept_name not in associations['associated_concepts']:
                                        associations['associated_concepts'].append(concept_name)
                        
                        except Exception as e:
                            self.logger.error(f"Error analyzing {filepath}: {e}")
        
        return associations
    
    def _calculate_semantic_similarity(self, keywords: List[str], text_content: str, other_data: Dict) -> float:
        """Calculate semantic similarity between two data sets."""
        # Extract keywords and text from other data
        other_keywords = self._extract_keywords(other_data)
        other_text = self._extract_text_content(other_data)
        
        # Calculate keyword similarity
        keyword_similarity = 0.0
        if keywords and other_keywords:
            common_keywords = set(keywords) & set(other_keywords)
            keyword_similarity = len(common_keywords) / max(len(keywords), len(other_keywords))
        
        # Calculate text similarity
        text_similarity = 0.0
        if text_content and other_text:
            text_similarity = SequenceMatcher(None, text_content, other_text).ratio()
        
        # Combined similarity score
        combined_similarity = (keyword_similarity * 0.7) + (text_similarity * 0.3)
        
        return combined_similarity
    
    def _discover_conceptnet_associations(self, keywords: List[str]) -> Dict:
        """Discover associations using ConceptNet."""
        associations = {
            'linked_goals': [],
            'linked_needs': [],
            'linked_skills': [],
            'linked_senses': [],
            'associated_concepts': []
        }
        
        if not self.conceptnet_client:
            return associations
        
        # Query ConceptNet for each keyword
        for keyword in keywords[:5]:  # Limit to first 5 keywords to avoid API overload
            try:
                conceptnet_data = self.conceptnet_client.query_concept(keyword, limit=5)
                
                if conceptnet_data.get('has_data', False):
                    # Extract related concepts from ConceptNet
                    edges = conceptnet_data.get('edges', [])
                    for edge in edges:
                        target = edge.get('target', '')
                        if target:
                            # Check if target matches any of our categories
                            target_lower = target.lower()
                            
                            # Check goals
                            for goal in ['exercise', 'people', 'pleasure', 'production']:
                                if goal in target_lower and goal not in associations['linked_goals']:
                                    associations['linked_goals'].append(goal)
                            
                            # Check needs
                            for need in ['exploration', 'love', 'play', 'safety', 'security']:
                                if need in target_lower and need not in associations['linked_needs']:
                                    associations['linked_needs'].append(need)
                            
                            # Add to concepts
                            if target not in associations['associated_concepts']:
                                associations['associated_concepts'].append(target)
                
                # Rate limiting
                import time
                time.sleep(0.1)
            
            except Exception as e:
                self.logger.error(f"Error querying ConceptNet for {keyword}: {e}")
        
        return associations
    
    def update_file_associations(self, filepath: str):
        """Update associations for a specific file."""
        self.logger.info(f"Updating associations for {filepath}")
        
        # Discover new associations
        new_associations = self.discover_associations_for_file(filepath)
        
        # Update the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update associations
            updated = False
            for field, values in new_associations.items():
                if field in data:
                    # Add new associations
                    for value in values:
                        if value not in data[field]:
                            data[field].append(value)
                            updated = True
                else:
                    # Create new field
                    data[field] = values
                    updated = True
            
            # Save if updated
            if updated:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                self.logger.info(f"Updated associations for {filepath}")
                
                # Update cross-references
                self._update_cross_references(filepath, new_associations)
            
        except Exception as e:
            self.logger.error(f"Error updating associations for {filepath}: {e}")
    
    def _update_cross_references(self, source_filepath: str, associations: Dict):
        """Update cross-references in other files."""
        source_name = os.path.basename(source_filepath).replace('.json', '')
        source_type = self._get_file_type(source_filepath)
        
        # Update cross-references for each association
        for field, values in associations.items():
            for value in values:
                target_filepath = self._find_target_file(value, field)
                if target_filepath and target_filepath != source_filepath:
                    self._add_cross_reference(target_filepath, source_name, source_type)
    
    def _get_file_type(self, filepath: str) -> str:
        """Get the file type based on directory."""
        for file_type, directory in self.directories.items():
            if directory in filepath:
                return file_type
        return 'unknown'
    
    def _find_target_file(self, target_name: str, field_type: str) -> Optional[str]:
        """Find the target file for a given name and field type."""
        # Map field types to directories
        field_to_dir = {
            'linked_goals': 'goals',
            'linked_needs': 'needs',
            'linked_skills': 'skills',
            'linked_senses': 'senses',
            'associated_concepts': 'concepts'
        }
        
        if field_type in field_to_dir:
            directory = field_to_dir[field_type]
            filepath = os.path.join(directory, f"{target_name}.json")
            if os.path.exists(filepath):
                return filepath
        
        return None
    
    def _add_cross_reference(self, target_filepath: str, source_name: str, source_type: str):
        """Add a cross-reference to the target file."""
        try:
            with open(target_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine the appropriate field for cross-reference
            cross_ref_field = None
            if source_type == 'goals':
                cross_ref_field = 'linked_goals'
            elif source_type == 'needs':
                cross_ref_field = 'linked_needs'
            elif source_type == 'skills':
                cross_ref_field = 'linked_skills'
            elif source_type == 'senses':
                cross_ref_field = 'linked_senses'
            elif source_type == 'concepts':
                cross_ref_field = 'associated_concepts'
            
            if cross_ref_field:
                if cross_ref_field not in data:
                    data[cross_ref_field] = []
                
                if source_name not in data[cross_ref_field]:
                    data[cross_ref_field].append(source_name)
                    
                    with open(target_filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Added cross-reference: {source_name} -> {target_filepath}")
        
        except Exception as e:
            self.logger.error(f"Error adding cross-reference to {target_filepath}: {e}")
    
    def run_complete_discovery(self):
        """Run complete association discovery on all files."""
        self.logger.info("Starting complete association discovery...")
        
        total_files = 0
        updated_files = 0
        
        for file_type, directory in self.directories.items():
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.endswith('.json'):
                        filepath = os.path.join(directory, filename)
                        total_files += 1
                        
                        try:
                            # Update associations for this file
                            self.update_file_associations(filepath)
                            updated_files += 1
                        
                        except Exception as e:
                            self.logger.error(f"Error processing {filepath}: {e}")
        
        self.logger.info(f"Complete discovery finished: {updated_files}/{total_files} files updated")
        
        return {
            'total_files': total_files,
            'updated_files': updated_files,
            'timestamp': datetime.now().isoformat()
        }
    
    def monitor_and_update(self, watch_directories: List[str] = None):
        """Monitor directories for changes and update associations automatically."""
        if watch_directories is None:
            watch_directories = list(self.directories.values())
        
        self.logger.info(f"Starting monitoring for directories: {watch_directories}")
        
        # This would implement file system monitoring
        # For now, we'll provide a framework
        pass

def main():
    """Main function to run the automated association discovery."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create and run the system
    discovery = AutomatedAssociationDiscovery()
    
    print("🔍 Automated Association Discovery System for CARL")
    print("=" * 60)
    
    # Run complete discovery
    result = discovery.run_complete_discovery()
    
    print(f"\n📊 Discovery Results:")
    print(f"   Total files processed: {result['total_files']}")
    print(f"   Files updated: {result['updated_files']}")
    print(f"   Timestamp: {result['timestamp']}")
    
    print("\n✅ Automated association discovery complete!")

if __name__ == "__main__":
    main()
