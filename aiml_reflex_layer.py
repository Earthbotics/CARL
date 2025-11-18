#!/usr/bin/env python3
"""
AIML Reflex Layer for CARL's Cognitive Pipeline

This module implements a fast-response cache system using AIML (Artificial Intelligence Markup Language)
that acts as a "reflex brainstem" for immediate responses before full cognitive processing.

The system integrates with CARL's perception → judgment → memory → action pipeline,
providing instant responses for common patterns while still allowing full processing
for novel inputs.
"""

import os
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
import random

class AIMLReflexEngine:
    """
    AIML-based reflex engine that provides fast responses for common patterns.
    
    This engine acts as a "reflex brainstem" that can provide immediate responses
    for known patterns while allowing novel inputs to pass through to the full
    cognitive pipeline.
    """
    
    def __init__(self, aiml_dir: str = "aiml", config: Optional[Dict] = None):
        """
        Initialize the AIML reflex engine.
        
        Args:
            aiml_dir: Directory containing AIML files
            config: Configuration dictionary with AIML settings
        """
        self.aiml_dir = aiml_dir
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure AIML directory exists
        os.makedirs(aiml_dir, exist_ok=True)
        
        # Initialize pattern storage
        self.static_patterns = {}  # Pre-loaded patterns from files
        self.dynamic_patterns = {}  # Runtime-added patterns
        self.pattern_frequencies = {}  # Track pattern usage
        
        # Load AIML files
        self._load_aiml_files()
        
        # Initialize dynamic patterns file
        self.dynamic_file = os.path.join(aiml_dir, "dynamic.aiml")
        self._ensure_dynamic_file()
        
        # Load dynamic patterns
        self._load_dynamic_patterns()
        
        self.logger.info(f"AIML Reflex Engine initialized with {len(self.static_patterns)} static patterns")
    
    def _load_aiml_files(self):
        """Load AIML files from the specified directory."""
        try:
            if not os.path.exists(self.aiml_dir):
                return
            
            for filename in os.listdir(self.aiml_dir):
                if filename.endswith('.aiml') and filename != 'dynamic.aiml':
                    filepath = os.path.join(self.aiml_dir, filename)
                    self._load_aiml_file(filepath)
                    
        except Exception as e:
            self.logger.error(f"Error loading AIML files: {e}")
    
    def _load_aiml_file(self, filepath: str):
        """Load a single AIML file with enhanced support for topics and random responses."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Load topics first
            topics = {}
            for topic in root.findall('topic'):
                topic_name = topic.get('name', 'default')
                topics[topic_name] = []
                
                for category in topic.findall('category'):
                    pattern_elem = category.find('pattern')
                    template_elem = category.find('template')
                    
                    if pattern_elem is not None and template_elem is not None:
                        pattern = pattern_elem.text.strip().upper()
                        template = self._process_template(template_elem)
                        
                        topics[topic_name].append({
                            'pattern': pattern,
                            'template': template,
                            'source': 'static',
                            'file': os.path.basename(filepath),
                            'topic': topic_name,
                            'created': datetime.now().isoformat(),
                            'usage_count': 0
                        })
            
            # Load non-topic categories
            # 🔧 FIX: Use a different approach to avoid getparent() issue
            # First collect all categories that are NOT inside topics
            non_topic_categories = []
            for category in root.findall('category'):
                # Check if this category is inside a topic by looking at the tree structure
                is_in_topic = False
                for topic in root.findall('topic'):
                    if category in topic.findall('category'):
                        is_in_topic = True
                        break
                
                if not is_in_topic:
                    non_topic_categories.append(category)
            
            # Process non-topic categories
            for category in non_topic_categories:
                    
                pattern_elem = category.find('pattern')
                template_elem = category.find('template')
                
                if pattern_elem is not None and template_elem is not None:
                    pattern = pattern_elem.text.strip().upper()
                    template = self._process_template(template_elem)
                    
                    # Store pattern with metadata
                    self.static_patterns[pattern] = {
                        'template': template,
                        'source': 'static',
                        'file': os.path.basename(filepath),
                        'topic': 'default',
                        'created': datetime.now().isoformat(),
                        'usage_count': 0
                    }
            
            # Store topics
            if topics:
                self.topics = getattr(self, 'topics', {})
                self.topics.update(topics)
                    
        except Exception as e:
            self.logger.error(f"Error loading AIML file {filepath}: {e}")
    
    def _process_template(self, template_elem):
        """Process template element to handle random responses and other tags."""
        try:
            # Check for random responses
            random_elem = template_elem.find('random')
            if random_elem is not None:
                # Extract random options
                options = []
                for li in random_elem.findall('li'):
                    if li.text:
                        options.append(li.text.strip())
                
                if options:
                    # Return a special format for random selection
                    return f"RANDOM:{'|'.join(options)}"
            
            # Check for other special tags
            if template_elem.text:
                return template_elem.text.strip()
            
            # Handle mixed content
            return ''.join(template_elem.itertext()).strip()
            
        except Exception as e:
            self.logger.error(f"Error processing template: {e}")
            return template_elem.text.strip() if template_elem.text else ""
    
    def _ensure_dynamic_file(self):
        """Ensure dynamic.aiml file exists with proper structure."""
        if not os.path.exists(self.dynamic_file):
            # Create basic dynamic AIML file
            aiml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<aiml version="2.0">
    <!-- Dynamic patterns added at runtime -->
</aiml>'''
            
            with open(self.dynamic_file, 'w', encoding='utf-8') as f:
                f.write(aiml_content)
            
            self.logger.info(f"Created dynamic AIML file: {self.dynamic_file}")
    
    def _load_dynamic_patterns(self):
        """Load dynamic patterns from the dynamic.aiml file."""
        try:
            if not os.path.exists(self.dynamic_file):
                return
            
            tree = ET.parse(self.dynamic_file)
            root = tree.getroot()
            
            for category in root.findall('category'):
                pattern_elem = category.find('pattern')
                template_elem = category.find('template')
                
                if pattern_elem is not None and template_elem is not None:
                    pattern = pattern_elem.text.strip().upper()
                    template = template_elem.text.strip()
                    
                    # Store dynamic pattern
                    self.dynamic_patterns[pattern] = {
                        'template': template,
                        'source': 'dynamic',
                        'file': 'dynamic.aiml',
                        'created': datetime.now().isoformat(),
                        'usage_count': 0
                    }
                    
        except Exception as e:
            self.logger.error(f"Error loading dynamic patterns: {e}")
    
    def get_reflex_response(self, user_input: str, current_topic: str = None) -> Optional[str]:
        """
        Get a reflex response for the given input with topic support.
        
        Args:
            user_input: The user's input text
            current_topic: Current conversation topic for context
            
        Returns:
            Response string if pattern matches, None otherwise
        """
        try:
            # Normalize input for pattern matching
            normalized_input = self._normalize_input(user_input)
            
            # Check topic-specific patterns first if topic is provided
            if current_topic and hasattr(self, 'topics') and current_topic in self.topics:
                topic_patterns = {item['pattern']: item for item in self.topics[current_topic]}
                response = self._match_patterns(normalized_input, topic_patterns)
                if response:
                    self._update_pattern_usage(response['pattern'])
                    processed_response = self._process_response(response['template'])
                    self.logger.info(f"🎯 Topic reflex hit: '{user_input}' -> '{processed_response}' (topic: {current_topic}, pattern: {response['pattern']})")
                    return processed_response
            
            # Check static patterns
            response = self._match_patterns(normalized_input, self.static_patterns)
            if response:
                self._update_pattern_usage(response['pattern'])
                processed_response = self._process_response(response['template'])
                self.logger.info(f"🎯 Static reflex hit: '{user_input}' -> '{processed_response}' (pattern: {response['pattern']})")
                return processed_response
            
            # Check dynamic patterns
            response = self._match_patterns(normalized_input, self.dynamic_patterns)
            if response:
                self._update_pattern_usage(response['pattern'])
                processed_response = self._process_response(response['template'])
                self.logger.info(f"🔄 Dynamic reflex hit: '{user_input}' -> '{processed_response}' (pattern: {response['pattern']})")
                return processed_response
            
            self.logger.debug(f"🔍 No reflex match found for: '{user_input}'")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting reflex response: {e}")
            return None
    
    def _process_response(self, template: str) -> str:
        """Process response template to handle random selections and other features."""
        try:
            # Handle random responses
            if template.startswith("RANDOM:"):
                options = template[7:].split("|")  # Remove "RANDOM:" prefix
                if options:
                    return random.choice(options)
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error processing response: {e}")
            return template
    
    def _normalize_input(self, user_input: str) -> str:
        """Normalize input for pattern matching."""
        # Convert to uppercase and remove extra whitespace
        normalized = user_input.upper().strip()
        
        # Remove punctuation for better matching
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _match_patterns(self, normalized_input: str, patterns: Dict) -> Optional[Dict]:
        """Match input against patterns with wildcard support."""
        # Direct match first
        if normalized_input in patterns:
            return {
                'pattern': normalized_input,
                'template': patterns[normalized_input]['template'],
                'match_type': 'exact'
            }
        
        # Wildcard matching
        for pattern, data in patterns.items():
            if self._matches_wildcard_pattern(normalized_input, pattern):
                return {
                    'pattern': pattern,
                    'template': data['template'],
                    'match_type': 'wildcard'
                }
        
        return None
    
    def _matches_wildcard_pattern(self, input_text: str, pattern: str) -> bool:
        """Check if input matches a wildcard pattern."""
        # Convert AIML wildcards to regex
        # * matches any sequence of words
        # _ matches any single word
        regex_pattern = pattern.replace('*', '.*').replace('_', r'\w+')
        
        try:
            return bool(re.match(f'^{regex_pattern}$', input_text))
        except:
            return False
    
    def _update_pattern_usage(self, pattern: str):
        """Update usage statistics for a pattern."""
        if pattern in self.pattern_frequencies:
            self.pattern_frequencies[pattern] += 1
        else:
            self.pattern_frequencies[pattern] = 1
    
    def add_dynamic_pattern(self, input_text: str, response_text: str, source: str = "user") -> bool:
        """
        Add a new dynamic pattern to the reflex system.
        
        Args:
            input_text: The input pattern to match
            response_text: The response to return
            source: Source of the pattern ("concept", "user", "openai")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Normalize input for storage
            normalized_input = self._normalize_input(input_text)
            
            # Create pattern data
            pattern_data = {
                'template': response_text,
                'source': source,
                'file': 'dynamic.aiml',
                'created': datetime.now().isoformat(),
                'usage_count': 0
            }
            
            # Add to dynamic patterns
            self.dynamic_patterns[normalized_input] = pattern_data
            
            # Add to AIML file
            self._add_pattern_to_aiml_file(normalized_input, response_text)
            
            self.logger.info(f"Added dynamic pattern: '{normalized_input}' -> '{response_text}' (source: {source})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding dynamic pattern: {e}")
            return False
    
    def _add_pattern_to_aiml_file(self, pattern: str, template: str):
        """Add a pattern to the dynamic AIML file."""
        try:
            # Load existing file
            if os.path.exists(self.dynamic_file):
                tree = ET.parse(self.dynamic_file)
                root = tree.getroot()
            else:
                # Create new AIML structure
                root = ET.Element('aiml')
                root.set('version', '2.0')
            
            # Create new category
            category = ET.SubElement(root, 'category')
            
            pattern_elem = ET.SubElement(category, 'pattern')
            pattern_elem.text = pattern
            
            template_elem = ET.SubElement(category, 'template')
            template_elem.text = template
            
            # Save updated file
            tree = ET.ElementTree(root)
            tree.write(self.dynamic_file, encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            self.logger.error(f"Error adding pattern to AIML file: {e}")
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about pattern usage."""
        total_patterns = len(self.static_patterns) + len(self.dynamic_patterns)
        total_usage = sum(self.pattern_frequencies.values())
        
        return {
            'total_patterns': total_patterns,
            'static_patterns': len(self.static_patterns),
            'dynamic_patterns': len(self.dynamic_patterns),
            'total_usage': total_usage,
            'most_used_patterns': sorted(
                self.pattern_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'pattern_sources': {
                'static': len([p for p in self.static_patterns.values() if p['source'] == 'static']),
                'dynamic': len([p for p in self.dynamic_patterns.values() if p['source'] == 'dynamic']),
                'concept': len([p for p in self.dynamic_patterns.values() if p['source'] == 'concept']),
                'user': len([p for p in self.dynamic_patterns.values() if p['source'] == 'user']),
                'openai': len([p for p in self.dynamic_patterns.values() if p['source'] == 'openai'])
            }
        }
    
    def reload_dynamic_patterns(self):
        """Reload dynamic patterns from file (hot-reload support)."""
        try:
            self.dynamic_patterns.clear()
            self._load_dynamic_patterns()
            self.logger.info("Dynamic patterns reloaded successfully")
        except Exception as e:
            self.logger.error(f"Error reloading dynamic patterns: {e}")
    
    def create_aiml_pattern(self, input_text: str, response_text: str) -> str:
        """
        Create AIML XML pattern for a given input/response pair.
        
        Args:
            input_text: The input pattern
            response_text: The response template
            
        Returns:
            AIML XML string
        """
        # Normalize input for AIML
        normalized_input = self._normalize_input(input_text)
        
        # Create AIML category
        category = ET.Element('category')
        
        pattern_elem = ET.SubElement(category, 'pattern')
        pattern_elem.text = normalized_input
        
        template_elem = ET.SubElement(category, 'template')
        template_elem.text = response_text
        
        # Convert to string
        return ET.tostring(category, encoding='unicode')
    
    def export_patterns(self, filepath: str) -> bool:
        """Export all patterns to a file."""
        try:
            all_patterns = {**self.static_patterns, **self.dynamic_patterns}
            
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_patterns': len(all_patterns),
                'patterns': all_patterns,
                'statistics': self.get_pattern_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Patterns exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting patterns: {e}")
            return False
    
    def import_patterns(self, filepath: str) -> bool:
        """Import patterns from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for pattern, data in import_data.get('patterns', {}).items():
                if data.get('source') == 'dynamic':
                    # Add as dynamic pattern
                    self.dynamic_patterns[pattern] = data
                    self._add_pattern_to_aiml_file(pattern, data['template'])
                    imported_count += 1
            
            self.logger.info(f"Imported {imported_count} patterns from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing patterns: {e}")
            return False


class AIMLReflexIntegration:
    """
    Integration layer that connects AIML reflex engine with CARL's cognitive pipeline.
    """
    
    def __init__(self, aiml_engine: AIMLReflexEngine, memory_system=None, concept_system=None):
        """
        Initialize the integration layer.
        
        Args:
            aiml_engine: The AIML reflex engine
            memory_system: CARL's memory system
            concept_system: CARL's concept system
        """
        self.aiml_engine = aiml_engine
        self.memory_system = memory_system
        self.concept_system = concept_system
        self.logger = logging.getLogger(__name__)
        
        # Track reflex responses for learning
        self.reflex_log = []
        self.learning_threshold = 3  # Learn after 3 similar responses
        
        # 🔧 ENHANCEMENT: Initialize memory-based learning
        self.memory_learning_enabled = True
        self.concept_learning_enabled = True
        
        # Load patterns from memory and concepts
        if self.memory_learning_enabled:
            self._load_patterns_from_memory()
        
        if self.concept_learning_enabled:
            self._load_patterns_from_concepts()
    
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input through the reflex system.
        
        Args:
            user_input: The user's input
            context: Additional context information
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Check for reflex response
            reflex_response = self.aiml_engine.get_reflex_response(user_input)
            
            if reflex_response:
                # Log reflex hit
                self._log_reflex_hit(user_input, reflex_response, context)
                
                # Update memory system if available
                if self.memory_system:
                    self._update_memory_with_reflex(user_input, reflex_response)
                
                return {
                    'response': reflex_response,
                    'source': 'reflex',
                    'confidence': 0.9,  # High confidence for reflex responses
                    'processing_time': 0.01,  # Very fast
                    'pattern_matched': True
                }
            
            return {
                'response': None,
                'source': 'none',
                'confidence': 0.0,
                'processing_time': 0.0,
                'pattern_matched': False
            }
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                'response': None,
                'source': 'error',
                'confidence': 0.0,
                'processing_time': 0.0,
                'pattern_matched': False,
                'error': str(e)
            }
    
    def _log_reflex_hit(self, user_input: str, response: str, context: Dict[str, Any] = None):
        """Log a reflex hit for learning purposes."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'response': response,
            'context': context or {},
            'type': 'reflex_hit'
        }
        
        self.reflex_log.append(log_entry)
        
        # Keep only recent entries
        if len(self.reflex_log) > 1000:
            self.reflex_log = self.reflex_log[-500:]
    
    def _update_memory_with_reflex(self, user_input: str, response: str):
        """Update memory system with reflex response."""
        try:
            if hasattr(self.memory_system, 'store_memory'):
                # Create memory context
                from memory_system import MemoryContext
                context = MemoryContext(
                    current_emotion="neutral",
                    emotional_intensity=0.5,
                    cognitive_load=0.1,  # Low cognitive load for reflexes
                    attention_focus="reflex",
                    environmental_context={},
                    personality_state={}
                )
                
                # Store as working memory
                memory_id = self.memory_system.store_memory(
                    content=f"Reflex response: {user_input} -> {response}",
                    memory_type="working",
                    context=context,
                    importance=0.3,  # Moderate importance
                    source="reflex_system"
                )
                
                self.logger.debug(f"Stored reflex memory: {memory_id}")
                
        except Exception as e:
            self.logger.error(f"Error updating memory with reflex: {e}")
    
    def learn_from_openai_response(self, user_input: str, openai_response: str) -> bool:
        """
        Learn a new reflex pattern from OpenAI response.
        
        Args:
            user_input: The original input
            openai_response: The OpenAI-generated response
            
        Returns:
            True if pattern was learned, False otherwise
        """
        try:
            # Check if response has random action tag
            if "[[random_action]]" in openai_response:
                # Remove the tag for cleaner response
                clean_response = openai_response.replace("[[random_action]]", "").strip()
                
                # Add as dynamic pattern
                success = self.aiml_engine.add_dynamic_pattern(
                    input_text=user_input,
                    response_text=clean_response,
                    source="openai"
                )
                
                if success:
                    self.logger.info(f"Learned new reflex from OpenAI: '{user_input}' -> '{clean_response}'")
                    
                    # Update concept system if available
                    if self.concept_system:
                        self._update_concept_system(user_input, clean_response)
                
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error learning from OpenAI response: {e}")
            return False
    
    def _update_concept_system(self, user_input: str, response: str):
        """Update concept system with new reflex pattern."""
        try:
            if hasattr(self.concept_system, 'learn_new_reflex'):
                self.concept_system.learn_new_reflex(user_input, response)
            elif hasattr(self.concept_system, 'create_or_update_concept'):
                # Extract concepts from input and response
                concepts = self._extract_concepts(user_input + " " + response)
                for concept in concepts:
                    self.concept_system.create_or_update_concept(concept, "reflex_pattern")
                    
        except Exception as e:
            self.logger.error(f"Error updating concept system: {e}")
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract potential concepts from text."""
        # Simple concept extraction - could be enhanced
        words = text.lower().split()
        concepts = []
        
        # Look for meaningful words (longer than 3 characters)
        for word in words:
            if len(word) > 3 and word.isalpha():
                concepts.append(word)
        
        return concepts[:5]  # Limit to 5 concepts
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learning system."""
        return {
            'total_reflex_hits': len(self.reflex_log),
            'recent_hits': len([log for log in self.reflex_log if 
                               datetime.fromisoformat(log['timestamp']) > 
                               datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)]),
            'pattern_statistics': self.aiml_engine.get_pattern_statistics(),
            'learning_threshold': self.learning_threshold
        }
    
    def _load_patterns_from_memory(self):
        """Load AIML patterns from CARL's memory system."""
        try:
            if not self.memory_system:
                return
            
            self.logger.info("🧠 Loading AIML patterns from memory system...")
            
            # Get recent memories that might contain Q&A patterns
            if hasattr(self.memory_system, 'get_recent_memories'):
                recent_memories = self.memory_system.get_recent_memories(limit=100)
                
                for memory in recent_memories:
                    if memory.get('type') == 'conversation':
                        # Extract potential Q&A patterns
                        self._extract_qa_patterns_from_memory(memory)
            
            # Get episodic memories
            if hasattr(self.memory_system, 'episodic_memory_cache'):
                for memory_id, memory_data in self.memory_system.episodic_memory_cache.items():
                    if memory_data.get('type') == 'conversation':
                        self._extract_qa_patterns_from_memory(memory_data)
            
            self.logger.info("✅ Memory-based pattern loading completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading patterns from memory: {e}")
    
    def _load_patterns_from_concepts(self):
        """Load AIML patterns from CARL's concept system."""
        try:
            if not self.concept_system:
                return
            
            self.logger.info("🔗 Loading AIML patterns from concept system...")
            
            # Get concept files
            concept_dir = "concepts"
            if os.path.exists(concept_dir):
                for filename in os.listdir(concept_dir):
                    if filename.endswith('.json'):
                        concept_file = os.path.join(concept_dir, filename)
                        self._extract_patterns_from_concept_file(concept_file)
            
            self.logger.info("✅ Concept-based pattern loading completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading patterns from concepts: {e}")
    
    def _extract_qa_patterns_from_memory(self, memory_data: Dict):
        """Extract Q&A patterns from memory data."""
        try:
            content = memory_data.get('content', '')
            if not content:
                return
            
            # Look for question-answer patterns
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '?' in line and i + 1 < len(lines):
                    question = line.strip()
                    answer = lines[i + 1].strip()
                    
                    if question and answer:
                        # Add as dynamic pattern
                        self.aiml_engine.add_dynamic_pattern(
                            input_text=question,
                            response_text=answer,
                            source="memory"
                        )
                        
        except Exception as e:
            self.logger.error(f"❌ Error extracting Q&A patterns: {e}")
    
    def _extract_patterns_from_concept_file(self, concept_file: str):
        """Extract patterns from concept file."""
        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                concept_data = json.load(f)
            
            # Look for common questions and responses
            if 'common_questions' in concept_data:
                for qa_pair in concept_data['common_questions']:
                    if isinstance(qa_pair, dict) and 'question' in qa_pair and 'answer' in qa_pair:
                        self.aiml_engine.add_dynamic_pattern(
                            input_text=qa_pair['question'],
                            response_text=qa_pair['answer'],
                            source="concept"
                        )
            
            # Look for associated memories
            if 'associated_memories' in concept_data:
                for memory_ref in concept_data['associated_memories']:
                    if isinstance(memory_ref, dict) and 'content' in memory_ref:
                        self._extract_qa_patterns_from_memory(memory_ref)
                        
        except Exception as e:
            self.logger.error(f"❌ Error extracting patterns from concept file {concept_file}: {e}")
    
    def learn_from_conversation(self, user_input: str, carl_response: str):
        """Learn new patterns from successful conversations."""
        try:
            # Add successful response as pattern
            success = self.aiml_engine.add_dynamic_pattern(
                input_text=user_input,
                response_text=carl_response,
                source="conversation"
            )
            
            if success:
                self.logger.info(f"🎓 Learned new pattern from conversation: '{user_input}' -> '{carl_response}'")
                
                # Store in memory system
                if self.memory_system:
                    self._store_learned_pattern(user_input, carl_response)
                
                # Update concept system
                if self.concept_system:
                    self._update_concept_with_pattern(user_input, carl_response)
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error learning from conversation: {e}")
            return False
    
    def _store_learned_pattern(self, user_input: str, response: str):
        """Store learned pattern in memory system."""
        try:
            if hasattr(self.memory_system, 'store_memory'):
                memory_id = self.memory_system.store_memory(
                    content=f"Learned AIML pattern: {user_input} -> {response}",
                    memory_type="procedural",
                    importance=0.7,
                    source="aiml_learning"
                )
                self.logger.debug(f"Stored learned pattern in memory: {memory_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Error storing learned pattern: {e}")
    
    def _update_concept_with_pattern(self, user_input: str, response: str):
        """Update concept system with new pattern."""
        try:
            if hasattr(self.concept_system, 'create_or_update_concept'):
                # Extract key concepts from input
                concepts = self._extract_concepts(user_input)
                for concept in concepts:
                    self.concept_system.create_or_update_concept(
                        concept, 
                        f"AIML pattern: {user_input} -> {response}"
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Error updating concept with pattern: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    
    # Create AIML reflex engine
    aiml_engine = AIMLReflexEngine()
    
    # Test basic functionality
    print("Testing AIML Reflex Engine...")
    
    # Add a test pattern
    aiml_engine.add_dynamic_pattern("hello", "Hi there! How can I help you?", "test")
    
    # Test pattern matching
    response = aiml_engine.get_reflex_response("Hello")
    print(f"Response to 'Hello': {response}")
    
    # Test wildcard pattern
    aiml_engine.add_dynamic_pattern("what is *", "That's an interesting question about *", "test")
    response = aiml_engine.get_reflex_response("what is love")
    print(f"Response to 'what is love': {response}")
    
    # Get statistics
    stats = aiml_engine.get_pattern_statistics()
    print(f"Pattern statistics: {stats}")
